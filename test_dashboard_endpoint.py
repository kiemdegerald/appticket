import requests
import json

# Test de l'endpoint utilisé par le dashboard agent
agence_id = "2c8ee4e2-ad2d-4845-b9e5-aa9b46b3c2e1"
url = f"http://localhost:8000/api/agent/tickets-agence/{agence_id}/"

try:
    response = requests.get(url)
    print(f"Status Code: {response.status_code}")
    print(f"URL testée: {url}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Agence: {data.get('agence', {}).get('nom_agence', 'N/A')}")
        print(f"Nombre de tickets en attente: {data.get('nombre_tickets_en_attente', 0)}")
        print(f"Nombre total de tickets: {len(data.get('tous_les_tickets', []))}")
        
        print("\nTous les tickets:")
        for ticket in data.get('tous_les_tickets', []):
            print(f"- {ticket.get('numero_ticket')} ({ticket.get('etat')})")
    else:
        print(f"Erreur: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("Erreur de connexion - le serveur n'est pas démarré")
except Exception as e:
    print(f"Erreur: {e}") 