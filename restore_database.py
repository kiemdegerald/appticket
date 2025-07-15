#!/usr/bin/env python
"""
Script pour restaurer les données de base nécessaires au système
"""
import os
import sys
import django
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ticket.settings')
django.setup()

from appticket.models import Ticket, Client, Agent, Administrateur, Agence, Notification, ConfigurationDistribution

def create_agences():
    """Créer les agences de base"""
    print("🏢 Création des agences...")
    
    agences_data = [
        {
            'nom_agence': 'ONEA Centre',
            'latitude': Decimal('12.3714'),
            'longitude': Decimal('-1.5197'),
            'adresse': 'Ouagadougou, Burkina Faso',
            'is_active': True
        },
        {
            'nom_agence': 'ONEA Bobo-Dioulasso',
            'latitude': Decimal('11.1781'),
            'longitude': Decimal('-4.2893'),
            'adresse': 'Bobo-Dioulasso, Burkina Faso',
            'is_active': True
        }
    ]
    
    created_agences = []
    for data in agences_data:
        agence, created = Agence.objects.get_or_create(
            nom_agence=data['nom_agence'],
            defaults=data
        )
        if created:
            print(f"✅ Agence créée: {agence.nom_agence}")
        else:
            print(f"ℹ️  Agence existante: {agence.nom_agence}")
        created_agences.append(agence)
    
    return created_agences

def create_agents():
    """Créer les agents de base"""
    print("\n👨‍💼 Création des agents...")
    
    agents_data = [
        {
            'nom': 'Konaté',
            'prenom': 'Fatou',
            'is_active': True
        },
        {
            'nom': 'Ouédraogo',
            'prenom': 'Moussa',
            'is_active': True
        }
    ]
    
    created_agents = []
    for data in agents_data:
        agent, created = Agent.objects.get_or_create(
            nom=data['nom'],
            prenom=data['prenom'],
            defaults=data
        )
        if created:
            print(f"✅ Agent créé: {agent.prenom} {agent.nom}")
        else:
            print(f"ℹ️  Agent existant: {agent.prenom} {agent.nom}")
        created_agents.append(agent)
    
    return created_agents

def create_clients():
    """Créer quelques clients de test"""
    print("\n👥 Création des clients...")
    
    clients_data = [
        {'latitude': Decimal('12.3714'), 'longitude': Decimal('-1.5197')},
        {'latitude': Decimal('12.3720'), 'longitude': Decimal('-1.5200')},
        {'latitude': Decimal('12.3700'), 'longitude': Decimal('-1.5180')},
        {'latitude': Decimal('11.1781'), 'longitude': Decimal('-4.2893')},
        {'latitude': Decimal('11.1790'), 'longitude': Decimal('-4.2900')},
    ]
    
    created_clients = []
    for i, data in enumerate(clients_data):
        client, created = Client.objects.get_or_create(
            latitude=data['latitude'],
            longitude=data['longitude'],
            defaults=data
        )
        if created:
            print(f"✅ Client créé: {client.id}")
        else:
            print(f"ℹ️  Client existant: {client.id}")
        created_clients.append(client)
    
    return created_clients

def create_tickets(agences, clients):
    """Créer quelques tickets de test"""
    print("\n🎫 Création des tickets...")
    
    ticket_types = ['RECLAMATION', 'DEMANDE_INFO', 'DEMANDE_BRANCHEMENT', 'FACTURE', 'PANNE', 'AUTRE']
    
    created_tickets = []
    
    # Créer des tickets pour chaque agence
    for agence in agences:
        for i, client in enumerate(clients[:3]):  # Utiliser les 3 premiers clients
            ticket_type = ticket_types[i % len(ticket_types)]
            
            # Créer le ticket
            ticket = Ticket.objects.create(
                type_reservation=ticket_type,
                etat='en_attente',
                client=client,
                agence=agence,
                date_emission=timezone.now() - timedelta(minutes=i*5)  # Différentes heures
            )
            
            print(f"✅ Ticket créé: {ticket.numero_ticket} ({ticket.type_reservation})")
            created_tickets.append(ticket)
    
    return created_tickets

def create_notifications(tickets):
    """Créer quelques notifications de test"""
    print("\n🔔 Création des notifications...")
    
    notification_types = ['appel', 'information', 'rappel']
    
    for ticket in tickets:
        # Créer 1-2 notifications par ticket
        for i in range(2):
            notification = Notification.objects.create(
                message=f"Notification de test {i+1} pour le ticket {ticket.numero_ticket}",
                type_notification=notification_types[i % len(notification_types)],
                ticket=ticket,
                statut='envoye'
            )
            print(f"✅ Notification créée pour {ticket.numero_ticket}")
    
    print(f"✅ {len(tickets) * 2} notifications créées")

def restore_database():
    """Fonction principale pour restaurer la base de données"""
    print("=" * 50)
    print("🔄 RESTAURATION DE LA BASE DE DONNÉES")
    print("=" * 50)
    
    try:
        # Créer les agences
        agences = create_agences()
        
        # Créer les agents
        agents = create_agents()
        
        # Créer les clients
        clients = create_clients()
        
        # Créer les tickets
        tickets = create_tickets(agences, clients)
        
        # Créer les notifications
        create_notifications(tickets)
        
        print("\n" + "=" * 50)
        print("🎉 RESTAURATION TERMINÉE AVEC SUCCÈS!")
        print("=" * 50)
        
        # Afficher le résumé
        print(f"📊 Résumé de la restauration:")
        print(f"   🏢 Agences: {Agence.objects.count()}")
        print(f"   👨‍💼 Agents: {Agent.objects.count()}")
        print(f"   👥 Clients: {Client.objects.count()}")
        print(f"   🎫 Tickets: {Ticket.objects.count()}")
        print(f"   🔔 Notifications: {Notification.objects.count()}")
        
        # Afficher les IDs importants
        print(f"\n🔑 IDs importants:")
        for agence in agences:
            print(f"   Agence '{agence.nom_agence}': {agence.id_agence}")
        for agent in agents:
            print(f"   Agent '{agent.prenom} {agent.nom}': {agent.id}")
        
    except Exception as e:
        print(f"❌ Erreur lors de la restauration: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    restore_database() 