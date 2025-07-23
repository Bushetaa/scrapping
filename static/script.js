// Dashboard JavaScript functionality
let refreshInterval;
let lastUpdateTime = null;

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', function() {
    refreshData();
    startAutoRefresh();
    
    // Add refresh indicator
    const refreshIndicator = document.createElement('div');
    refreshIndicator.className = 'auto-refresh-indicator';
    refreshIndicator.innerHTML = '<i class="fas fa-sync-alt fa-spin"></i> Refreshing...';
    document.body.appendChild(refreshIndicator);
});

// Start automatic refresh every 10 seconds
function startAutoRefresh() {
    refreshInterval = setInterval(refreshData, 10000);
}

// Stop automatic refresh
function stopAutoRefresh() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
    }
}

// Manual refresh function
function refreshData() {
    showRefreshIndicator();
    
    fetch('/api/status')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                updateDashboard(data.data);
                updateSummaryCards(data.data);
                lastUpdateTime = new Date();
                updateLastUpdatedTime();
            } else {
                showError('Failed to load data: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error fetching data:', error);
            showError('Network error occurred while fetching data');
        })
        .finally(() => {
            hideRefreshIndicator();
        });
}

// Update the main status table
function updateDashboard(platforms) {
    const tableBody = document.getElementById('status-table-body');
    
    if (platforms.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="6" class="text-center text-muted">
                    <i class="fas fa-exclamation-circle"></i>
                    No monitoring data available
                </td>
            </tr>
        `;
        return;
    }
    
    tableBody.innerHTML = platforms.map(platform => {
        const statusIcon = getStatusIcon(platform);
        const newPostBadge = platform.has_new_post ? 
            '<span class="badge bg-success new-post-indicator">✅ Yes</span>' : 
            '<span class="badge bg-secondary">⭕ No</span>';
        
        const successRateColor = getSuccessRateColor(platform.success_rate);
        const platformIcon = getPlatformIcon(platform.platform);
        
        return `
            <tr>
                <td>
                    ${platformIcon}
                    <strong>${platform.platform}</strong>
                </td>
                <td>
                    <div class="last-post-preview" title="${escapeHtml(platform.last_post)}">
                        ${escapeHtml(platform.last_post)}
                    </div>
                </td>
                <td>
                    <small class="text-muted">
                        ${formatDateTime(platform.last_checked)}
                    </small>
                </td>
                <td>
                    <div class="d-flex align-items-center">
                        <div class="success-rate-bar me-2" style="width: 60px;">
                            <div class="success-rate-fill" style="width: ${platform.success_rate}%; background-color: ${successRateColor};"></div>
                        </div>
                        <small>${platform.success_rate}%</small>
                    </div>
                    <small class="text-muted">${platform.success_count}/${platform.check_count}</small>
                </td>
                <td>${newPostBadge}</td>
                <td>${statusIcon}</td>
            </tr>
        `;
    }).join('');
}

// Update summary cards at the top
function updateSummaryCards(platforms) {
    const activeMonitoring = platforms.filter(p => p.check_count > 0).length;
    const newPosts = platforms.filter(p => p.has_new_post).length;
    const errors = platforms.filter(p => p.error_message).length;
    
    document.getElementById('active-monitoring').textContent = activeMonitoring;
    document.getElementById('new-posts').textContent = newPosts;
    document.getElementById('error-count').textContent = errors;
}

// Get status icon based on platform status
function getStatusIcon(platform) {
    if (platform.error_message) {
        return `<span class="status-error" title="${escapeHtml(platform.error_message)}">
                    <i class="fas fa-exclamation-circle"></i> Error
                </span>`;
    } else if (platform.check_count === 0) {
        return '<span class="status-warning"><i class="fas fa-clock"></i> Pending</span>';
    } else {
        return '<span class="status-success"><i class="fas fa-check-circle"></i> Active</span>';
    }
}

// Get platform icon
function getPlatformIcon(platform) {
    const icons = {
        'LinkedIn': '<i class="fab fa-linkedin platform-linkedin"></i>',
        'TikTok': '<i class="fab fa-tiktok platform-tiktok"></i>',
        'Facebook': '<i class="fab fa-facebook platform-facebook"></i>',
        'X': '<i class="fab fa-x-twitter platform-x"></i>'
    };
    return icons[platform] || '<i class="fas fa-globe"></i>';
}

// Get success rate color
function getSuccessRateColor(rate) {
    if (rate >= 80) return '#28a745';
    if (rate >= 60) return '#ffc107';
    return '#dc3545';
}

// Format date and time
function formatDateTime(dateString) {
    if (!dateString || dateString === 'Never') {
        return 'Never';
    }
    
    try {
        const date = new Date(dateString);
        return date.toLocaleString('en-US', {
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
    } catch {
        return dateString;
    }
}

// Update last updated time
function updateLastUpdatedTime() {
    const element = document.getElementById('last-updated');
    if (lastUpdateTime) {
        element.textContent = lastUpdateTime.toLocaleTimeString();
    }
}

// Show refresh indicator
function showRefreshIndicator() {
    const indicator = document.querySelector('.auto-refresh-indicator');
    if (indicator) {
        indicator.classList.add('show');
    }
}

// Hide refresh indicator
function hideRefreshIndicator() {
    setTimeout(() => {
        const indicator = document.querySelector('.auto-refresh-indicator');
        if (indicator) {
            indicator.classList.remove('show');
        }
    }, 500);
}

// Show error message
function showError(message) {
    const tableBody = document.getElementById('status-table-body');
    tableBody.innerHTML = `
        <tr>
            <td colspan="6" class="text-center text-danger">
                <i class="fas fa-exclamation-triangle"></i>
                ${escapeHtml(message)}
            </td>
        </tr>
    `;
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Handle page visibility changes to pause/resume refreshing
document.addEventListener('visibilitychange', function() {
    if (document.hidden) {
        stopAutoRefresh();
    } else {
        refreshData();
        startAutoRefresh();
    }
});

// Add keyboard shortcuts
document.addEventListener('keydown', function(event) {
    // Ctrl+R or F5 to refresh
    if ((event.ctrlKey && event.key === 'r') || event.key === 'F5') {
        event.preventDefault();
        refreshData();
    }
});
