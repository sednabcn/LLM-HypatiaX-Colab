/**
 * HypatiaX Main Application
 * Handles the Formula Mapper functionality on index.html
 * File: frontend/js/main.js
 */

document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 HypatiaX Application Initializing...');

    // Initialize API client (already done in api-client.js)
    const apiClient = window.apiClient;

    // Check API status
    checkAPIStatus();

    // Initialize Formula Form
    initializeFormulaForm();

    // Initialize Test Button
    initializeTestButton();

    // Add navigation highlighting
    highlightCurrentPage();

    console.log('✨ HypatiaX Application Ready!');
});

// ============================================================================
// API STATUS
// ============================================================================

async function checkAPIStatus() {
    const statusEl = document.getElementById('api-status');
    const demoWarning = document.getElementById('demo-warning');

    if (!statusEl) return;

    try {
        const health = await window.apiClient.healthCheck();
        statusEl.innerHTML = `✅ Backend Online - ${health.mode || 'production'} mode`;
        statusEl.className = 'api-status online';

        if (health.mode === 'demo' && demoWarning) {
            demoWarning.innerHTML = `
                <div class="warning-message">
                    ⚠️ Running in DEMO mode - NER models not loaded
                </div>
            `;
        }
    } catch (error) {
        statusEl.innerHTML = '❌ Backend Offline - Cannot connect to server';
        statusEl.className = 'api-status offline';

        if (demoWarning) {
            demoWarning.innerHTML = `
                <div class="error-message">
                    Backend server is not running. Please start the Flask server.
                </div>
            `;
        }
    }
}

// ============================================================================
// FORMULA FORM
// ============================================================================

function initializeFormulaForm() {
    const form = document.getElementById('formula-form');
    const resultDiv = document.getElementById('formula-result');
    const descriptionInput = document.getElementById('description-input');
    const methodSelect = document.getElementById('method-select');
    const quickSuggestion = document.getElementById('quick-suggestion');

    if (!form) return;

    // Handle form submission
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const description = descriptionInput.value.trim();
        const method = methodSelect.value;

        if (!description) {
            window.showToast('Please enter a description', 'error');
            return;
        }

        showLoading(resultDiv, 'Generating formula...');

        try {
            const result = await window.apiClient.mapDescription(description, method);
            displayFormulaResult(result, resultDiv);
            window.showToast('Formula generated successfully!', 'success');
        } catch (error) {
            showError(resultDiv, error);
            window.showToast('Error: ' + error.message, 'error');
        }
    });

    // Handle example query buttons
    document.querySelectorAll('.example-query-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            descriptionInput.value = btn.dataset.query;
            descriptionInput.focus();
        });
    });

    // Add quick suggestion on input
    if (descriptionInput && quickSuggestion) {
        descriptionInput.addEventListener('input', debounce(() => {
            const value = descriptionInput.value.trim().toLowerCase();
            if (value.length > 5) {
                if (value.includes('total') || value.includes('sum')) {
                    quickSuggestion.innerHTML = '💡 Suggestion: Use SUM() for totals';
                } else if (value.includes('average') || value.includes('mean')) {
                    quickSuggestion.innerHTML = '💡 Suggestion: Use AVG() for averages';
                } else if (value.includes('count')) {
                    quickSuggestion.innerHTML = '💡 Suggestion: Use COUNT() to count records';
                } else {
                    quickSuggestion.innerHTML = '';
                }
            } else {
                quickSuggestion.innerHTML = '';
            }
        }, 300));
    }
}

function displayFormulaResult(result, container) {
    if (!container) return;

    let html = `
        <div class="result-card">
            <h3>Generated Formula</h3>
            <div class="formula-output" style="font-size: 1.2em; padding: 15px; background: #f3f4f6; border-radius: 8px; font-family: monospace;">
                ${escapeHtml(result.formula)}
            </div>

            <div class="result-meta" style="display: flex; gap: 20px; margin-top: 15px; color: #6b7280;">
                <span>Confidence: <strong>${(result.confidence * 100).toFixed(0)}%</strong></span>
                <span>Method: <strong>${result.method}</strong></span>
                <span>Time: <strong>${result.processing_time_ms}ms</strong></span>
            </div>
    `;

    if (result.entities && result.entities.length > 0) {
        html += `
            <div style="margin-top: 20px;">
                <h4>Detected Entities</h4>
                <div class="entities-list" style="display: flex; flex-wrap: wrap; gap: 10px; margin-top: 10px;">
                    ${result.entities.map(e => `
                        <span class="entity" style="padding: 5px 10px; background: #e0e7ff; border-radius: 4px; font-size: 0.9em;">
                            <strong>${escapeHtml(e.text)}</strong> <small>(${e.label})</small>
                        </span>
                    `).join('')}
                </div>
            </div>
        `;
    }

    html += '</div>';

    container.innerHTML = html;
    container.style.display = 'block';
}

// ============================================================================
// TEST BUTTON
// ============================================================================

function initializeTestButton() {
    const testBtn = document.getElementById('test-hypatiax-btn');
    const testResults = document.getElementById('test-results');

    if (!testBtn) return;

    testBtn.addEventListener('click', async () => {
        showLoading(testResults, 'Running tests...');

        try {
            const result = await window.apiClient.runTests();
            displayTestResults(result, testResults);
            window.showToast('Tests completed!', 'success');
        } catch (error) {
            showError(testResults, error);
            window.showToast('Test failed: ' + error.message, 'error');
        }
    });
}

function displayTestResults(result, container) {
    if (!container) return;

    const passed = result.test_results.filter(t => t.status === 'pass').length;
    const failed = result.test_results.filter(t => t.status === 'fail').length;

    let html = `
        <div class="result-card">
            <h3>Test Results</h3>
            <p>Passed: <strong style="color: #10b981;">${passed}</strong> | Failed: <strong style="color: #ef4444;">${failed}</strong></p>

            <div style="margin-top: 20px;">
                ${result.test_results.map(test => `
                    <div style="padding: 10px; margin: 10px 0; background: ${test.status === 'pass' ? '#d1fae5' : '#fee2e2'}; border-radius: 4px;">
                        <div><strong>Query:</strong> ${escapeHtml(test.description)}</div>
                        <div><strong>Formula:</strong> ${escapeHtml(test.formula)}</div>
                        ${test.error ? `<div style="color: #dc2626;"><strong>Error:</strong> ${escapeHtml(test.error)}</div>` : ''}
                    </div>
                `).join('')}
            </div>
        </div>
    `;

    container.innerHTML = html;
    container.style.display = 'block';
}

// ============================================================================
// UTILITIES
// ============================================================================

function highlightCurrentPage() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-menu a');

    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href === currentPath ||
            (currentPath.endsWith('/') && href === 'index.html') ||
            (currentPath.endsWith('index.html') && href === 'index.html')) {
            link.classList.add('active');
        }
    });
}

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        background: ${type === 'error' ? '#ef4444' : type === 'success' ? '#10b981' : '#3b82f6'};
        color: white;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        z-index: 10000;
        animation: slideIn 0.3s ease-out;
    `;

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease-in';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

window.showToast = showToast;
