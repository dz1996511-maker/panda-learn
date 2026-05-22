// AI 学习助手 — 前端脚本
// HTMX handles most interactivity; this file is for minimal enhancements.

document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide flash messages after 5 seconds
    document.querySelectorAll('[data-auto-hide]').forEach(function(el) {
        setTimeout(function() {
            el.style.transition = 'opacity 0.5s';
            el.style.opacity = '0';
            setTimeout(function() { el.remove(); }, 500);
        }, 5000);
    });
});
