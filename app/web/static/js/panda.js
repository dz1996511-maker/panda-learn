/**
 * 🐼 像素熊猫学习伴侣
 */

const PandaMessages = {
    home: [
        "欢迎回来！像素熊猫在等你！",
        "今天要学什么？我准备好了！",
        "一起加油吧！",
    ],
    knowledge: [
        "导入资料，我来帮你消化！",
        "知识就是力量！",
        "又学到新东西了呢！",
    ],
    learning: [
        "专心学习的样子很酷！",
        "慢慢来，理解比速度重要！",
        "你已经比昨天更厉害了！",
    ],
    practice: [
        "做题巩固知识！加油！",
        "错了也没关系，继续前进！",
        "你可以的！",
    ],
    analysis: [
        "数据会告诉你哪里需要加强！",
        "进步看得见！",
    ],
    encouragement: [
        "你今天学得很棒！",
        "保持节奏！",
        "每一步都在进步！",
        "相信自己！",
        "像素熊猫为你打气！",
        "学习使我快乐！",
    ],
};

function getMessagesForPage() {
    const p = window.location.pathname;
    if (p === '/' || p === '') return PandaMessages.home;
    if (p.startsWith('/knowledge')) return PandaMessages.knowledge;
    if (p.startsWith('/learning')) return PandaMessages.learning;
    if (p.startsWith('/practice')) return PandaMessages.practice;
    if (p.startsWith('/analysis')) return PandaMessages.analysis;
    return PandaMessages.encouragement;
}

function randomMessage() {
    const msgs = getMessagesForPage();
    return msgs[Math.floor(Math.random() * msgs.length)];
}

function randomEncouragement() {
    return PandaMessages.encouragement[Math.floor(Math.random() * PandaMessages.encouragement.length)];
}

function updateSpeech(text) {
    const bubble = document.getElementById('panda-speech');
    if (bubble) {
        bubble.textContent = text;
        bubble.classList.remove('panda-talk');
        void bubble.offsetWidth;
        bubble.classList.add('panda-talk');
    }
}

function bouncePanda(element) {
    if (!element) return;
    element.style.transition = 'transform 0.1s';
    element.style.transform = 'translateY(-6px)';
    setTimeout(() => {
        element.style.transform = 'translateY(0)';
    }, 120);
}

function onPandaClick(e) {
    updateSpeech(randomEncouragement());
    const target = e.currentTarget;
    bouncePanda(target.querySelector('canvas') || target);
}

function initPanda() {
    // 初始问候
    setTimeout(() => updateSpeech('你好！我是像素熊猫！'), 500);

    // 每 25 秒换消息
    setInterval(() => updateSpeech(randomMessage()), 25000);

    // 点击右下角熊猫
    const companion = document.getElementById('panda-companion');
    if (companion) companion.addEventListener('click', onPandaClick);

    // 点击侧边栏熊猫
    const sidebar = document.getElementById('sidebar-panda');
    if (sidebar) sidebar.addEventListener('click', onPandaClick);

    // 页面切换回来时问候
    document.addEventListener('visibilitychange', () => {
        if (!document.hidden) {
            setTimeout(() => updateSpeech('你回来啦！继续加油！'), 500);
        }
    });
}

document.addEventListener('DOMContentLoaded', initPanda);
