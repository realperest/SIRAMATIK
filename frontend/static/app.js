// Sıramatik - Ortak JavaScript Fonksiyonları

// API adresi: Eğer sayfa IP ile açıldıysa (mobildeki gibi), API'yi de o IP üzerinden çağır.
const currentHost = window.location.hostname || 'localhost';
const API_URL = `http://${currentHost}:8000/api`;

// API çağrısı yardımcı fonksiyonu
async function apiCall(endpoint, options = {}) {
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };

    // Token varsa ekle
    const token = localStorage.getItem('token');
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    try {
        const response = await fetch(`${API_URL}${endpoint}`, {
            headers: headers,
            ...options
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Bir hata oluştu');
        }

        return await response.json();
    } catch (error) {
        console.error('API Hatası:', error);
        throw error;
    }
}

// Tarih formatlama
function formatTarih(tarihString) {
    const d = new Date(tarihString);
    const simdi = new Date();

    const isBugun = d.getDate() === simdi.getDate() &&
        d.getMonth() === simdi.getMonth() &&
        d.getFullYear() === simdi.getFullYear();

    const saat = d.toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' });

    if (isBugun) {
        return `BUGÜN ${saat}`;
    } else {
        const tarih = d.toLocaleDateString('tr-TR', { day: '2-digit', month: '2-digit', year: 'numeric' });
        return `${tarih} ${saat}`;
    }
}

// Toast bildirimi göster
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        padding: 15px 25px;
        background: ${type === 'success' ? '#4CAF50' : '#f44336'};
        color: white;
        border-radius: 10px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        z-index: 9999;
        animation: slideIn 0.3s ease-out;
    `;

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'fadeOut 0.3s ease-out';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Loading göster/gizle
function showLoading(show = true) {
    let loader = document.getElementById('global-loader');

    if (show) {
        if (!loader) {
            loader = document.createElement('div');
            loader.id = 'global-loader';
            loader.innerHTML = '<div class="spinner"></div>';
            loader.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0,0,0,0.5);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 9998;
            `;
            document.body.appendChild(loader);
        }
    } else {
        if (loader) loader.remove();
    }
}


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
