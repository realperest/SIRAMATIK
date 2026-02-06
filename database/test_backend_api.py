"""
Backend API Test - Siramatik Schema
"""
import requests

BASE_URL = "http://localhost:8000"

print("🧪 Backend API Testi\n")

# 1. Health check
print("1️⃣ Health Check...")
try:
    response = requests.get(f"{BASE_URL}/health")
    print(f"   ✅ Status: {response.status_code}")
    print(f"   📊 Response: {response.json()}")
except Exception as e:
    print(f"   ❌ Hata: {e}")

# 2. Root endpoint
print("\n2️⃣ Root Endpoint...")
try:
    response = requests.get(f"{BASE_URL}/")
    print(f"   ✅ Status: {response.status_code}")
    data = response.json()
    print(f"   📊 App: {data.get('app')}")
    print(f"   📊 Version: {data.get('version')}")
    print(f"   📊 Features: {data.get('features')}")
except Exception as e:
    print(f"   ❌ Hata: {e}")

# 3. Servisler listesi (demo firma ID)
print("\n3️⃣ Servisler Listesi...")
try:
    # Demo firma ID (seed data'dan)
    firma_id = "11111111-1111-1111-1111-111111111111"
    response = requests.get(f"{BASE_URL}/api/servisler/{firma_id}")
    print(f"   ✅ Status: {response.status_code}")
    if response.status_code == 200:
        servisler = response.json()
        print(f"   📊 {len(servisler)} servis bulundu:")
        for servis in servisler:
            print(f"      - {servis.get('ad')} ({servis.get('kuyruk_sayisi')} kuyruk)")
    else:
        print(f"   ⚠️  Response: {response.text}")
except Exception as e:
    print(f"   ❌ Hata: {e}")

print("\n" + "="*60)
print("✅ TEST TAMAMLANDI!")
print("="*60)
print("\n📝 API Docs:")
print(f"   {BASE_URL}/docs")
print()
