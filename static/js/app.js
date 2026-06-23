// 家庭记事本 - 前端交互脚本

document.addEventListener('DOMContentLoaded', function() {
    // 初始化工具提示
    initTooltips();

    // 初始化表单验证
    initFormValidation();
});

/**
 * 初始化工具提示
 */
function initTooltips() {
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    tooltipElements.forEach(el => {
        el.addEventListener('mouseenter', showTooltip);
        el.addEventListener('mouseleave', hideTooltip);
    });
}

function showTooltip(e) {
    const text = e.target.getAttribute('data-tooltip');
    const tooltip = document.createElement('div');
    tooltip.className = 'tooltip';
    tooltip.textContent = text;
    document.body.appendChild(tooltip);

    const rect = e.target.getBoundingClientRect();
    tooltip.style.left = rect.left + rect.width / 2 - tooltip.offsetWidth / 2 + 'px';
    tooltip.style.top = rect.top - tooltip.offsetHeight - 10 + 'px';
}

function hideTooltip() {
    const tooltip = document.querySelector('.tooltip');
    if (tooltip) {
        tooltip.remove();
    }
}

/**
 * 初始化表单验证
 */
function initFormValidation() {
    const forms = document.querySelectorAll('.member-form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const nameInput = form.querySelector('#name');
            if (nameInput && !nameInput.value.trim()) {
                e.preventDefault();
                showNotification('请输入姓名', 'error');
                nameInput.focus();
            }
        });
    });
}

/**
 * 显示通知
 */
function showNotification(message, type = 'info') {
    // 移除现有通知
    const existing = document.querySelector('.notification');
    if (existing) {
        existing.remove();
    }

    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <span class="notification-icon">${type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️'}</span>
        <span class="notification-text">${message}</span>
    `;

    document.body.appendChild(notification);

    // 动画进入
    requestAnimationFrame(() => {
        notification.classList.add('show');
    });

    // 自动消失
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

/**
 * 展开/收起长文本
 */
function toggleText(element) {
    element.classList.toggle('expanded');
    const btn = element.querySelector('.toggle-btn');
    if (btn) {
        btn.textContent = element.classList.contains('expanded') ? '收起' : '展开';
    }
}

// 添加CSS动画样式
const style = document.createElement('style');
style.textContent = `
    .notification {
        position: fixed;
        top: 20px;
        right: 20px;
        background: white;
        padding: 15px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
        display: flex;
        align-items: center;
        gap: 10px;
        z-index: 1000;
        transform: translateX(400px);
        transition: transform 0.3s ease;
    }

    .notification.show {
        transform: translateX(0);
    }

    .notification-success {
        border-left: 4px solid #66BB6A;
    }

    .notification-error {
        border-left: 4px solid #EF5350;
    }

    .tooltip {
        position: fixed;
        background: rgba(0, 0, 0, 0.8);
        color: white;
        padding: 8px 12px;
        border-radius: 6px;
        font-size: 0.85rem;
        z-index: 1000;
        pointer-events: none;
    }
`;
document.head.appendChild(style);
