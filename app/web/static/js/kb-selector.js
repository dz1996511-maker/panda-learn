/**
 * 知识库选择器 — 显示所有已上传文件，点击激活
 */

function formatSize(bytes) {
    if (!bytes) return '';
    if (bytes < 1024) return bytes + 'B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + 'KB';
    return (bytes / 1024 / 1024).toFixed(1) + 'MB';
}

function formatTime(iso) {
    if (!iso) return '';
    const d = new Date(iso);
    return d.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
}

function renderKbSelector() {
    const container = document.getElementById('kb-selector-panel');
    if (!container) return;

    const state = KnowledgeStore.getState();
    const files = state.files;
    const activeId = state.activeFileId;

    if (!files || files.length === 0) {
        container.innerHTML = '<div class="kb-empty">暂无文件，去知识库导入</div>';
        return;
    }

    let html = '<div class="kb-file-list">';
    files.forEach(f => {
        const isActive = f.id === activeId;
        html += `
            <div class="kb-file-item ${isActive ? 'active' : ''}" data-id="${f.id}" onclick="KnowledgeStore.setActiveFile('${f.id}')">
                <div class="kb-file-info">
                    <div class="kb-file-name">${f.name}</div>
                    <div class="kb-file-meta">${formatTime(f.timestamp)}${f.fileSize ? ' · ' + formatSize(f.fileSize) : ''}${f.fileType ? ' · ' + f.fileType : ''}</div>
                </div>
                ${isActive ? '<span class="kb-active-tag">当前</span>' : ''}
            </div>
        `;
    });
    html += '</div>';
    container.innerHTML = html;
}

// 在 Store 变化时重新渲染
document.addEventListener('knowledge-store-change', renderKbSelector);
document.addEventListener('DOMContentLoaded', () => {
    // 延迟等 store 同步完再渲染
    setTimeout(renderKbSelector, 100);
});
