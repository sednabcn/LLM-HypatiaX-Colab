// frontend/js/dashboard.js - Dashboard Interface

class Dashboard {
    constructor() {
        this.apiClient = window.apiClient || new APIClient();
        this.initialize();
    }
    
    async initialize() {
        console.log('Initializing Dashboard...');
        await this.loadStats();
        await this.loadRecentActivity();
        this.startAutoRefresh();
    }
    
    async loadStats() {
        try {
            const health = await this.apiClient.healthCheck();
            this.updateStats({
                status: health.status,
                version: health.version,
                models_loaded: health.models_loaded,
                mode: health.mode
            });
        } catch (error) {
            console.error('Failed to load stats:', error);
            this.updateStats({ status: 'offline' });
        }
    }
    
    updateStats(data) {
        // Update status card
        const statusCard = document.getElementById('status-card');
        if (statusCard) {
            statusCard.innerHTML = `
                <h3>System Status</h3>
                <div class="stat-value ${data.status === 'online' ? 'stat-success' : 'stat-error'}">
                    ${data.status === 'online' ? '🟢 Online' : '🔴 Offline'}
                </div>
                ${data.mode ? `<p class="stat-label">Mode: ${data.mode}</p>` : ''}
            `;
        }
        
        // Update version card
        const versionCard = document.getElementById('version-card');
        if (versionCard) {
            versionCard.innerHTML = `
                <h3>Version</h3>
                <div class="stat-value">${data.version || 'Unknown'}</div>
                <p class="stat-label">HypatiaX API</p>
            `;
        }
        
        // Update models card
        const modelsCard = document.getElementById('models-card');
        if (modelsCard) {
            modelsCard.innerHTML = `
                <h3>Models</h3>
                <div class="stat-value ${data.models_loaded ? 'stat-success' : 'stat-warning'}">
                    ${data.models_loaded ? '✅ Loaded' : '⚠️ Demo Mode'}
                </div>
                <p class="stat-label">NER Models Status</p>
            `;
        }
    }
    
    async loadRecentActivity() {
        try {
            const tests = await this.apiClient.runTests();
            this.displayActivity(tests.test_results || []);
        } catch (error) {
            console.error('Failed to load activity:', error);
        }
    }
    
    displayActivity(results) {
        const activityContainer = document.getElementById('recent-activity');
        if (!activityContainer) return;
        
        if (results.length === 0) {
            activityContainer.innerHTML = '<p class="empty-state">No recent activity</p>';
            return;
        }
        
        const html = results.map(result => `
            <div class="activity-item">
                <div class="activity-description">${this.escapeHtml(result.description)}</div>
                <div class="activity-formula">${this.escapeHtml(result.formula)}</div>
                ${result.error ? `<div class="activity-error">${this.escapeHtml(result.error)}</div>` : ''}
            </div>
        `).join('');
        
        activityContainer.innerHTML = html;
    }
    
    startAutoRefresh() {
        // Refresh stats every 30 seconds
        setInterval(() => this.loadStats(), 30000);
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Make Dashboard globally available
window.Dashboard = Dashboard;
