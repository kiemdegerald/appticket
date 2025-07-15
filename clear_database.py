#!/usr/bin/env python
"""
Script pour supprimer toutes les données de la base de données
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ticket.settings')
django.setup()

from appticket.models import Ticket, Client, Agent, Administrateur, Agence, Notification, ConfigurationDistribution

def clear_all_data():
    """Supprime toutes les données de tous les modèles"""
    print("🗑️  Suppression de toutes les données de la base de données...")
    
    # Supprimer dans l'ordre pour éviter les erreurs de clés étrangères
    models_to_clear = [
        (Notification, "Notifications"),
        (Ticket, "Tickets"),
        (Client, "Clients"),
        (Agent, "Agents"),
        (Administrateur, "Administrateurs"),
        (Agence, "Agences"),
        (ConfigurationDistribution, "Configurations de distribution")
    ]
    
    total_deleted = 0
    
    for model, model_name in models_to_clear:
        try:
            count = model.objects.count()
            model.objects.all().delete()
            print(f"✅ {model_name}: {count} enregistrements supprimés")
            total_deleted += count
        except Exception as e:
            print(f"❌ Erreur lors de la suppression des {model_name}: {e}")
    
    print(f"\n🎉 Suppression terminée! Total: {total_deleted} enregistrements supprimés")
    print("📊 État de la base de données:")
    
    # Afficher le nombre d'enregistrements restants
    for model, model_name in models_to_clear:
        count = model.objects.count()
        print(f"   {model_name}: {count} enregistrements")

if __name__ == "__main__":
    print("=" * 50)
    print("🧹 SCRIPT DE SUPPRESSION DE LA BASE DE DONNÉES")
    print("=" * 50)
    
    # Demander confirmation
    response = input("\n⚠️  ATTENTION: Cette action supprimera TOUTES les données!\nÊtes-vous sûr? (oui/non): ")
    
    if response.lower() in ['oui', 'yes', 'o', 'y']:
        clear_all_data()
    else:
        print("❌ Opération annulée") 