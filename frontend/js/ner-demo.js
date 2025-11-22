/**
 * NER Demo Interface
 * Handles Named Entity Recognition demo on ner-demo.html
 * File: frontend/js/ner-demo.js
 */

class NERDemo {
    constructor() {
        this.apiClient = window.apiClient || new APIClient();
        this.initialize();
    }
    
    async initialize() {
        console.log('Initializing NER Demo...');
        this.initializeElements();
        this.attachEventListeners();
        await this.checkAPIStatus();
    }
    
    // ============================================================================
    // INITIALIZATION
    // ============================================================================
    
    initializeElements() {
        // Demo controls
        this.modelSelect = document.getElementById('model-select');
        this.inputText = document.getElementById('input-text');
        this.extractBtn = document.getElementById('extract-btn');
        this.clearBtn = document.getElementById('clear-btn');
        this.exampleBtn = document.getElementById('example-btn');
        
        // Results
        this.loadingEl = document.getElementById('loading');
        this.resultsSection = document.getElementById('results-section');
        this.highlightedText = document.getElementById('highlighted-text');
        this.entityList = document.getElementById('entity-list');
        this.totalEntities = document.getElementById('total-entities');
        this.processingTime = document.getElementById('processing-time');
        this.confidence = document.getElementById('confidence');
        this.rawJson = document.getElementById('raw-json');
        this.errorMessage = document.getElementById('error-message');
        
        // Status
        this.apiStatus = document.getElementById('api-status');
    }
    
    attachEventListeners() {
        if (this.extractBtn) {
            this.extractBtn.addEventListener('click', () => this.handleExtract());
        }
        
        if (this.clearBtn) {
            this.clearBtn.addEventListener('click', () => this.handleClear());
        }
        
        if (this.exampleBtn) {
            this.exampleBtn.addEventListener('click', () => this.loadExample());
        }
    }
    
    // ============================================================================
    // API STATUS
    // ============================================================================
    
    async checkAPIStatus() {
        if (!this.apiStatus) return;
        
        try {
            const health = await this.apiClient.healthCheck();
            this.apiStatus.innerHTML = `✅ Backend Online - ${health.mode || 'production'} mode`;
            this.apiStatus.className = 'api-status online';
        } catch (error) {
            this.apiStatus.innerHTML = '❌ Backend Offline';
            this.apiStatus.className = 'api-status offline';
            console.error('API Status check failed:', error);
        }
    }
    
    // ============================================================================
    // EVENT HANDLERS
    // ============================================================================
    
    async handleExtract() {
        const text = this.inputText.value.trim();
        
        if (!text) {
            window.showToast('Please enter some text', 'error');
            return;
        }
        
        // Show loading
        this.showLoading(true);
        this.hideError();
        this.hideResults();
        
        const startTime = Date.now();
        
        try {
            // Use the recognize entities endpoint
            const result = await this.apiClient.recognizeEntities(text);
            const processingTime = Date.now() - startTime;
            
            this.displayResults(result, text, processingTime);
            window.showToast('Entities extracted successfully!', 'success');
        } catch (error) {
            this.showError(error.message);
            window.showToast('Error: ' + error.message, 'error');
        } finally {
            this.showLoading(false);
        }
    }
    
    handleClear() {
        this.inputText.value = '';
        this.hideResults();
        this.hideError();
        this.inputText.focus();
    }
    
    loadExample() {
        const examples = [
            "Show me the sum of sales by region for last quarter",
            "Calculate average profit margin for each product category",
            "Count the number of orders where discount is greater than 10%",
            "Find total revenue by customer segment",
            "Display the maximum sales value for each year"
        ];
        
        const randomExample = examples[Math.floor(Math.random() * examples.length)];
        this.inputText.value = randomExample;
        this.inputText.focus();
        window.showToast('Example loaded!', 'success');
    }
    
    // ============================================================================
    // DISPLAY RESULTS
    // ============================================================================
    
    displayResults(result, originalText, processingTime) {
        if (!result || !result.entities) {
            this.showError('No entities found in the response');
            return;
        }
        
        // Update stats
        if (this.totalEntities) {
            this.totalEntities.textContent = result.entities.length;
        }
        if (this.processingTime) {
            this.processingTime.textContent = processingTime + 'ms';
        }
        if (this.confidence) {
            const avgConfidence = result.entities.length > 0 
                ? (result.entities.reduce((sum, e) => sum + (e.confidence || 1), 0) / result.entities.length * 100).toFixed(0)
                : 0;
            this.confidence.textContent = avgConfidence + '%';
        }
        
        // Display highlighted text
        if (this.highlightedText) {
            this.highlightedText.innerHTML = this.createHighlightedText(originalText, result.entities);
        }
        
        // Display entity list
        if (this.entityList) {
            this.entityList.innerHTML = this.createEntityList(result.entities);
        }
        
        // Display raw JSON
        if (this.rawJson) {
            this.rawJson.textContent = JSON.stringify(result, null, 2);
        }
        
        // Show results section
        this.showResults(true);
    }
    
    createHighlightedText(text, entities) {
        if (!entities || entities.length === 0) {
            return escapeHtml(text);
        }
        
        // Sort entities by start position
        const sortedEntities = [...entities].sort((a, b) => a.start - b.start);
        
        let html = '';
        let lastIndex = 0;
        
        sortedEntities.forEach(entity => {
            // Add text before entity
            html += escapeHtml(text.substring(lastIndex, entity.start));
            
            // Add highlighted entity
            const color = this.getEntityColor(entity.label);
            html += `<mark style="background-color: ${color}; padding: 2px 4px; border-radius: 3px;" 
                          title="${entity.label}">
                        ${escapeHtml(entity.text)}
                     </mark>`;
            
            lastIndex = entity.end;
        });
        
        // Add remaining text
        html += escapeHtml(text.substring(lastIndex));
        
        return html;
    }
    
    createEntityList(entities) {
        if (!entities || entities.length === 0) {
            return '<p class="empty-state">No entities found</p>';
        }
        
        return entities.map(entity => {
            const color = this.getEntityColor(entity.label);
            return `
                <div class="entity-item" style="padding: 10px; margin: 5px 0; background: #f9fafb; border-left: 4px solid ${color}; border-radius: 4px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <strong style="color: ${color};">${escapeHtml(entity.text)}</strong>
                            <span class="entity-badge" style="margin-left: 10px; padding: 2px 8px; background: ${color}; color: white; border-radius: 12px; font-size: 0.8em;">
                                ${entity.label}
                            </span>
                        </div>
                        ${entity.confidence ? `
                            <span style="color: #6b7280; font-size: 0.9em;">
                                ${(entity.confidence * 100).toFixed(0)}%
                            </span>
                        ` : ''}
                    </div>
                    <div style="color: #6b7280; font-size: 0.85em; margin-top: 5px;">
                        Position: ${entity.start}-${entity.end}
                    </div>
                </div>
            `;
        }).join('');
    }
    
    getEntityColor(label) {
        const colors = {
            'AGGREGATION': '#3b82f6',     // Blue
            'FIELD': '#10b981',            // Green
            'FILTER': '#f59e0b',           // Orange
            'DIMENSION': '#8b5cf6',        // Purple
            'MEASURE': '#ef4444',          // Red
            'TIME_PERIOD': '#ec4899',      // Pink
            'COMPARISON': '#14b8a6',       // Teal
            'VALUE': '#f97316',            // Orange
            'FUNCTION': '#6366f1'          // Indigo
        };
        
        return colors[label] || '#6b7280'; // Default gray
    }
    
    // ============================================================================
    // UI STATE MANAGEMENT
    // ============================================================================
    
    showLoading(show) {
        if (this.loadingEl) {
            this.loadingEl.classList.toggle('hidden', !show);
        }
        if (this.extractBtn) {
            this.extractBtn.disabled = show;
            this.extractBtn.textContent = show ? 'Processing...' : '🎯 Extract Entities';
        }
    }
    
    showResults(show) {
        if (this.resultsSection) {
            this.resultsSection.classList.toggle('hidden', !show);
        }
    }
    
    hideResults() {
        this.showResults(false);
    }
    
    showError(message) {
        if (this.errorMessage) {
            this.errorMessage.innerHTML = `
                <div class="error-icon">⚠️</div>
                <div class="error-content">
                    <h4>Error</h4>
                    <p>${escapeHtml(message)}</p>
                </div>
            `;
            this.errorMessage.classList.remove('hidden');
        }
    }
    
    hideError() {
        if (this.errorMessage) {
            this.errorMessage.classList.add('hidden');
        }
    }
}

// Initialize NER Demo when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.nerDemo = new NERDemo();
    console.log('✅ NER Demo initialized');
});
