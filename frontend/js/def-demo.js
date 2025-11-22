/**
 * DeFi Calculator Demo Interface
 * Handles DeFi position analysis and IL calculations
 * File: frontend/js/defi-demo.js
 */

class DeFiDemo {
    constructor() {
        this.apiClient = window.apiClient || new APIClient();
        this.initialize();
    }
    
    async initialize() {
        console.log('Initializing DeFi Demo...');
        await this.checkAPIStatus();
        this.initializeQuickIL();
        this.initializePositionAnalysis();
        this.loadURLParameters();
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
        } catch (error) {
            statusEl.innerHTML = '❌ Backend Offline - Using demo mode';
            statusEl.className = 'api-status offline';
            console.error('API Status check failed:', error);
        }
    }
    
    // ============================================================================
    // QUICK IL CALCULATOR
    // ============================================================================
    
    initializeQuickIL() {
        const form = document.getElementById('quick-il-form');
        if (!form) return;
        
        // Handle form submission
        form.addEventListener('submit', (e) => this.handleQuickIL(e));
        
        // Add real-time price change preview
        const inputs = form.querySelectorAll('input[type="number"]');
        inputs.forEach(input => {
            input.addEventListener('input', () => this.updatePriceChangePreview());
        });
    }
    
    updatePriceChangePreview() {
        const form = document.getElementById('quick-il-form');
        const preview = document.getElementById('price-change-preview');
        if (!form || !preview) return;
        
        const initialPrice = parseFloat(form.initial_price.value);
        const currentPrice = parseFloat(form.current_price.value);
        
        if (initialPrice && currentPrice && initialPrice > 0) {
            const change = ((currentPrice - initialPrice) / initialPrice * 100);
            const arrow = change >= 0 ? '↑' : '↓';
            const color = change >= 0 ? '#10b981' : '#ef4444';
            
            preview.innerHTML = `
                <div style="padding: 12px; background: #f3f4f6; border-radius: 6px; margin: 10px 0;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="color: #6b7280;">Price Change:</span>
                        <strong style="color: ${color}; font-size: 1.1em;">
                            ${arrow} ${Math.abs(change).toFixed(2)}%
                        </strong>
                    </div>
                    <div style="color: #9ca3af; font-size: 0.85em; margin-top: 5px;">
                        Ratio: ${(currentPrice / initialPrice).toFixed(4)}x
                    </div>
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
        
        // Validation
        if (!initialPrice || !currentPrice || initialPrice <= 0 || currentPrice <= 0) {
            showError(resultDiv, new Error('Please enter valid prices (greater than 0)'));
            return;
        }
        
        showLoading(resultDiv, 'Calculating impermanent loss...');
        
        try {
            const result = await this.apiClient.calculateILPercentage(initialPrice, currentPrice);
            
            const ilColor = this.getILColor(result.il_percentage);
            const severity = this.getILSeverity(result.il_percentage);
            
            resultDiv.innerHTML = `
                <div class="result-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 25px; border-radius: 12px; margin-top: 20px;">
                    <h3 style="margin: 0 0 20px 0; font-size: 1.3em;">Impermanent Loss Analysis</h3>
                    
                    <div style="background: rgba(255,255,255,0.15); padding: 20px; border-radius: 8px; margin-bottom: 15px;">
                        <div style="text-align: center;">
                            <div style="font-size: 3em; font-weight: bold; margin-bottom: 10px;">
                                ${result.il_percentage.toFixed(2)}%
                            </div>
                            <div style="font-size: 1.1em; opacity: 0.9;">
                                Impermanent Loss
                            </div>
                        </div>
                    </div>
                    
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 15px;">
                        <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 8px;">
                            <div style="opacity: 0.8; font-size: 0.9em; margin-bottom: 5px;">Price Ratio</div>
                            <div style="font-size: 1.3em; font-weight: bold;">${result.price_ratio.toFixed(4)}x</div>
                        </div>
                        <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 8px;">
                            <div style="opacity: 0.8; font-size: 0.9em; margin-bottom: 5px;">Severity</div>
                            <div style="font-size: 1.3em; font-weight: bold;">${severity}</div>
                        </div>
                    </div>
                    
                    <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 8px;">
                        <div style="font-size: 0.95em; line-height: 1.6;">
                            ${result.interpretation}
                        </div>
                    </div>
                    
                    <div style="margin-top: 15px; padding: 12px; background: rgba(255,255,255,0.1); border-radius: 8px; font-size: 0.9em;">
                        💡 <strong>Tip:</strong> IL can be offset by trading fees. Use the Complete Position Analysis below for full details.
                    </div>
                </div>
            `;
            resultDiv.style.display = 'block';
        } catch (error) {
            showError(resultDiv, error);
        }
    }
    
    getILColor(ilPercentage) {
        if (ilPercentage >= -1) return '#10b981';      // Green - minimal
        if (ilPercentage >= -5) return '#f59e0b';      // Orange - moderate
        if (ilPercentage >= -10) return '#ef4444';     // Red - significant
        return '#991b1b';                              // Dark red - severe
    }
    
    getILSeverity(ilPercentage) {
        if (ilPercentage >= -1) return '✅ Minimal';
        if (ilPercentage >= -5) return '⚠️ Moderate';
        if (ilPercentage >= -10) return '❌ Significant';
        return '🚨 Severe';
    }
    
    // ============================================================================
    // POSITION ANALYSIS
    // ============================================================================
    
    initializePositionAnalysis() {
        const form = document.getElementById('position-analysis-form');
        if (!form) return;
        
        form.addEventListener('submit', (e) => this.handlePositionAnalysis(e));
        
        // Add input validation
        const numberInputs = form.querySelectorAll('input[type="number"]');
        numberInputs.forEach(input => {
            input.addEventListener('input', () => {
                if (input.value && parseFloat(input.value) < 0) {
                    input.setCustomValidity('Value must be positive');
                } else {
                    input.setCustomValidity('');
                }
            });
        });
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
        
        // Validation
        for (const [key, value] of Object.entries(params)) {
            if (isNaN(value) || value <= 0) {
                showError(resultDiv, new Error(`Invalid ${key.replace(/_/g, ' ')}`));
                return;
            }
        }
        
        showLoading(resultDiv, 'Analyzing position... This may take a moment.');
        
        try {
            const result = await this.apiClient.analyzePosition(params);
            this.displayPositionAnalysis(result, resultDiv);
            window.showToast('Position analysis complete!', 'success');
        } catch (error) {
            showError(resultDiv, error);
            window.showToast('Error: ' + error.message, 'error');
        }
    }
    
    displayPositionAnalysis(result, container) {
        if (!container) return;
        
        const netPnLColor = result.net_pnl_usd >= 0 ? '#10b981' : '#ef4444';
        const netPnLIcon = result.net_pnl_usd >= 0 ? '📈' : '📉';
        const recommendationColor = result.recommendation.toLowerCase().includes('good') ? '#10b981' : 
                                    result.recommendation.toLowerCase().includes('consider') ? '#f59e0b' : '#ef4444';
        
        container.innerHTML = `
            <div class="result-card" style="margin-top: 20px;">
                <h3 style="color: #1f2937; margin-bottom: 20px; font-size: 1.5em;">
                    📊 Position Analysis Results
                </h3>
                
                <!-- Summary Card -->
                <div style="background: linear-gradient(135deg, ${netPnLColor}15 0%, ${netPnLColor}05 100%); 
                            padding: 20px; border-radius: 12px; margin-bottom: 20px; 
                            border: 2px solid ${netPnLColor};">
                    <div style="text-align: center;">
                        <div style="font-size: 0.9em; color: #6b7280; margin-bottom: 10px;">Net Profit/Loss</div>
                        <div style="font-size: 2.5em; font-weight: bold; color: ${netPnLColor}; margin-bottom: 10px;">
                            ${netPnLIcon} ${formatCurrency(result.net_pnl_usd)}
                        </div>
                        <div style="font-size: 1em; color: #6b7280;">
                            Return: ${formatPercent((result.net_pnl_usd / result.initial_value_usd) * 100)}
                        </div>
                    </div>
                </div>
                
                <!-- Three Column Layout -->
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; margin-bottom: 20px;">
                    
                    <!-- Current Position -->
                    <div class="analysis-section" style="background: #f9fafb; padding: 20px; border-radius: 8px; border-left: 4px solid #3b82f6;">
                        <h4 style="color: #3b82f6; margin: 0 0 15px 0; display: flex; align-items: center; gap: 8px;">
                            💰 Current Position
                        </h4>
                        <div style="display: flex; flex-direction: column; gap: 10px;">
                            <div>
                                <div style="color: #6b7280; font-size: 0.85em;">Token A</div>
                                <div style="font-weight: bold; font-size: 1.1em;">${formatNumber(result.current_position.token_a, 4)}</div>
                            </div>
                            <div>
                                <div style="color: #6b7280; font-size: 0.85em;">Token B</div>
                                <div style="font-weight: bold; font-size: 1.1em;">${formatNumber(result.current_position.token_b, 4)}</div>
                            </div>
                            <div style="padding-top: 10px; border-top: 1px solid #e5e7eb;">
                                <div style="color: #6b7280; font-size: 0.85em;">Total Value</div>
                                <div style="font-weight: bold; font-size: 1.2em; color: #3b82f6;">${formatCurrency(result.current_position.value_usd)}</div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Performance Metrics -->
                    <div class="analysis-section" style="background: #f9fafb; padding: 20px; border-radius: 8px; border-left: 4px solid #8b5cf6;">
                        <h4 style="color: #8b5cf6; margin: 0 0 15px 0; display: flex; align-items: center; gap: 8px;">
                            📈 Performance
                        </h4>
                        <div style="display: flex; flex-direction: column; gap: 10px;">
                            <div>
                                <div style="color: #6b7280; font-size: 0.85em;">Impermanent Loss</div>
                                <div style="font-weight: bold; font-size: 1.1em; color: ${this.getILColor(result.il_percentage)};">
                                    ${formatPercent(result.il_percentage)}
                                </div>
                            </div>
                            <div>
                                <div style="color: #6b7280; font-size: 0.85em;">Fee Income</div>
                                <div style="font-weight: bold; font-size: 1.1em; color: #10b981;">
                                    +${formatCurrency(result.fee_income_usd)}
                                </div>
                            </div>
                            <div style="padding-top: 10px; border-top: 1px solid #e5e7eb;">
                                <div style="color: #6b7280; font-size: 0.85em;">HODL Comparison</div>
                                <div style="font-weight: bold; font-size: 1.1em;">
                                    ${formatCurrency(result.hodl_value_usd)}
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Pool Quality -->
                    <div class="analysis-section" style="background: #f9fafb; padding: 20px; border-radius: 8px; border-left: 4px solid #f59e0b;">
                        <h4 style="color: #f59e0b; margin: 0 0 15px 0; display: flex; align-items: center; gap: 8px;">
                            ⭐ Pool Quality
                        </h4>
                        <div style="display: flex; flex-direction: column; gap: 10px;">
                            <div>
                                <div style="color: #6b7280; font-size: 0.85em;">Quality Score</div>
                                <div style="font-weight: bold; font-size: 1.3em; color: #f59e0b;">
                                    ${formatNumber(result.pool_quality_score, 1)}/100
                                </div>
                                <div style="background: #e5e7eb; height: 8px; border-radius: 4px; margin-top: 5px; overflow: hidden;">
                                    <div style="background: #f59e0b; height: 100%; width: ${result.pool_quality_score}%; transition: width 0.3s;"></div>
                                </div>
                            </div>
                            <div>
                                <div style="color: #6b7280; font-size: 0.85em;">Daily Turnover</div>
                                <div style="font-weight: bold; font-size: 1.1em;">${formatPercent(result.daily_turnover_rate)}</div>
                            </div>
                            <div>
                                <div style="color: #6b7280; font-size: 0.85em;">Break-Even</div>
                                <div style="font-weight: bold; font-size: 1.1em;">
                                    ${result.days_to_breakeven === 'infinite' ? '∞ days' : formatNumber(result.days_to_breakeven, 1) + ' days'}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Recommendation -->
                <div style="background: linear-gradient(135deg, ${recommendationColor}15 0%, ${recommendationColor}05 100%); 
                            padding: 20px; border-radius: 12px; border: 2px solid ${recommendationColor};">
                    <h4 style="color: ${recommendationColor}; margin: 0 0 10px 0; display: flex; align-items: center; gap: 8px;">
                        💡 Recommendation
                    </h4>
                    <p style="margin: 0; line-height: 1.6; color: #1f2937; font-size: 1.05em;">
                        ${result.recommendation}
                    </p>
                </div>
                
                <!-- Detailed Breakdown (Collapsible) -->
                <details style="margin-top: 20px; background: #f9fafb; padding: 15px; border-radius: 8px;">
                    <summary style="cursor: pointer; font-weight: bold; color: #4b5563; user-select: none;">
                        📋 View Detailed Breakdown
                    </summary>
                    <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #e5e7eb;">
                        <pre style="background: #1f2937; color: #f9fafb; padding: 15px; border-radius: 8px; overflow-x: auto; font-size: 0.85em;">${JSON.stringify(result, null, 2)}</pre>
                    </div>
                </details>
            </div>
        `;
        
        container.style.display = 'block';
    }
    
    // ============================================================================
    // URL PARAMETERS & EXAMPLES
    // ============================================================================
    
    loadURLParameters() {
        const urlParams = new URLSearchParams(window.location.search);
        
        if (urlParams.get('example') === 'true') {
            this.loadExampleData();
        }
    }
    
    loadExampleData() {
        const form = document.getElementById('position-analysis-form');
        if (!form) return;
        
        // ETH/USDC pool example
        form.initial_token_a.value = '10';
        form.initial_token_b.value = '20000';
        form.initial_price.value = '2000';
        form.current_price.value = '2400';
        form.daily_volume_usd.value = '500000';
        form.pool_tvl_usd.value = '10000000';
        form.days_elapsed.value = '30';
        form.fee_rate.value = '0.003';
        
        window.showToast('Example data loaded! (ETH/USDC pool)', 'success');
        
        // Scroll to form
        form.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

// Initialize DeFi Demo when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('quick-il-form') || document.getElementById('position-analysis-form')) {
        window.defiDemo = new DeFiDemo();
        console.log('✅ DeFi Demo initialized');
    }
});
