
import os

app_js_path = r"D:\KODLAMALAR\GITHUB\SIRAMATIK\frontend\static\app.js"
ws_impl_path = r"D:\KODLAMALAR\GITHUB\SIRAMATIK\frontend\static\ws_impl.js"

try:
    with open(ws_impl_path, "r", encoding="utf-8") as f:
        ws_code = f.read()

    # app.js'i okurken encoding hatası olursa ignore et
    with open(app_js_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    
    if "initWebSocket" not in content:
        with open(app_js_path, "a", encoding="utf-8") as f:
            f.write("\n" + ws_code)
        print("✅ app.js güncellendi.")
    else:
        print("ℹ️ WebSocket kodu zaten ekli.")

except Exception as e:
    print(f"❌ Hata: {e}")
