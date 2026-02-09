
import os
import shutil

app_js_path = r"frontend/static/app.js"
ws_impl_path = r"frontend/static/ws_impl.js"

print(f"Adding WebSocket implementation to {app_js_path}...")

try:
    # 1. ws_impl.js oku (UTF-8)
    with open(ws_impl_path, "r", encoding="utf-8") as f:
        ws_code = f.read()

    # 2. app.js oku (Muhtemelen UTF-8 değilse Latin-1 dene)
    content = ""
    encoding_used = "utf-8"
    try:
        with open(app_js_path, "r", encoding="utf-8") as f:
            content = f.read()
    except UnicodeDecodeError:
        print("⚠️ UTF-8 okuma hatası, Latin-1 deneniyor...")
        encoding_used = "latin-1"
        with open(app_js_path, "r", encoding="latin-1") as f:
            content = f.read()

    # 3. Kontrol et ve ekle
    if "initWebSocket" not in content:
        # Dosyayı aynı encoding ile açıp ('a' modunda) ekleyelim
        with open(app_js_path, "a", encoding=encoding_used) as f:
            f.write("\n" + ws_code)
        print(f"✅ Başarılı! app.js güncellendi ({encoding_used}).")
    else:
        print("ℹ️ WebSocket kodu zaten mevcut.")

except Exception as e:
    print(f"❌ KRİTİK HATA: {e}")
