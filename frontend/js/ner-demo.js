// frontend/js/ner-demo.js - NER Demo Interface

class NERDemo {
    constructor() {
        this.apiClient = window.apiClient || new APIClient();
        this.initializeElements();
        this.attachEventListeners();
        this.checkBackendStatus();
    }
    
    initializeElements() {
        this.form = document.getElementById('ner-form');
        this.input = document.getElementById('description-input');
        this.methodSelect = document.getElementById('method-select');
        this.submitBtn = document.getElementById('submit-btn');
        this.resultsContainer = document.getElementById('results-container');
        this.statusIndicator = document.getElementById('status-indicator');
    }
    
    attachEventListeners() {
        if (this.form) {
            this.form.addEventListener('submit', (e) => this.handleSubmit(e));
        }
        
        // Add example buttons if they exist
        document.querySelectorAll('.example-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.input.value = e.target.dataset.example;
            });
        });
    }
    
    async checkBackendStatus() {
        try {
            const health = await this.apiClient.healthCheck();
            this.updateStatus(true, health.mode || 'production');
        } catch (error) {
            this.updateStatus(false);
        }
    }
    
    updateStatus(online, mode = 'unknown') {
        if (!this.statusIndicator) return;
        
        if (online) {
            this.statusIndicator.innerHTML = `
                <span class="status-dot status-online"></span>
                Backend Online (${mode})
            `;
            this.statusIndicator.className = 'status status-online';
        } else {
            this.statusIndicator.innerHTML = `
                <span class="status-dot status-offline"></span>
                Backend Offline
            `;
            this.statusIndicator.className = 'status status-offline';
        }
    }
    
    async handleSubmit(e) {
        e.preventDefault();
        
        const description = this.input.value.trim();
        const method = this.methodSelect?.value || 'vocab';
        
        if (!description) {
            window.showToast('Please enter a description', 'error');
            return;
        }
        
        this.setLoading(true);
        
        try {
            const result = await this.apiClient.mapDescription(description, method);
            this.displayResults(result);
            window.showToast('Formula generated successfully!', 'success');
        } catch (error) {
            this.displayError(error.message);
            window.showToast('Error: ' + error.message, 'error');
        } finally {
            this.setLoading(false);
        }
    }
    
    setLoading(loading) {
        if (this.submitBtn) {
            this.submitBtn.disabled = loading;
            this.submitBtn.textContent = loading ? 'Processing...' : 'Generate Formula';
        }
    }
    
    displayResults(result) {
        if (!this.resultsContainer) return;
        
        const html = `
            <div class="result-card">
                <h3>Generated Formula</h3>
                <div class="formula-output">${this.escapeHtml(result.formula)}</div>
                
                <div class="result-meta">
                    <span>Confidence: ${(result.confidence * 100).toFixed(0)}%</span>
                    <span>Method: ${result.method}</span>
                    <span>Time: ${result.processing_time_ms}ms</span>
                </div>
                
                ${result.entities && result.entities.length > 0 ? `
                    <h4>Detected Entities</h4>
                    <div class="entities-list">
                        ${result.entities.map(e => `
                            <span class="entity entity-${e.label.toLowerCase()}">
                                ${this.escapeHtml(e.text)} <small>${e.label}</small>
                            </span>
                        `).join('')}
                    </div>
                ` : ''}
            </div>
        `;
        
        this.resultsContainer.innerHTML = html;
        this.resultsContainer.style.display = 'block';
    }
    
    displayError(message) {
        if (!this.resultsContainer) return;
        
        this.resultsContainer.innerHTML = `
            <div class="error-message">
                <strong>Error:</strong> ${this.escapeHtml(message)}
            </div>
        `;
        this.resultsContainer.style.display = 'block';
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Make NERDemo globally available
window.NERDemo = NERDemo;
