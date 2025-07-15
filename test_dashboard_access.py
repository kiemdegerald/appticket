import requests

# Test d'accès au dashboard agent
url = "http://localhost:8000/api/agent/dashboard/"

try:
    response = requests.get(url)
    print(f"Status Code: {response.status_code}")
    print(f"URL testée: {url}")
    
    if response.status_code == 200:
        print("✅ Dashboard accessible")
        print(f"Taille de la réponse: {len(response.text)} caractères")
        # Vérifier si le contenu contient des éléments du dashboard
        if "Dashboard Agent" in response.text:
            print("✅ Contenu du dashboard détecté")
        if "ticketsList" in response.text:
            print("✅ JavaScript du dashboard détecté")
        if "loadTickets" in response.text:
            print("✅ Fonction loadTickets détectée")
    else:
        print(f"❌ Erreur: {response.status_code}")
        print(f"Contenu: {response.text[:200]}...")
        
except requests.exceptions.ConnectionError:
    print("❌ Erreur de connexion - le serveur n'est pas démarré")
except Exception as e:
    print(f"❌ Erreur: {e}") 