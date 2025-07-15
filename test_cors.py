import requests

def test_cors():
    print("=== TEST CORS ===")
    
    # Test avec localhost
    url_localhost = "http://localhost:8000/api/agent/tickets-agence/2c8ee4e2-ad2d-4845-b9e5-aa9b46b3c2e1/"
    headers_localhost = {
        'Origin': 'http://127.0.0.1:8000',
        'Accept': 'application/json'
    }
    
    try:
        response = requests.get(url_localhost, headers=headers_localhost)
        print(f"Test localhost -> localhost")
        print(f"Status: {response.status_code}")
        print(f"CORS Headers: {dict(response.headers)}")
        
        if 'Access-Control-Allow-Origin' in response.headers:
            print("✅ CORS headers présents")
        else:
            print("❌ CORS headers manquants")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    print("\n=== INSTRUCTIONS ===")
    print("1. Accédez au dashboard via: http://127.0.0.1:8000/api/agent/dashboard/")
    print("2. Ouvrez la console du navigateur (F12)")
    print("3. Vérifiez s'il y a encore des erreurs CORS")
    print("4. Les tickets devraient maintenant s'afficher dans le tableau")

if __name__ == "__main__":
    test_cors() 