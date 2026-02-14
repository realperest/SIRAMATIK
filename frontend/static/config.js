/**
 * Sıramatik - Tüm sayfalar için tek merkezi API/WS adresi.
 * Bu dosyayı değiştirerek tüm frontend (kiosk, ekran, bilet, personel, admin, raporlar vb.) aynı backend'i kullanır.
 */
(function() {
    'use strict';
    var host = typeof window !== 'undefined' && window.location && window.location.hostname ? window.location.hostname : 'localhost';
    var isLocal = host === 'localhost' || host === '127.0.0.1';
    window.API_URL = isLocal ? 'http://127.0.0.1:8000' : 'https://siramatik-production.up.railway.app';
    window.SIRAMATIK_WS_URL = isLocal ? 'ws://127.0.0.1:8000/ws' : 'wss://siramatik-production.up.railway.app/ws';
    window.SIRAMATIK_IS_LOCAL = isLocal;
})();
