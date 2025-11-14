// frontend/js/main.js - Main Application Entry Point

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 HypatiaX Application Initializing...');
    
    // Initialize API client
    if (typeof APIClient !== 'undefined') {
        window.apiClient = new APIClient();
        console.log('✅ API Client initialized');
    }
    
    // Initialize NER Demo if on demo page
    if (document.getElementById('ner-demo-container')) {
        if (typeof NERDemo !== 'undefined') {
            window.nerDemo = new NERDemo();
            console.log('✅ NER Demo initialized');
        }
    }
    
    // Initialize Dashboard if on dashboard page
    if (document.getElementById('dashboard-container')) {
        if (typeof Dashboard !== 'undefined') {
            window.dashboard = new Dashboard();
            console.log('✅ Dashboard initialized');
        }
    }
    
    // Add navigation highlighting
    highlightCurrentPage();
    
    // Add smooth scrolling
    enableSmoothScrolling();
    
    console.log('✨ HypatiaX Application Ready!');
});

/**
 * Highlight current page in navigation
 */
function highlightCurrentPage() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('nav a');
    
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath || 
            (currentPath === '/' && link.getAttribute('href') === 'index.html')) {
            link.classList.add('active');
        }
    });
}

/**
 * Enable smooth scrolling for anchor links
 */
function enableSmoothScrolling() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

/**
 * Utility: Show toast notification
 */
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

// Make utility functions globally available
window.showToast = showToast;
