#!/usr/bin/env python
"""
Script pour supprimer seulement les tickets et notifications
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ticket.settings')
django.setup()

from appticket.models import Ticket, Notification

def clear_tickets_only():
    """Supprime seulement les tickets et notifications"""
    print("🗑️  Suppression des tickets et notifications...")
    
    # Supprimer les notifications d'abord (car elles référencent les tickets)
    notifications_count = Notification.objects.count()
    Notification.objects.all().delete()
    print(f"✅ Notifications: {notifications_count} supprimées")
    
    # Supprimer les tickets
    tickets_count = Ticket.objects.count()
    Ticket.objects.all().delete()
    print(f"✅ Tickets: {tickets_count} supprimés")
    
    print(f"\n🎉 Suppression terminée!")
    print(f"📊 État de la base de données:")
    print(f"   Tickets: {Ticket.objects.count()}")
    print(f"   Notifications: {Notification.objects.count()}")
    print(f"   Agences: {django.apps.apps.get_model('appticket', 'Agence').objects.count()}")
    print(f"   Agents: {django.apps.apps.get_model('appticket', 'Agent').objects.count()}")
    print(f"   Clients: {django.apps.apps.get_model('appticket', 'Client').objects.count()}")

if __name__ == "__main__":
    print("=" * 50)
    print("🧹 SUPPRESSION DES TICKETS SEULEMENT")
    print("=" * 50)
    
    # Demander confirmation
    response = input("\n⚠️  Cette action supprimera TOUS les tickets et notifications!\nÊtes-vous sûr? (oui/non): ")
    
    if response.lower() in ['oui', 'yes', 'o', 'y']:
        clear_tickets_only()
    else:
        print("❌ Opération annulée") 