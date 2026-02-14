// Sıramatik - Ortak JavaScript Fonksiyonları
// API/WS adresi: config.js yüklüyse oradan (window.API_URL), yoksa hostname'e göre hesaplanır.

const currentHost = window.location.hostname || 'localhost';
const isLocal = typeof window.SIRAMATIK_IS_LOCAL !== 'undefined' ? window.SIRAMATIK_IS_LOCAL : (currentHost === 'localhost' || currentHost === '127.0.0.1');
const API_URL = (typeof window.API_URL !== 'undefined' && window.API_URL) ? window.API_URL : (isLocal ? 'http://127.0.0.1:8000' : 'https://siramatik-production.up.railway.app');
if (typeof window !== 'undefined') window.API_URL = API_URL;

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

// WebSocket'i global olarak erişilebilir yap (admin paneli için)
window.ws = ws;

function initWebSocket(callback) {
    if (callback && typeof callback === 'function') {
        wsListeners.push(callback);
    }

    // Eğer zaten bağlıysa veya deniyorsa tekrar bağlama
    if (ws && (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING)) {
        return;
    }

    const wsUrl = (typeof window.SIRAMATIK_WS_URL !== 'undefined' && window.SIRAMATIK_WS_URL)
        ? window.SIRAMATIK_WS_URL
        : (isLocal ? 'ws://127.0.0.1:8000/ws' : 'wss://siramatik-production.up.railway.app/ws');

    console.log('🔗 WebSocket Bağlanıyor:', wsUrl);

    function connect() {
        ws = new WebSocket(wsUrl);
        window.ws = ws; // Global erişim için

        ws.onopen = () => {
            console.log('[OK] WebSocket Bağlandı!');
            window.ws = ws;
            var w = document.getElementById('connection-w');
            if (w) w.className = 'connection-badge active';
        };

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                // console.log('📩 Yeni Mesaj:', data);
                wsListeners.forEach(listener => listener(data));
            } catch (e) {
                console.error('[ERR] WebSocket veri hatası:', e);
            }
        };

        ws.onclose = () => {
            console.warn('[WARN] WebSocket koptu. Yeniden bağlanılıyor...');
            ws = null;
            window.ws = null;
            var w = document.getElementById('connection-w');
            if (w) w.className = 'connection-badge inactive';
            setTimeout(connect, wsReconnectDelay);
        };

        ws.onerror = (err) => {
            console.error('[ERR] WebSocket hatası:', err);
            ws.close();
        };
    }

    connect();
}
