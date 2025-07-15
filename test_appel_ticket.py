#!/usr/bin/env python
import os
import sys
import django
import requests
import json

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ticket.settings')
django.setup()

from appticket.models import Ticket, Agent

def test_appel_ticket():
    print("=== TEST DE L'API APPEL TICKET ===")
    
    # Récupérer un ticket en attente
    ticket = Ticket.objects.filter(etat='en_attente').first()
    if not ticket:
        print("Aucun ticket en attente disponible")
        return
    
    # Récupérer un agent actif
    agent = Agent.objects.filter(is_active=True).first()
    if not agent:
        print("Aucun agent actif disponible")
        return
    
    print(f"Ticket à appeler: {ticket.numero_ticket} (ID: {ticket.id_ticket})")
    print(f"Agent: {agent.nom} {agent.prenom} (ID: {agent.id})")
    
    # Test de l'API
    url = "http://localhost:8000/api/agent/appeler-ticket/"
    data = {
        "ticket_id": str(ticket.id_ticket),
        "agent_id": str(agent.id),
        "message_notification": "Présentez-vous au guichet"
    }
    
    try:
        response = requests.put(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Appel de ticket réussi!")
            
            # Vérifier que le ticket a été mis à jour
            ticket.refresh_from_db()
            print(f"État du ticket après appel: {ticket.etat}")
            print(f"Agent assigné: {ticket.agent.nom if ticket.agent else 'Aucun'}")
        else:
            print("❌ Échec de l'appel de ticket")
            
    except requests.exceptions.ConnectionError:
        print("Erreur de connexion - le serveur n'est pas démarré")
    except Exception as e:
        print(f"Erreur: {e}")

if __name__ == "__main__":
    test_appel_ticket() 