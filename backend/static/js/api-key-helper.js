// API isteklerine otomatik olarak X-API-KEY ekleyen yardımcı Javascript
function addApiKeyToRequests() {
    const API_KEY = "5f46f9d0-ca57-4c39-a104-af1bad3022ea";
    
    // XMLHttpRequest için
    const originalXHROpen = XMLHttpRequest.prototype.open;
    XMLHttpRequest.prototype.open = function() {
        const result = originalXHROpen.apply(this, arguments);
        this.setRequestHeader('X-API-KEY', API_KEY);
        return result;
    };
    
    // Fetch API için
    const originalFetch = window.fetch;
    window.fetch = function() {
        const args = Array.from(arguments);
        const resource = args[0];
        const config = args[1] || {};
        
        // İstek yapılandırması varsa
        if (config.headers) {
            if (config.headers instanceof Headers) {
                config.headers.append('X-API-KEY', API_KEY);
            } else {
                config.headers['X-API-KEY'] = API_KEY;
            }
        } else {
            config.headers = {
                'X-API-KEY': API_KEY
            };
        }
        
        args[1] = config;
        return originalFetch.apply(this, args);
    };
    
    console.log('API Key otomatik olarak isteklere ekleniyor: ' + API_KEY);
}

// Sayfa yüklendiğinde çalıştır
document.addEventListener('DOMContentLoaded', function() {
    addApiKeyToRequests();
});
