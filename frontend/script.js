const API = "http://localhost:8000/api";
let selectedLvl = "B1";
let player = null;
let currentLang = "RU";

// Словарь текстов
const translations = {
    RU: {
        title: "AI Language Trainer",
        subtitle: "Профессиональный тренажер английского языка.",
        levelLabel: "Выберите уровень",
        topicLabel: "Ситуация (на русском)",
        topicPlaceholder: "Например: Покупка билетов в Лондоне...",
        startBtn: "Начать практику",
        analysisTitle: "Анализ речи",
        analysisDefault: "Жду сообщения...",
        liveLabel: "Live Practice",
        aiStatus: "Собеседник активен",
        inputPlaceholder: "Ответьте по-английски..."
    },
    EN: {
        title: "AI Language Trainer",
        subtitle: "Professional English speaking practice.",
        levelLabel: "Select Level",
        topicLabel: "Scenario (in Russian)",
        topicPlaceholder: "e.g. Buying tickets in London...",
        startBtn: "Start Practice",
        analysisTitle: "Analysis",
        analysisDefault: "Waiting for speech...",
        liveLabel: "Live Practice",
        aiStatus: "AI Partner Active",
        inputPlaceholder: "Reply in English..."
    }
};

// Смена языка
function setLanguage(lang) {
    currentLang = lang;
    const t = translations[lang];
    document.getElementById('ui-title').innerText = t.title;
    document.getElementById('ui-subtitle').innerText = t.subtitle;
    document.getElementById('ui-level-label').innerText = t.levelLabel;
    document.getElementById('ui-topic-label').innerText = t.topicLabel;
    document.getElementById('topic-input').placeholder = t.topicPlaceholder;
    document.getElementById('ui-start-btn-text').innerText = t.startBtn;
    document.getElementById('ui-analysis-title').innerText = t.analysisTitle;
    document.getElementById('analysis-box').innerText = t.analysisDefault;
    document.getElementById('ui-live-label').innerText = t.liveLabel;
    document.getElementById('ui-ai-status').innerText = t.aiStatus;
    document.getElementById('user-input').placeholder = t.inputPlaceholder;
    document.getElementById('lang-ru').classList.toggle('lang-btn-active', lang === 'RU');
    document.getElementById('lang-en').classList.toggle('lang-btn-active', lang === 'EN');
}

function setLevel(lvl, btn) {
    selectedLvl = lvl;
}

// Запуск
async function startDialogue() {
    const topic = document.getElementById('topic-input').value;
    const level = document.getElementById('level-select').value;
    if(!topic) return alert(currentLang === "RU" ? "Введите ситуацию!" : "Enter scenario!");

    const btn = document.getElementById('start-btn');
    const btnText = document.getElementById('ui-start-btn-text');
    btn.disabled = true;
    btnText.innerText = "...";

    try {
        await fetch(`${API}/session/start`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ topic, level })
        });

        const bgRes = await fetch(`${API}/session/background`).then(r => r.json());
        if (bgRes.image) {
            const chatScreen = document.getElementById('chat-screen');
            chatScreen.style.backgroundImage = `url(data:image/jpeg;base64,${bgRes.image})`;
            chatScreen.style.backgroundSize = 'cover';
            chatScreen.style.backgroundPosition = 'center';
        }

        document.getElementById('dashboard').classList.add('hidden');
        document.getElementById('chat-screen').classList.remove('hidden');
        document.getElementById('messages-container').innerHTML = "";

        const initMsg = await fetch(`${API}/chat/init`, { method: 'POST' }).then(r => r.json());
        addMessage(initMsg);
        playAudio(initMsg.audio);

    } catch (e) {
        alert("Server error!");
    } finally {
        btn.disabled = false;
        btnText.innerText = translations[currentLang].startBtn;
    }
}

async function sendMessage() {
    const input = document.getElementById('user-input');
    const text = input.value.trim();
    if (!text) return;
    input.value = "";
    addMessage({ role: 'user', text: text });
    const aiMsg = await fetch(`${API}/chat/message`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ text })
    }).then(r => r.json());
    addMessage(aiMsg);
    if (aiMsg.corrections) document.getElementById('analysis-box').innerText = aiMsg.corrections;
    playAudio(aiMsg.audio);
}

function addMessage(msg) {
    const container = document.getElementById('messages-container');
    const isUser = msg.role === 'user';
    const mId = Math.random().toString(36).substr(2, 9);
    const div = document.createElement('div');
    div.style.display = "flex";
    div.style.justifyContent = isUser ? "flex-end" : "flex-start";
    div.style.width = "100%";
    let content = `<div class="msg-bubble ${isUser ? 'msg-user' : 'msg-ai'}">
            <p id="t-${mId}" class="${!isUser ? 'blur-msg' : ''}">${msg.text}</p>
            <p id="tr-${mId}" class="hidden translation-text">"${msg.translation || ''}"</p>`;
    if (!isUser) {
        content += `<div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(0,0,0,0.05); display: flex; gap: 0.5rem; align-items: center;">
                <button onclick="playAudio('${msg.audio}')" class="control-btn"><i data-lucide="rotate-ccw" style="width: 0.875rem; height: 0.875rem;"></i></button>
                <button onclick="document.getElementById('t-${mId}').classList.toggle('revealed')" class="control-btn"><i data-lucide="eye" style="width: 0.875rem; height: 0.875rem;"></i></button>
                <button onclick="document.getElementById('tr-${mId}').classList.toggle('hidden')" class="control-btn"><i data-lucide="languages" style="width: 0.875rem; height: 0.875rem;"></i></button>
            </div>`;
    }
    content += `</div>`;
    div.innerHTML = content;
    container.appendChild(div);
    lucide.createIcons();
    container.scrollTop = container.scrollHeight;
}

// ПОДСКАЗКИ
let hintsVisible = false;
async function toggleHints() {
    const container = document.getElementById('hints-container');
    const btn = document.getElementById('hint-btn');
    if (hintsVisible) {
        container.classList.add('hidden');
        hintsVisible = false;
        btn.style.background = "white"; btn.style.color = "#94a3b8";
        return;
    }
    btn.innerText = "...";
    try {
        const data = await fetch(`${API}/chat/hints`, { method: 'POST' }).then(r => r.json());
        container.innerHTML = "";
        data.hints.forEach(hint => {
            const d = document.createElement('div');
            d.className = "hint-item"; d.innerText = hint;
            d.onclick = () => { document.getElementById('user-input').value = hint; toggleHints(); };
            container.appendChild(d);
        });
        container.classList.remove('hidden');
        hintsVisible = true;
        btn.innerHTML = '<i data-lucide="x" style="width: 1.5rem; height: 1.5rem;"></i>';
        lucide.createIcons();
        btn.style.background = "var(--primary)"; btn.style.color = "white";
    } catch (e) { alert("Unavailable"); }
}

function playAudio(base64) {
    if (!base64 || base64.length < 500) return;
    if (player) player.pause();
    const blob = new Blob([Uint8Array.from(atob(base64), c => c.charCodeAt(0))], { type: 'audio/wav' });
    player = new Audio(URL.createObjectURL(blob));
    const dot = document.getElementById('status-dot');
    player.onplay = () => { dot.style.background = "#22c55e"; dot.classList.add('animate-pulse'); };
    player.onended = () => { dot.style.background = "#cbd5e1"; dot.classList.remove('animate-pulse'); };
    player.play();
}

const micBtn = document.getElementById('mic-btn');
const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
if (SR) {
    const recognition = new SR();
    recognition.lang = 'en-US';
    micBtn.onmousedown = () => { recognition.start(); micBtn.classList.add('mic-btn-active'); document.getElementById('recording-visual').classList.remove('hidden'); };
    micBtn.onmouseup = () => { recognition.stop(); micBtn.classList.remove('mic-btn-active'); document.getElementById('recording-visual').classList.add('hidden'); };
    recognition.onresult = (event) => { document.getElementById('user-input').value = event.results[0][0].transcript; };
}

function resetToDashboard() { location.reload(); }
lucide.createIcons();
