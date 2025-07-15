#!/usr/bin/env python
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ticket.settings')
django.setup()

from appticket.models import Ticket, Agence, Client
from appticket.views_agent import AgentTicketsAgenceAPIView
from rest_framework.test import APIRequestFactory
from django.urls import reverse

def test_agent_api():
    print("=== TEST DE L'API AGENT ===")
    
    # ID de l'agence utilisée dans le dashboard
    agence_id = "2c8ee4e2-ad2d-4845-b9e5-aa9b46b3c2e1"
    
    # Créer une requête de test
    factory = APIRequestFactory()
    request = factory.get(f'/api/agent/tickets-agence/{agence_id}/')
    
    # Appeler la vue
    view = AgentTicketsAgenceAPIView()
    response = view.get(request, agence_id=agence_id)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.data
        print(f"Agence: {data.get('agence', {}).get('nom_agence', 'N/A')}")
        print(f"Nombre de tickets en attente: {data.get('nombre_tickets_en_attente', 0)}")
        print(f"Nombre total de tickets: {len(data.get('tous_les_tickets', []))}")
        
        print("\nTous les tickets:")
        for ticket in data.get('tous_les_tickets', []):
            print(f"- {ticket.get('numero_ticket')} ({ticket.get('etat')})")
    else:
        print(f"Erreur: {response.data}")

if __name__ == "__main__":
    test_agent_api() 