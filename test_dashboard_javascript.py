import requests
import json

# Simulation du JavaScript du dashboard agent
API_BASE_URL = 'http://localhost:8000/api'
AGENCE_ID = '2c8ee4e2-ad2d-4845-b9e5-aa9b46b3c2e1'

def test_loadTickets():
    """Simule la fonction loadTickets du dashboard"""
    print("=== SIMULATION DE LA FONCTION loadTickets ===")
    
    try:
        # Appel à l'API exactement comme dans le JavaScript
        url = f"{API_BASE_URL}/agent/tickets-agence/{AGENCE_ID}/"
        print(f"URL appelée: {url}")
        
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Réponse reçue avec succès")
            print(f"Agence: {data.get('agence', {}).get('nom_agence', 'N/A')}")
            print(f"Nombre de tickets en attente: {data.get('nombre_tickets_en_attente', 0)}")
            
            # Simuler allTickets = data.tous_les_tickets || []
            allTickets = data.get('tous_les_tickets', [])
            print(f"Nombre total de tickets récupérés: {len(allTickets)}")
            
            if allTickets:
                print("\nPremiers tickets:")
                for i, ticket in enumerate(allTickets[:5]):
                    print(f"  {i+1}. {ticket.get('numero_ticket')} ({ticket.get('etat')})")
                
                # Simuler filterTickets()
                print("\n=== SIMULATION DE filterTickets ===")
                filteredTickets = allTickets  # Sans filtre pour l'instant
                print(f"Tickets filtrés: {len(filteredTickets)}")
                
                # Simuler displayTickets()
                print("\n=== SIMULATION DE displayTickets ===")
                if filteredTickets:
                    print("✅ Tickets à afficher dans le tableau")
                    for ticket in filteredTickets[:3]:
                        print(f"  - {ticket.get('numero_ticket')} | {ticket.get('type_reservation')} | {ticket.get('etat')}")
                else:
                    print("❌ Aucun ticket à afficher")
                
                # Simuler updateStats()
                print("\n=== SIMULATION DE updateStats ===")
                nombre_en_attente = data.get('nombre_tickets_en_attente', 0)
                print(f"Tickets en attente à afficher: {nombre_en_attente}")
                
            else:
                print("❌ Aucun ticket dans la réponse")
                
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
            print(f"Contenu: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Erreur de connexion - le serveur n'est pas démarré")
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    test_loadTickets() 