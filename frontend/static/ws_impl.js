
// ============================================
// WEBSOCKET YÖNETİMİ (Gerçek Zamanlı Güncelleme)
// ============================================

let ws = null;
let wsListeners = [];
const wsReconnectDelay = 3000;

function initWebSocket(callback) {
    if (callback && typeof callback === 'function') {
        wsListeners.push(callback);
    }

    // Eğer zaten bağlıysa veya deniyorsa tekrar bağlama
    if (ws && (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING)) {
        return;
    }

    // API_URL global olarak app.js başında tanımlı
    // WS URL'sini buradan türetelim: ws://localhost:8000/ws
    let wsUrl = API_URL.replace('http', 'ws').replace('/api', '/ws');

    // Eğer replacement başarısız olursa manuel oluştur (Fallback)
    if (!wsUrl.includes('ws')) {
        // wss:// or ws://
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const host = window.location.hostname || 'localhost';
        wsUrl = `${protocol}//${host}:8000/ws`;
    }

    console.log('🔗 WebSocket Bağlanıyor:', wsUrl);

    function connect() {
        ws = new WebSocket(wsUrl);

        ws.onopen = () => {
            console.log('✅ WebSocket Bağlandı!');
        };

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                // console.log('📩 Yeni Mesaj:', data);
                wsListeners.forEach(listener => listener(data));
            } catch (e) {
                console.error('❌ WebSocket veri hatası:', e);
            }
        };

        ws.onclose = () => {
            console.warn('⚠️ WebSocket koptu. Yeniden bağlanılıyor...');
            ws = null;
            setTimeout(connect, wsReconnectDelay);
        };

        ws.onerror = (err) => {
            console.error('❌ WebSocket hatası:', err);
            ws.close();
        };
    }

    connect();
}
