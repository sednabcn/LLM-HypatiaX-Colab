// frontend/js/api-client.js - API Client

class APIClient {
    constructor(baseURL = 'http://localhost:5000/api') {
        this.baseURL = baseURL;
        this.timeout = 30000; // 30 seconds
    }
    
    /**
     * Make API request
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), this.timeout);
        
        try {
            const response = await fetch(url, {
                ...options,
                signal: controller.signal,
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                }
            });
            
            clearTimeout(timeoutId);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            clearTimeout(timeoutId);
            
            if (error.name === 'AbortError') {
                throw new Error('Request timeout - server may be offline');
            }
            throw error;
        }
    }
    
    /**
     * Check API health
     */
    async healthCheck() {
        return await this.request('/health');
    }
    
    /**
     * Map description to formula
     */
    async mapDescription(description, method = 'vocab') {
        return await this.request('/map', {
            method: 'POST',
            body: JSON.stringify({ description, method })
        });
    }
    
    /**
     * Run test suite
     */
    async runTests() {
        return await this.request('/test');
    }
}

// Make APIClient globally available
window.APIClient = APIClient;
