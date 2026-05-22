/**
 * 🎨 像素图标集 — Canvas 逐像素渲染
 * 每个图标 10x10 逻辑像素，3x 缩放 = 30x30 显示
 */

const IconColors = {
    '.': null,
    'W': '#ffffff',
    'B': '#1a1a1a',
    'G': '#888888',
    'L': '#aaaaaa',
    'A': '#4fc3f7',
    'D': '#666666',
    'E': '#eeeeee',
};

// 图标定义 — 10x10 像素网格
const ICONS = {
    home: [
        "...WWWW...",
        "..WWWWWW..",
        ".WWWWWWWW.",
        "WWWWWWWWWW",
        "WWW....WWW",
        "WWW....WWW",
        "WWW....WWW",
        "WWW....WWW",
        "WWWWWWWWWW",
        "WWWWWWWWWW",
    ],
    knowledge: [
        ".GGGGGGGG.",
        "GG......GG",
        "GG......GG",
        "GG......GG",
        "GGGGGGGGGG",
        "GG......GG",
        "GG......GG",
        "GG......GG",
        "GGGGGGGGGG",
        "GG........",
    ],
    learning: [
        "..WWWWWW..",
        ".WWWWWWWW.",
        "WW......WW",
        "WW......WW",
        "WW..AA..WW",
        ".WW.AA.WW.",
        "..W.AA.W..",
        "...WWWW...",
        "..WW..WW..",
        "..WWWWWW..",
    ],
    practice: [
        ".....WW...",
        "....WWWW..",
        "...WW.GG..",
        "..WW..GG..",
        ".WW...GG..",
        "WW....GG..",
        "WW...GG...",
        ".WW.GG....",
        "..WWW.....",
        "..WW......",
    ],
    analysis: [
        "GG......GG",
        "GG......GG",
        "GG......GG",
        "GG......GG",
        "GG......GG",
        "GGGGGGGGGG",
        ".GG....GG.",
        ".GG....GG.",
        "..GGGGGG..",
        "..GGGGGG..",
    ],
    settings: [
        "...WWWW...",
        "..WW..WW..",
        ".WWGGGGWW.",
        ".WWGGGGWW.",
        ".WWGGGGWW.",
        "..WW..WW..",
        "...WWWW...",
        "..W....W..",
        ".WW....WW.",
        "..........",
    ],
    panda_small: [
        "....BBBB....",
        "...BBBBBB...",
        "..BBEEBBBB..",
        "..BWWWWWB...",
        "BBBBWWWWBB..",
        "BBBBWWDWBB..",
        "BBBNNPPNBBB.",
        ".BBBBBBBB...",
        "..BB..BB....",
        "..BBBBBB....",
    ],
    book_open: [
        ".GGGGGGG...",
        "GG....GG...",
        "GG....GG...",
        "GG....GG...",
        "GGGGGGGG...",
        "GG....GG...",
        "GG....GG...",
        "GG....GG...",
        "GGGGGGGG...",
        "GG.........",
    ],
    star: [
        "....A.....",
        "...AAA....",
        "..AAAAA...",
        ".AAAAAAA..",
        "AAAAAAAAA.",
        "..AAAAA...",
        ".AAAAAAA..",
        "AAAA.AAAAA",
        "AA.....AA.",
        "..........",
    ],
};

function renderIcon(canvasId, iconName) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;

    const data = ICONS[iconName];
    if (!data) return;

    // 从 canvas 属性尺寸计算像素放大倍数
    const px = Math.floor(canvas.width / 10) || 3;

    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    for (let y = 0; y < 10; y++) {
        const row = data[y];
        if (!row) continue;
        for (let x = 0; x < 10; x++) {
            const ch = row[x];
            const color = IconColors[ch];
            if (!color) continue;
            ctx.fillStyle = color;
            ctx.fillRect(x * px, y * px, px, px);
        }
    }
}

// 批量渲染所有 [data-icon] canvas
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('canvas[data-icon]').forEach(c => {
        renderIcon(c.id, c.getAttribute('data-icon'));
    });
});
