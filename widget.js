(function() {
    // ====== CONFIG ======
    const API_URL = "https://metroglass-chatbot-production.up.railway.app";

    // ====== CSS ======
    const css = `
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    #septo-widget { position:fixed; bottom:24px; right:24px; z-index:999999; font-family:'Inter',-apple-system,sans-serif; }

    #septo-btn {
        width:64px; height:64px; border-radius:50%;
        background:linear-gradient(135deg,#0f4c75,#3282b8); border:none; cursor:pointer;
        box-shadow:0 6px 24px rgba(15,76,117,0.35); display:flex; align-items:center;
        justify-content:center; transition:all .3s cubic-bezier(.4,0,.2,1); position:relative;
    }
    #septo-btn:hover { transform:scale(1.08); box-shadow:0 8px 32px rgba(15,76,117,0.45); }
    #septo-btn::before {
        content:''; position:absolute; width:64px; height:64px; border-radius:50%;
        background:#3282b8; animation:septoPulse 2.5s ease-out infinite; z-index:-1;
    }
    #septo-btn.open::before { animation:none; }
    @keyframes septoPulse { 0%{transform:scale(1);opacity:.4} 100%{transform:scale(1.6);opacity:0} }

    #septo-btn .chat-icon, #septo-btn .close-icon { transition:all .3s ease; }
    #septo-btn .close-icon { position:absolute; opacity:0; transform:rotate(-90deg) scale(0); }
    #septo-btn.open .chat-icon { opacity:0; transform:rotate(90deg) scale(0); }
    #septo-btn.open .close-icon { opacity:1; transform:rotate(0) scale(1); }

    .septo-badge {
        position:absolute; top:-2px; right:-2px; width:20px; height:20px;
        background:#ef4444; border-radius:50%; border:2px solid #fff;
        font-size:11px; color:#fff; display:flex; align-items:center;
        justify-content:center; font-weight:600;
    }
    #septo-btn.open .septo-badge { display:none; }

    #septo-panel {
        position:absolute; bottom:80px; right:0; width:400px; height:580px;
        background:#fff; border-radius:16px; box-shadow:0 12px 40px rgba(15,76,117,0.18);
        display:flex; flex-direction:column; overflow:hidden;
        opacity:0; transform:translateY(20px) scale(.95); pointer-events:none;
        transition:all .35s cubic-bezier(.4,0,.2,1); transform-origin:bottom right;
    }
    #septo-panel.visible { opacity:1; transform:translateY(0) scale(1); pointer-events:all; }

    .septo-header {
        background:linear-gradient(135deg,#0b3954,#0f4c75 50%,#3282b8);
        color:#fff; padding:18px 20px; display:flex; align-items:center; gap:14px; flex-shrink:0;
    }
    .septo-avatar {
        width:44px; height:44px; background:rgba(255,255,255,.15); border-radius:12px;
        display:flex; align-items:center; justify-content:center; font-size:22px;
        flex-shrink:0; backdrop-filter:blur(8px);
    }
    .septo-header h3 { font-size:15px; font-weight:600; margin:0; letter-spacing:-.01em; }
    .septo-header p { font-size:12px; opacity:.8; margin:2px 0 0; }
    .septo-online { display:inline-flex; align-items:center; gap:5px; }
    .septo-online::before {
        content:''; width:7px; height:7px; background:#34d399; border-radius:50%;
        display:inline-block; animation:septoBlink 2s ease infinite;
    }
    @keyframes septoBlink { 0%,100%{opacity:1} 50%{opacity:.4} }

    .septo-msgs {
        flex:1; padding:16px; overflow-y:auto; display:flex; flex-direction:column;
        gap:8px; background:#f8f9fb;
    }
    .septo-msgs::-webkit-scrollbar { width:4px; }
    .septo-msgs::-webkit-scrollbar-thumb { background:#cbd5e1; border-radius:4px; }

    .septo-msg {
        max-width:82%; padding:11px 15px; font-size:13.5px; line-height:1.55;
        border-radius:14px; animation:septoMsgIn .3s cubic-bezier(.4,0,.2,1) forwards;
        opacity:0; white-space:pre-wrap; word-wrap:break-word;
    }
    @keyframes septoMsgIn { from{opacity:0;transform:translateY(8px)} to{opacity:1;transform:translateY(0)} }

    .septo-msg.bot {
        background:#fff; color:#1a2332; align-self:flex-start;
        border:1px solid #e2e8f0; border-bottom-left-radius:4px;
        box-shadow:0 1px 3px rgba(0,0,0,.04);
    }
    .septo-msg.user {
        background:linear-gradient(135deg,#0f4c75,#3282b8); color:#fff;
        align-self:flex-end; border-bottom-right-radius:4px;
        box-shadow:0 2px 8px rgba(15,76,117,.2);
    }

    .septo-typing {
        display:flex; align-items:center; gap:5px; padding:12px 18px;
        background:#fff; border:1px solid #e2e8f0; border-radius:14px;
        border-bottom-left-radius:4px; align-self:flex-start;
        animation:septoMsgIn .3s ease forwards;
    }
    .septo-typing span {
        width:7px; height:7px; background:#94a3b8; border-radius:50%;
        animation:septoBounce 1.4s ease-in-out infinite;
    }
    .septo-typing span:nth-child(2){animation-delay:.2s}
    .septo-typing span:nth-child(3){animation-delay:.4s}
    @keyframes septoBounce { 0%,60%,100%{transform:translateY(0)} 30%{transform:translateY(-6px)} }

    .septo-quick {
        display:flex; gap:6px; flex-wrap:wrap; align-self:flex-start;
        animation:septoMsgIn .4s ease forwards; opacity:0; animation-delay:.5s;
    }
    .septo-quick button {
        padding:7px 14px; border:1.5px solid #3282b8; background:#fff; color:#0f4c75;
        border-radius:20px; font-size:12.5px; font-weight:500; cursor:pointer;
        transition:all .2s ease; font-family:inherit;
    }
    .septo-quick button:hover { background:#0f4c75; color:#fff; transform:translateY(-1px); }

    .septo-input {
        padding:14px 16px; border-top:1px solid #e2e8f0; display:flex;
        gap:10px; align-items:center; background:#fff; flex-shrink:0;
    }
    .septo-input input {
        flex:1; padding:11px 16px; border:1.5px solid #e2e8f0; border-radius:24px;
        font-size:13.5px; font-family:inherit; outline:none; transition:border .2s,box-shadow .2s;
        color:#1a2332; background:#fff;
    }
    .septo-input input:focus { border-color:#3282b8; box-shadow:0 0 0 3px rgba(50,130,184,.1); }
    .septo-input input::placeholder { color:#a0aec0; }

    .septo-send {
        width:42px; height:42px; border-radius:50%;
        background:linear-gradient(135deg,#0f4c75,#3282b8); border:none; cursor:pointer;
        display:flex; align-items:center; justify-content:center;
        transition:all .2s ease; flex-shrink:0;
    }
    .septo-send:hover { transform:scale(1.06); box-shadow:0 4px 12px rgba(15,76,117,.3); }
    .septo-send:disabled { opacity:.5; cursor:not-allowed; transform:none; }

    .septo-footer {
        padding:8px; text-align:center; font-size:10.5px; color:#94a3b8;
        background:#fff; flex-shrink:0;
    }

    @media(max-width:480px){
        #septo-panel { width:calc(100vw - 16px); height:calc(100vh - 100px);
        bottom:76px; right:-16px; border-radius:16px 16px 0 0; }
    }
    `;

    // ====== HTML ======
    const html = `
    <div id="septo-panel">
        <div class="septo-header">
            <div class="septo-avatar">🪟</div>
            <div>
                <h3>SEPTO — METROGLASS</h3>
                <p class="septo-online">Online acum</p>
            </div>
        </div>
        <div class="septo-msgs" id="septo-msgs">
            <div class="septo-msg bot">Bună ziua! Sunt SEPTO, asistentul virtual METROGLASS. 👋\n\nVă pot ajuta să estimați rapid prețul pentru ferestre sau uși din PVC.\n\nCe vă interesează?</div>
            <div class="septo-quick" id="septo-quick">
                <button onclick="window._septo.sendQuick('Vreau preț pentru o fereastră')">🪟 Fereastră</button>
                <button onclick="window._septo.sendQuick('Vreau preț pentru o ușă')">🚪 Ușă</button>
                <button onclick="window._septo.sendQuick('Vreau o ofertă completă')">🏠 Ofertă completă</button>
                <button onclick="window._septo.sendQuick('Ce profile recomandați?')">💡 Recomandare</button>
            </div>
        </div>
        <div class="septo-input">
            <input type="text" id="septo-input" placeholder="Scrieți mesajul..." onkeypress="if(event.key==='Enter') window._septo.send()">
            <button class="septo-send" onclick="window._septo.send()" id="septo-send-btn">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M22 2L11 13" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M22 2L15 22L11 13L2 9L22 2Z" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
            </button>
        </div>
        <div class="septo-footer">Prețuri orientative • METROGLASS © 2026</div>
    </div>
    <button id="septo-btn" onclick="window._septo.toggle()">
        <span class="septo-badge">1</span>
        <svg class="chat-icon" width="28" height="28" viewBox="0 0 24 24" fill="none"><path d="M21 11.5a8.38 8.38 0 01-.9 3.8 8.5 8.5 0 01-7.6 4.7 8.38 8.38 0 01-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 01-.9-3.8 8.5 8.5 0 014.7-7.6 8.38 8.38 0 013.8-.9h.5a8.48 8.48 0 018 8v.5z" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
        <svg class="close-icon" width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M18 6L6 18M6 6l12 12" stroke="#fff" stroke-width="2.5" stroke-linecap="round"/></svg>
    </button>`;

    // ====== INJECT ======
    const style = document.createElement('style');
    style.textContent = css;
    document.head.appendChild(style);

    const widget = document.createElement('div');
    widget.id = 'septo-widget';
    widget.innerHTML = html;
    document.body.appendChild(widget);

    // ====== LOGIC ======
    let history = [];
    let isOpen = false;

    history.push({
        role: "assistant",
        content: "Bună ziua! Sunt SEPTO, asistentul virtual METROGLASS. 👋\n\nVă pot ajuta să estimați rapid prețul pentru ferestre sau uși din PVC.\n\nCe vă interesează?"
    });

    window._septo = {
        toggle: function() {
            isOpen = !isOpen;
            document.getElementById('septo-panel').classList.toggle('visible', isOpen);
            document.getElementById('septo-btn').classList.toggle('open', isOpen);
            if (isOpen) setTimeout(() => document.getElementById('septo-input').focus(), 350);
        },

        sendQuick: function(text) {
            const q = document.getElementById('septo-quick');
            if (q) q.remove();
            document.getElementById('septo-input').value = text;
            this.send();
        },

        send: async function() {
            const input = document.getElementById('septo-input');
            const text = input.value.trim();
            if (!text) return;

            this.addMsg(text, 'user');
            input.value = '';
            document.getElementById('septo-send-btn').disabled = true;

            const typing = this.showTyping();

            try {
                const res = await fetch(API_URL + '/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: text, history: history })
                });
                const data = await res.json();
                typing.remove();
                this.addMsg(data.response, 'bot');
                history.push({ role: "user", content: text });
                history.push({ role: "assistant", content: data.response });
                if (history.length > 20) history = history.slice(-20);
            } catch(e) {
                typing.remove();
                this.addMsg('Conexiune pierdută. Încercați din nou.', 'bot');
            }

            document.getElementById('septo-send-btn').disabled = false;
        },

        addMsg: function(text, type) {
            const div = document.createElement('div');
            div.className = 'septo-msg ' + type;
            div.textContent = text;
            document.getElementById('septo-msgs').appendChild(div);
            this.scroll();
            return div;
        },

        showTyping: function() {
            const div = document.createElement('div');
            div.className = 'septo-typing';
            div.innerHTML = '<span></span><span></span><span></span>';
            document.getElementById('septo-msgs').appendChild(div);
            this.scroll();
            return div;
        },

        scroll: function() {
            const el = document.getElementById('septo-msgs');
            setTimeout(() => el.scrollTop = el.scrollHeight, 50);
        }
    };
})();
