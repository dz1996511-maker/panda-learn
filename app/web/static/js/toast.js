/**
 * 🍞 Toast 通知系统 — 全局消息提示
 * 使用：showToast('导入成功！', 'success')
 *       showToast('出错了', 'error')
 *       showToast('加载中...', 'loading')
 */

function showToast(message, type, duration) {
    type = type || 'info';
    duration = duration || 3000;

    // 创建容器（若不存在）
    var container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        document.body.appendChild(container);
    }

    // 创建 toast 元素
    var toast = document.createElement('div');
    toast.className = 'toast toast-' + type;
    toast.innerHTML = getToastIcon(type) + '<span class="toast-msg">' + message + '</span>';

    container.appendChild(toast);

    // 触发滑入
    requestAnimationFrame(function() {
        toast.classList.add('toast-visible');
    });

    // 自动移除
    if (type !== 'loading') {
        setTimeout(function() {
            toast.classList.remove('toast-visible');
            toast.classList.add('toast-hiding');
            setTimeout(function() { toast.remove(); }, 300);
        }, duration);
    }

    return toast; // 返回引用用于手动关闭
}

function getToastIcon(type) {
    switch(type) {
        case 'success': return '<span class="toast-icon" style="color:#66bb6a;">✓</span>';
        case 'error':   return '<span class="toast-icon" style="color:#ef5350;">✕</span>';
        case 'loading': return '<span class="toast-icon toast-spin">⟳</span>';
        default:        return '<span class="toast-icon" style="color:#4fc3f7;">i</span>';
    }
}

// 便捷方法
function showSuccess(msg) { return showToast(msg, 'success'); }
function showError(msg)   { return showToast(msg, 'error'); }
function showLoading(msg) { return showToast(msg || '处理中...', 'loading', 999999); }
function hideLoading(toast) {
    if (toast) {
        toast.classList.remove('toast-visible');
        toast.classList.add('toast-hiding');
        setTimeout(function() { toast.remove(); }, 300);
    }
}

// 确认对话框
function showConfirm(msg, onConfirm) {
    var container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        document.body.appendChild(container);
    }

    var el = document.createElement('div');
    el.className = 'toast toast-confirm';
    el.innerHTML =
        '<div class="toast-confirm-body">' +
        '<div class="toast-confirm-msg">' + msg + '</div>' +
        '<div class="toast-confirm-actions">' +
        '<button class="btn btn-sm" onclick="this.closest(\'.toast\').remove()">取消</button>' +
        '<button class="btn btn-sm btn-danger" id="confirm-yes">确定</button>' +
        '</div></div>';

    container.appendChild(el);
    requestAnimationFrame(function() { el.classList.add('toast-visible'); });

    document.getElementById('confirm-yes').onclick = function() {
        el.remove();
        if (onConfirm) onConfirm();
    };
}
