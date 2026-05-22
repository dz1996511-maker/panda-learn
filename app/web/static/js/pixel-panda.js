/**
 * 🐼 像素熊猫 — Canvas 逐像素渲染
 * 每个像素 3x3 物理像素，16x16 逻辑像素 → 48x48 显示
 */

// 颜色表
const C = {
    '.': null,           // 透明
    'B': '#1a1a1a',      // 深色毛
    'W': '#ffffff',      // 白色脸/肚皮
    'E': '#444444',      // 内耳
    'P': '#ffb0b0',      // 腮红
    'D': '#000000',      // 瞳孔
    'G': '#cccccc',      // 眼神光
    'N': '#222222',      // 鼻子
    'M': '#111111',      // 嘴巴/身体
};

// 像素数据 — 16列 x 16行
// 一只坐着的熊猫（头像 + 上半身）
const PANDA = [
    "....BBBBBB....",
    "..BBBBBBBBBB..",
    ".BBBBEEBBEBBB.",
    ".BBWWWWWWWWBB.",
    ".BBWWWWWWWWBB.",
    "BBBBWWWWWWBBBB",
    "BBBBWWDDWWBBBB",
    "BBBBWDDWDWBBBB",
    "BBBBWWWWWWBBBB",
    "BBBNNPPNNNBBBB",
    "BBBBWWWWWWBBBB",
    ".BBBBWWWWBBBB.",
    "..BBBBBBBBBB..",
    "...BBBBBBBB...",
    "..BB....BB....",
    "..BBBBBBBB....",
];

function renderPanda(canvasId, scale) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;

    const px = scale || 3;
    canvas.width = 16 * px;
    canvas.height = 16 * px;

    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    for (let y = 0; y < 16; y++) {
        const row = PANDA[y];
        if (!row) continue;
        for (let x = 0; x < 16; x++) {
            const ch = row[x];
            const color = C[ch];
            if (!color) continue;
            ctx.fillStyle = color;
            ctx.fillRect(x * px, y * px, px, px);
        }
    }
}

// 渲染所有熊猫 canvas
function renderAllPandas() {
    renderPanda('pixel-panda-canvas', 3);
    renderPanda('pixel-panda-mini', 3);
}

// 等待 DOM 加载
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', renderAllPandas);
} else {
    renderAllPandas();
}
