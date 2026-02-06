
import requests
import json
import time

API_URL = "http://localhost:8000/api"
FIRMA_ID = 1

def test_api():
    print("BACKEND API TEST EDİLİYOR...")
    
    # 1. Kuyruklar Endpoint Testi
    endpoint = f"{API_URL}/kuyruklar/firma/{FIRMA_ID}"
    print(f"\n[1] GET {endpoint}")
    
    try:
        response = requests.get(endpoint)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Veri Tipi: {type(data)}")
            print(f"Kayıt Sayısı: {len(data)}")
            if len(data) > 0:
                print("Örnek Kayıt (İlk):")
                print(json.dumps(data[0], indent=2))
            else:
                print("UYARI: Boş liste döndü!")
        else:
            print(f"HATA: {response.text}")
            
    except Exception as e:
        print(f"Bağlantı Hatası: {e}")

if __name__ == "__main__":
    test_api()
