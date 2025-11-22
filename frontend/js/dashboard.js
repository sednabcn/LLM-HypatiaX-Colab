/**
 * Dashboard Interface
 * Handles dashboard metrics and DeFi calculator
 * File: frontend/js/dashboard.js
 */

class Dashboard {
    constructor() {
        this.apiClient = window.apiClient || new APIClient();
        this.initialize();
    }
    
    async initialize() {
        console.log('Initializing Dashboard...');
        await this.checkAPIStatus();
        this.initializeDeFiCalculator();
        this.startAutoRefresh();
    }
    
    // ============================================================================
    // API STATUS
    // ============================================================================
    
    async checkAPIStatus() {
        const statusEl = document.getElementById('api-status');
        if (!statusEl) return;
        
        try {
            const health = await this.apiClient.healthCheck();
            statusEl.innerHTML = `✅ Backend Online - ${health.mode || 'production'} mode`;
            statusEl.className = 'api-status online';
            
            // Update metric cards if they exist
            this.updateMetrics(health);
        } catch (error) {
            statusEl.innerHTML = '❌ Backend Offline - Using demo mode';
            statusEl.className = 'api-status offline';
            console.error('API Status check failed:', error);
        }
    }
    
    updateMetrics(health) {
        // These IDs match the dashboard.html
        const activeModels = document.getElementById('active-models');
        const apiRequests = document.getElementById('api-requests');
        
        if (activeModels && health.models_loaded) {
            activeModels.textContent = '8';
        }
    }
    
    // ============================================================================
    // DEFI CALCULATOR
    // ============================================================================
    
    initializeDeFiCalculator() {
        // Quick IL Calculator
        const quickForm = document.getElementById('quick-il-form');
        if (quickForm) {
            quickForm.addEventListener('submit', (e) => this.handleQuickIL(e));
            
            // Add price change preview
            const inputs = quickForm.querySelectorAll('input[type="number"]');
            inputs.forEach(input => {
                input.addEventListener('input', () => this.updatePriceChangePreview());
            });
        }
        
        // Full Position Analysis
        const positionForm = document.getElementById('position-analysis-form');
        if (positionForm) {
            positionForm.addEventListener('submit', (e) => this.handlePositionAnalysis(e));
        }
        
        // Load example if requested
        if (window.location.search.includes('example=true')) {
            this.loadExampleData();
        }
    }
    
    updatePriceChangePreview() {
        const form = document.getElementById('quick-il-form');
        const preview = document.getElementById('price-change-preview');
        if (!form || !preview) return;
        
        const initialPrice = parseFloat(form.initial_price.value);
        const currentPrice = parseFloat(form.current_price.value);
        
        if (initialPrice && currentPrice) {
            const change = ((currentPrice - initialPrice) / initialPrice * 100).toFixed(2);
            const arrow = change >= 0 ? '↑' : '↓';
            const color = change >= 0 ? '#10b981' : '#ef4444';
            
            preview.innerHTML = `
                <div style="padding: 10px; background: #f3f4f6; border-radius: 4px; margin: 10px 0;">
                    Price Change: <strong style="color: ${color}">${arrow} ${Math.abs(change)}%</strong>
                </div>
            `;
        } else {
            preview.innerHTML = '';
        }
    }
    
    async handleQuickIL(e) {
        e.preventDefault();
        const form = e.target;
        const resultDiv = document.getElementById('quick-il-result');
        
        const initialPrice = parseFloat(form.initial_price.value);
        const currentPrice = parseFloat(form.current_price.value);
        
        if (!initialPrice || !currentPrice || initialPrice <= 0 || currentPrice <= 0) {
            showError(resultDiv, new Error('Please enter valid prices'));
            return;
        }
        
        showLoading(resultDiv, 'Calculating IL...');
        
        try {
            const result = await this.apiClient.calculateILPercentage(initialPrice, currentPrice);
            
            resultDiv.innerHTML = `
                <div class="result-card">
                    <h3>Impermanent Loss</h3>
                    <div class="il-result">
                        <div class="il-percentage" style="font-size: 2.5em; color: ${result.il_percentage < -5 ? '#ef4444' : '#f59e0b'};">
                            ${result.il_percentage.toFixed(2)}%
                        </div>
                        <p style="margin: 10px 0;">Price Ratio: ${result.price_ratio.toFixed(4)}x</p>
                        <p style="color: #6b7280; font-size: 0.9em;">
                            ${result.interpretation}
                        </p>
                    </div>
                </div>
            `;
            resultDiv.style.display = 'block';
        } catch (error) {
            showError(resultDiv, error);
        }
    }
    
    async handlePositionAnalysis(e) {
        e.preventDefault();
        const form = e.target;
        const resultDiv = document.getElementById('position-analysis-result');
        
        const params = {
            initial_token_a: parseFloat(form.initial_token_a.value),
            initial_token_b: parseFloat(form.initial_token_b.value),
            initial_price: parseFloat(form.initial_price.value),
            current_price: parseFloat(form.current_price.value),
            daily_volume_usd: parseFloat(form.daily_volume_usd.value),
            pool_tvl_usd: parseFloat(form.pool_tvl_usd.value),
            days_elapsed: parseInt(form.days_elapsed.value),
            fee_rate: parseFloat(form.fee_rate.value)
        };
        
        showLoading(resultDiv, 'Analyzing position...');
        
        try {
            const result = await this.apiClient.analyzePosition(params);
            
            resultDiv.innerHTML = `
                <div class="result-card">
                    <h3>Position Analysis Results</h3>
                    
                    <div class="analysis-section">
                        <h4>Current Position</h4>
                        <p>Token A: ${formatNumber(result.current_position.token_a, 4)}</p>
                        <p>Token B: ${formatNumber(result.current_position.token_b, 4)}</p>
                        <p>Value: ${formatCurrency(result.current_position.value_usd)}</p>
                    </div>
                    
                    <div class="analysis-section">
                        <h4>Performance</h4>
                        <p>Impermanent Loss: <strong style="color: ${result.il_percentage < -5 ? '#ef4444' : '#f59e0b'}">${formatPercent(result.il_percentage)}</strong></p>
                        <p>Fee Income: ${formatCurrency(result.fee_income_usd)}</p>
                        <p>Net P&L: <strong style="color: ${result.net_pnl_usd >= 0 ? '#10b981' : '#ef4444'}">${formatCurrency(result.net_pnl_usd)}</strong></p>
                    </div>
                    
                    <div class="analysis-section">
                        <h4>Pool Metrics</h4>
                        <p>Quality Score: ${formatNumber(result.pool_quality_score, 2)}/100</p>
                        <p>Daily Turnover: ${formatPercent(result.daily_turnover_rate)}</p>
                        <p>Days to Break Even: ${result.days_to_breakeven === 'infinite' ? '∞' : formatNumber(result.days_to_breakeven, 1)}</p>
                    </div>
                    
                    <div class="analysis-section">
                        <h4>Recommendation</h4>
                        <p>${result.recommendation}</p>
                    </div>
                </div>
            `;
            resultDiv.style.display = 'block';
        } catch (error) {
            showError(resultDiv, error);
        }
    }
    
    loadExampleData() {
        const form = document.getElementById('position-analysis-form');
        if (!form) return;
        
        form.initial_token_a.value = '10';
        form.initial_token_b.value = '10000';
        form.initial_price.value = '1000';
        form.current_price.value = '1200';
        form.daily_volume_usd.value = '50000';
        form.pool_tvl_usd.value = '1000000';
        form.days_elapsed.value = '30';
        form.fee_rate.value = '0.003';
        
        window.showToast('Example data loaded!', 'success');
    }
    
    // ============================================================================
    // AUTO REFRESH
    // ============================================================================
    
    startAutoRefresh() {
        // Refresh API status every 30 seconds
        setInterval(() => this.checkAPIStatus(), 30000);
    }
}

// Initialize dashboard when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new Dashboard();
});
