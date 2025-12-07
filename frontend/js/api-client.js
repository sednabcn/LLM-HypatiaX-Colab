/**
 * HypatiaX API Client
 * Unified API client for all backend endpoints
 * File: frontend/js/api-client.js
 */

class APIClient {
    constructor(baseURL = 'http://localhost:5000') {
        this.baseURL = baseURL;
        this.timeout = 30000; // 30 seconds
    }

    /**
     * Generic request handler with error handling
     */
    async request(endpoint, options = {}) {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), this.timeout);

        try {
            const response = await fetch(`${this.baseURL}${endpoint}`, {
                ...options,
                signal: controller.signal,
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                }
            });

            clearTimeout(timeoutId);

            if (!response.ok) {
                const error = await response.json().catch(() => ({ error: 'Unknown error' }));
                throw new Error(error.error || `HTTP ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            clearTimeout(timeoutId);
            if (error.name === 'AbortError') {
                throw new Error('Request timeout - server not responding');
            }
            throw error;
        }
    }

    // ============================================================================
    // HEALTH & INFO
    // ============================================================================

    async healthCheck() {
        return this.request('/api/health');
    }

    async getInfo() {
        return this.request('/');
    }

    // ============================================================================
    // HYPATIAX - Tableau Formula Mapping
    // ============================================================================

    async mapDescription(description, method = 'vocab') {
        return this.request('/api/hypatiax/map', {
            method: 'POST',
            body: JSON.stringify({ description, method })
        });
    }

    async runTests() {
        return this.request('/api/hypatiax/test');
    }

    // ============================================================================
    // NER - Formula Extraction
    // ============================================================================

    async extractFormula(text, domain = 'general') {
        return this.request('/api/ner/extract-formula', {
            method: 'POST',
            body: JSON.stringify({ text, domain })
        });
    }

    async recognizeEntities(text) {
        return this.request('/api/ner/recognize-entities', {
            method: 'POST',
            body: JSON.stringify({ text })
        });
    }

    async convertToLatex(formula) {
        return this.request('/api/ner/convert-to-latex', {
            method: 'POST',
            body: JSON.stringify({ formula })
        });
    }

    async parseFormula(formula) {
        return this.request('/api/ner/parse-structure', {
            method: 'POST',
            body: JSON.stringify({ formula })
        });
    }

    async validateFormula(formula) {
        return this.request('/api/ner/validate-syntax', {
            method: 'POST',
            body: JSON.stringify({ formula })
        });
    }

    async identifyDomain(formula) {
        return this.request('/api/ner/identify-domain', {
            method: 'POST',
            body: JSON.stringify({ formula })
        });
    }

    async batchProcess(formulas) {
        return this.request('/api/ner/batch-process', {
            method: 'POST',
            body: JSON.stringify({ formulas })
        });
    }

    // ============================================================================
    // DEFI - Calculations
    // ============================================================================

    async calculateILPercentage(initialPrice, currentPrice) {
        return this.request('/api/defi/il-percentage', {
            method: 'POST',
            body: JSON.stringify({
                initial_price: initialPrice,
                current_price: currentPrice
            })
        });
    }

    async calculateQualityScore(params) {
        return this.request('/api/defi/quality-score', {
            method: 'POST',
            body: JSON.stringify(params)
        });
    }

    async analyzePosition(params) {
        return this.request('/api/defi/analyze-position', {
            method: 'POST',
            body: JSON.stringify(params)
        });
    }

    async calculateILLegacy(params) {
        return this.request('/api/defi/calculate-il', {
            method: 'POST',
            body: JSON.stringify(params)
        });
    }
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

function formatNumber(num, decimals = 2) {
    if (num === null || num === undefined || num === 'infinite') return num;
    return parseFloat(num).toLocaleString('en-US', {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
    });
}

function formatCurrency(num, decimals = 2) {
    if (num === null || num === undefined || num === 'infinite') return num;
    return '$' + formatNumber(num, decimals);
}

function formatPercent(num, decimals = 2) {
    if (num === null || num === undefined) return num;
    return formatNumber(num, decimals) + '%';
}

function showLoading(element, message = 'Loading...') {
    if (!element) return;
    element.innerHTML = `
        <div class="loading-spinner">
            <div class="spinner"></div>
            <p>${message}</p>
        </div>
    `;
    element.style.display = 'block';
}

function showError(element, error) {
    if (!element) return;
    const errorMessage = error.message || error.toString();
    element.innerHTML = `
        <div class="error-message">
            <div class="error-icon">⚠️</div>
            <div class="error-content">
                <h4>Error</h4>
                <p>${errorMessage}</p>
            </div>
        </div>
    `;
    element.style.display = 'block';
}

function showSuccess(element, message) {
    if (!element) return;
    element.innerHTML = `
        <div class="success-message">
            <div class="success-icon">✅</div>
            <div class="success-content">
                <p>${message}</p>
            </div>
        </div>
    `;
    element.style.display = 'block';
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ============================================================================
// GLOBAL INSTANCES & EXPORTS
// ============================================================================

// Create global API client instance
window.apiClient = new APIClient();
window.APIClient = APIClient;

// Export utilities
window.formatNumber = formatNumber;
window.formatCurrency = formatCurrency;
window.formatPercent = formatPercent;
window.showLoading = showLoading;
window.showError = showError;
window.showSuccess = showSuccess;
window.debounce = debounce;
window.escapeHtml = escapeHtml;
