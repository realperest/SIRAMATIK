import requests
import json

FIRMA_ID = 1
URL = f"http://localhost:8000/api/sira/bekleyen/{FIRMA_ID}"

# Login önce (token için)
LOGIN_URL = "http://localhost:8000/api/auth/login"
CREDS = {
    "email": "admin@demo.com",
    "password": "admin123"
}

def test_api():
    print(f"API TEST BAŞLIYOR: {URL}")
    
    # 1. Login
    try:
        print("Login deneniyor...")
        resp = requests.post(LOGIN_URL, json=CREDS)
        if resp.status_code != 200:
            print(f"Login Başarısız: {resp.status_code} {resp.text}")
            return
            
        token = resp.json()["access_token"]
        print("Login Başarılı. Token alındı.")
        
        # 2. Bekleyenleri çek
        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.get(URL, headers=headers)
        
        if resp.status_code == 200:
            data = resp.json()
            print(f"\n--- API YANITI ({len(data)} Kayıt) ---")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(f"İSTEK BAŞARISIZ: {resp.status_code}")
            print(resp.text)
            
    except Exception as e:
        print(f"HATA: {e}")

if __name__ == "__main__":
    test_api()
