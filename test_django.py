#!/usr/bin/env python
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ticket.settings')
django.setup()

from appticket.models import Ticket, Agence, Client
from appticket.views import FileAttenteAPIView
from rest_framework.test import APIRequestFactory
from django.urls import reverse

def test_database():
    print("=== TEST DE LA BASE DE DONNÉES ===")
    
    # Compter les tickets
    total_tickets = Ticket.objects.count()
    print(f"Total tickets: {total_tickets}")
    
    # Lister les agences
    agences = Agence.objects.all()
    print(f"Agences: {agences.count()}")
    for agence in agences:
        print(f"- {agence.nom_agence} (ID: {agence.id_agence})")
    
    # Lister les tickets par agence
    for agence in agences:
        tickets = Ticket.objects.filter(agence=agence)
        print(f"\nTickets pour {agence.nom_agence}:")
        for ticket in tickets[:5]:  # Afficher les 5 premiers
            print(f"  - {ticket.numero_ticket} ({ticket.etat})")

def test_api_view():
    print("\n=== TEST DE L'API VIEW ===")
    
    # ID de l'agence utilisée dans le dashboard
    agence_id = "2c8ee4e2-ad2d-4845-b9e5-aa9b46b3c2e1"
    
    try:
        agence = Agence.objects.get(id_agence=agence_id)
        print(f"Agence trouvée: {agence.nom_agence}")
        
        # Compter les tickets pour cette agence
        tickets_agence = Ticket.objects.filter(agence=agence)
        tickets_en_attente = tickets_agence.filter(etat='en_attente')
        
        print(f"Tickets totaux pour cette agence: {tickets_agence.count()}")
        print(f"Tickets en attente: {tickets_en_attente.count()}")
        
        # Lister les tickets
        print("\nTickets de cette agence:")
        for ticket in tickets_agence[:10]:
            print(f"  - {ticket.numero_ticket} ({ticket.etat}) - Client: {ticket.client.id}")
            
    except Agence.DoesNotExist:
        print(f"Agence avec ID {agence_id} non trouvée")
        print("Agences disponibles:")
        for agence in Agence.objects.all():
            print(f"  - {agence.id_agence}: {agence.nom_agence}")

if __name__ == "__main__":
    test_database()
    test_api_view() 