###############################################################
# AI LINUX COMMAND ASSISTANT — STREAMLIT WEB VERSION
# Python + Streamlit + Ollama
# Works on PC browser and iPhone Safari
# Non-Commercial / Personal Use
###############################################################

import streamlit as st
import subprocess
import sqlite3
import json
import os
import re
import datetime
import time

import requests

###############################################################
# CONFIG
###############################################################
APP_NAME      = "AI Linux Command Assistant"
VERSION       = "1.0.0"
DEFAULT_MODEL = "llama3-8b"
FAVORITES_DB  = "favorites.db"
HISTORY_FILE  = "command_history.json"
OLLAMA_URL    = os.environ.get("OLLAMA_URL", "http://localhost:11434")

AVAILABLE_MODELS = [
    "llama3", "llama3.2", "mistral",
    "codellama", "gemma2", "phi3"
]

CATEGORIES = [
    "General", "System", "Network", "Files",
    "Process", "Disk", "Testing", "Security",
    "Docker", "Custom"
]

DANGEROUS_COMMANDS = [
    "rm -rf /", "mkfs", "> /dev/sda", "dd if="
]

SYSTEM_PROMPT = """
You are a professional Linux system administrator and DevOps engineer.
Your role is to help users run Linux commands for system testing,
monitoring, debugging, and administration.

When responding:
1. Always provide the exact command to run
2. Wrap commands in ```bash ``` code blocks
3. Explain what the command does briefly
4. Warn about any dangerous operations
5. Suggest safer alternatives when applicable
6. Format output clearly

Be concise, accurate, and professional.
"""

###############################################################
# PAGE CONFIG & DARK THEME
###############################################################
st.set_page_config(
    page_title=APP_NAME,
    page_icon="🐧",
    layout="wide",
    initial_sidebar_state="expanded"
)

DARK_CSS = """
<style>
/* ── Global ── */
html, body, [class*="css"] {
    background-color: #1e1e2e !important;
    color: #cdd6f4 !important;
    font-family: 'Consolas', 'Courier New', monospace !important;
}

/* ── Main block ── */
.main .block-container {
    background-color: #1e1e2e !important;
    padding-top: 1rem;
    max-width: 100%;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background-color: #181825 !important;
    border-right: 1px solid #313244;
}
section[data-testid="stSidebar"] * {
    color: #cdd6f4 !important;
}

/* ── Inputs ── */
input, textarea, .stTextInput input, .stTextArea textarea {
    background-color: #181825 !important;
    color: #cdd6f4 !important;
    border: 2px solid #313244 !important;
    border-radius: 8px !important;
    font-family: 'Consolas', monospace !important;
}
input:focus, textarea:focus {
    border-color: #89b4fa !important;
    box-shadow: 0 0 0 1px #89b4fa !important;
}

/* ── Buttons ── */
.stButton > button {
    background-color: #313244 !important;
    color: #cdd6f4 !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Consolas', monospace !important;
    font-weight: bold !important;
    transition: background 0.2s;
}
.stButton > button:hover {
    background-color: #45475a !important;
    color: #ffffff !important;
}

/* ── Select box ── */
.stSelectbox div[data-baseweb="select"] > div {
    background-color: #313244 !important;
    color: #cdd6f4 !important;
    border: 1px solid #45475a !important;
    border-radius: 6px !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background-color: #181825 !important;
    border-radius: 8px;
    padding: 4px;
}
.stTabs [data-baseweb="tab"] {
    background-color: transparent !important;
    color: #6c7086 !important;
    border-radius: 6px !important;
    font-weight: bold;
}
.stTabs [aria-selected="true"] {
    background-color: #313244 !important;
    color: #f9e2af !important;
}

/* ── Expander ── */
.streamlit-expanderHeader {
    background-color: #313244 !important;
    color: #cdd6f4 !important;
    border-radius: 8px !important;
}
.streamlit-expanderContent {
    background-color: #1e1e2e !important;
    border: 1px solid #313244 !important;
}

/* ── Metrics ── */
[data-testid="metric-container"] {
    background-color: #313244 !important;
    border-radius: 8px !important;
    padding: 10px !important;
    border: 1px solid #45475a !important;
}

/* ── Chat messages ── */
.chat-user {
    background-color: #313244;
    border-left: 4px solid #89b4fa;
    border-radius: 8px;
    padding: 12px 16px;
    margin: 6px 0;
    font-family: 'Consolas', monospace;
    line-height: 1.6;
}
.chat-assistant {
    background-color: #1e1e2e;
    border-left: 4px solid #a6e3a1;
    border-radius: 8px;
    padding: 12px 16px;
    margin: 6px 0;
    border: 1px solid #313244;
    font-family: 'Consolas', monospace;
    line-height: 1.6;
}
.chat-system {
    background-color: #1e1e2e;
    border-left: 4px solid #f38ba8;
    border-radius: 8px;
    padding: 12px 16px;
    margin: 6px 0;
    border: 1px solid #313244;
    font-family: 'Consolas', monospace;
}
.chat-label-user      { color: #89b4fa; font-size: 11px; font-weight: bold; }
.chat-label-assistant { color: #a6e3a1; font-size: 11px; font-weight: bold; }
.chat-label-system    { color: #f38ba8; font-size: 11px; font-weight: bold; }

/* ── Terminal output ── */
.terminal-box {
    background-color: #0d0d0d;
    color: #00ff99;
    border: 1px solid #313244;
    border-radius: 8px;
    padding: 12px;
    font-family: 'Consolas', monospace;
    font-size: 13px;
    white-space: pre-wrap;
    word-wrap: break-word;
    min-height: 80px;
    max-height: 400px;
    overflow-y: auto;
}
.terminal-error { color: #f38ba8 !important; }
.terminal-header { color: #89b4fa; font-weight: bold; }

/* ── Code blocks ── */
code {
    background-color: #181825 !important;
    color: #a6e3a1 !important;
    border-radius: 4px !important;
    padding: 2px 6px !important;
}
pre {
    background-color: #181825 !important;
    border-left: 3px solid #a6e3a1 !important;
    border-radius: 6px !important;
    padding: 10px !important;
    color: #a6e3a1 !important;
}

/* ── Section headers ── */
.section-header {
    color: #6c7086;
    font-size: 12px;
    font-weight: bold;
    text-transform: uppercase;
    letter-spacing: 1px;
    padding: 4px 0;
    border-bottom: 1px solid #313244;
    margin-bottom: 8px;
}
.app-title {
    color: #89b4fa;
    font-size: 22px;
    font-weight: bold;
    font-family: 'Consolas', monospace;
}

/* ── Status badges ── */
.badge-ok      { background:#a6e3a1; color:#1e1e2e; padding:2px 10px; border-radius:12px; font-size:12px; font-weight:bold; }
.badge-error   { background:#f38ba8; color:#1e1e2e; padding:2px 10px; border-radius:12px; font-size:12px; font-weight:bold; }
.badge-warning { background:#f9e2af; color:#1e1e2e; padding:2px 10px; border-radius:12px; font-size:12px; font-weight:bold; }

/* ── Favorite item ── */
.fav-item {
    background-color: #313244;
    border-radius: 6px;
    padding: 8px 12px;
    margin: 4px 0;
    border-left: 3px solid #f9e2af;
    font-size: 13px;
    font-family: 'Consolas', monospace;
}
.fav-category { color: #f9e2af; font-size: 11px; }
.fav-command  { color: #a6e3a1; font-family: 'Consolas', monospace; }

/* ── History item ── */
.hist-item {
    background-color: #1e1e2e;
    border: 1px solid #313244;
    border-radius: 6px;
    padding: 6px 10px;
    margin: 3px 0;
    color: #89b4fa;
    font-family: 'Consolas', monospace;
    font-size: 13px;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #181825; border-radius: 4px; }
::-webkit-scrollbar-thumb { background: #45475a; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #6c7086; }

/* ── Mobile ── */
@media (max-width: 768px) {
    .main .block-container { padding: 0.5rem !important; }
    .app-title { font-size: 16px !important; }
}

/* ── Divider ── */
hr { border-color: #313244 !important; }

/* ── File uploader ── */
[data-testid="stFileUploader"] {
    background-color: #313244 !important;
    border: 2px dashed #45475a !important;
    border-radius: 8px !important;
}
</style>
"""

st.markdown(DARK_CSS, unsafe_allow_html=True)

###############################################################
# SESSION STATE INIT
###############################################################
def init_state():
    defaults = {
        "chat_history":     [],        # [{role, content, timestamp}]
        "terminal_lines":   [],        # [{text, type}] type: normal/error/header
        "command_history":  [],        # [str]
        "last_ai_command":  "",
        "current_model":    DEFAULT_MODEL,
        "ollama_status":    None,      # True/False/None
        "is_streaming":     False,
        "streaming_buffer": "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

###############################################################
# FAVORITES DATABASE
###############################################################
@st.cache_resource
def get_db():
    conn = sqlite3.connect(FAVORITES_DB, check_same_thread=False)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS favorites (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL,
            command     TEXT NOT NULL,
            category    TEXT DEFAULT 'General',
            description TEXT DEFAULT '',
            created_at  TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.commit()
    return conn

def db_add(name, command, category="General", description=""):
    db = get_db()
    db.execute(
        "INSERT INTO favorites (name,command,category,description) VALUES (?,?,?,?)",
        (name, command, category, description)
    )
    db.commit()

def db_delete(fav_id):
    db = get_db()
    db.execute("DELETE FROM favorites WHERE id=?", (fav_id,))
    db.commit()

@st.cache_data(ttl=30)  # Cache for 30 seconds
def db_get_all_cached(category_filter=None, search_kw=None):
    return db_get_all(category_filter, search_kw)

    db = get_db()
    query = "SELECT id,name,command,category,description,created_at FROM favorites"
    params = []
    conditions = []
    if category_filter and category_filter != "All":
        conditions.append("category=?")
        params.append(category_filter)
    if search_kw:
        conditions.append(
            "(name LIKE ? OR command LIKE ? OR description LIKE ?)"
        )
        kw = f"%{search_kw}%"
        params += [kw, kw, kw]
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " ORDER BY category, name"
    return db.execute(query, params).fetchall()

def db_export_json():
    rows = db_get_all()
    return json.dumps(
        [{"id":r[0],"name":r[1],"command":r[2],
          "category":r[3],"description":r[4],"created_at":r[5]}
         for r in rows],
        indent=2
    )

def db_import_json(json_str):
    data = json.loads(json_str)
    for item in data:
        db_add(
            item.get("name","Imported"),
            item.get("command",""),
            item.get("category","General"),
            item.get("description","")
        )

###############################################################
# HISTORY FILE
###############################################################
def save_history():
    try:
        with open(HISTORY_FILE, "w") as f:
            json.dump(st.session_state.command_history[:100], f, indent=2)
    except:
        pass

def load_history():
    try:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE) as f:
                st.session_state.command_history = json.load(f)
    except:
        st.session_state.command_history = []

if not st.session_state.command_history:
    load_history()

###############################################################
# OLLAMA HELPERS
###############################################################
def get_ollama_models():
    """Return static list of Groq supported models"""
    return [
        "llama3",
        "llama3.2",
        "mistral",
        "gemma2",
        "codellama",
        "phi3"
    ]

def check_ollama():
    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        return False
    try:
        r = requests.get(
            "https://api.groq.com/openai/v1/models",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=5
        )
        return r.status_code == 200
    except:
        return False


def stream_ollama(model, messages):
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
    GROQ_MODELS = {
        "llama3": "llama3-8b-8192",  # Fast ⚡
        "llama3.2": "llama3-8b-8192",  # Fast ⚡ (changed)
        "mistral": "mixtral-8x7b-32768",
        "gemma2": "gemma2-9b-it",
        "codellama": "llama3-8b-8192",  # Fast ⚡
        "phi3": "llama3-8b-8192",  # Fast ⚡
    }

    groq_model = GROQ_MODELS.get(model, "llama3-8b-8192")

    try:
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type":  "application/json"
            },
            json={
                "model":    groq_model,
                "messages": messages,
                "stream":   True
            },
            stream=True,
            timeout=60
        )
        for line in r.iter_lines():
            if line:
                line = line.decode("utf-8")
                if line.startswith("data: "):
                    line = line[6:]
                if line.strip() == "[DONE]":
                    break
                try:
                    data  = json.loads(line)
                    chunk = data["choices"][0]["delta"].get("content","")
                    if chunk:
                        yield chunk
                except:
                    continue
    except Exception as e:
        yield f"\n⚠️ API Error: {e}"

###############################################################
# COMMAND RUNNER
###############################################################
def run_command(command):
    """Run shell command, return (stdout, stderr, returncode, elapsed)."""
    for danger in DANGEROUS_COMMANDS:
        if danger in command:
            return "", f"⛔ BLOCKED: '{command}' is potentially destructive.", -999, 0.0

    start = time.time()
    try:
        process = subprocess.Popen(
            command, shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate(timeout=60)
        elapsed = time.time() - start
        return stdout, stderr, process.returncode, elapsed
    except subprocess.TimeoutExpired:
        return "", "Command timed out (60s limit)", -1, 60.0
    except Exception as e:
        return "", str(e), -1, 0.0

###############################################################
# EXTRACT COMMANDS FROM AI RESPONSE
###############################################################
def extract_commands(text):
    blocks = re.findall(r'```(?:bash|sh)?\n?(.*?)```', text, re.DOTALL)
    commands = []
    for block in blocks:
        lines = [
            l.strip() for l in block.strip().splitlines()
            if l.strip() and not l.strip().startswith('#')
        ]
        commands.extend(lines)
    return commands

###############################################################
# FORMAT CHAT MESSAGE HTML
###############################################################
def render_chat_message(role, content, timestamp):
    css_class = f"chat-{role}"
    label_class = f"chat-label-{role}"
    labels = {"user": "👤 YOU", "assistant": "🤖 AI ASSISTANT", "system": "⚙ SYSTEM"}
    label = labels.get(role, role.upper())

    # Format code blocks
    content_html = re.sub(
        r'```(?:bash|sh)?\n?(.*?)```',
        r'<pre><code>\1</code></pre>',
        content, flags=re.DOTALL
    )
    content_html = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', content_html)
    content_html = re.sub(r'\*(.*?)\*',     r'<i>\1</i>', content_html)
    content_html = content_html.replace('\n', '<br>')

    return f"""
    <div class="{css_class}">
        <div class="{label_class}">{label} &nbsp;
            <span style="color:#6c7086;font-size:10px;">{timestamp}</span>
        </div>
        <div style="margin-top:6px;">{content_html}</div>
    </div>
    """

###############################################################
# TERMINAL RENDER
###############################################################
def render_terminal():
    if not st.session_state.terminal_lines:
        return '<div class="terminal-box" style="color:#6c7086;">No output yet. Run a command below.</div>'

    lines_html = ""
    for line in st.session_state.terminal_lines:
        t    = line["type"]
        text = line["text"].replace("<","&lt;").replace(">","&gt;")
        text = text.replace("\n","<br>")
        if t == "header":
            lines_html += f'<span style="color:#89b4fa;font-weight:bold;">{text}</span>'
        elif t == "error":
            lines_html += f'<span style="color:#f38ba8;">{text}</span>'
        elif t == "success":
            lines_html += f'<span style="color:#a6e3a1;">{text}</span>'
        elif t == "info":
            lines_html += f'<span style="color:#f9e2af;">{text}</span>'
        else:
            lines_html += f'<span>{text}</span>'

    return f'<div class="terminal-box">{lines_html}</div>'

###############################################################
# SIDEBAR
###############################################################
with st.sidebar:
    st.markdown(f'<div class="app-title">🐧 {APP_NAME}</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="color:#6c7086;font-size:11px;">v{VERSION} · Personal Use</div>', unsafe_allow_html=True)
    st.divider()

    # ── Ollama Status ──────────────────────────────────────
    st.markdown('<div class="section-header">🔌 Ollama Status</div>', unsafe_allow_html=True)
    col_s1, col_s2 = st.columns([2, 1])
    with col_s1:
        if st.button("Check Connection", use_container_width=True):
            st.session_state.ollama_status = check_ollama()

    status = st.session_state.ollama_status
    if status is True:
        st.markdown('<span class="badge-ok">✅ Connected</span>', unsafe_allow_html=True)
    elif status is False:
        st.markdown('<span class="badge-error">❌ Offline</span>', unsafe_allow_html=True)
        st.info("Run: `ollama serve` in terminal")
    else:
        st.markdown('<span class="badge-warning">⚡ Not checked</span>', unsafe_allow_html=True)

    st.divider()

    # ── Model Selector ─────────────────────────────────────
    st.markdown('<div class="section-header">🧠 AI Model</div>', unsafe_allow_html=True)

    live_models = get_ollama_models()
    model_list  = live_models if live_models else AVAILABLE_MODELS

    if st.session_state.current_model not in model_list:
        model_list = [st.session_state.current_model] + model_list

    selected_model = st.selectbox(
        "Select Model", model_list,
        index=model_list.index(st.session_state.current_model),
        label_visibility="collapsed"
    )
    if selected_model != st.session_state.current_model:
        st.session_state.current_model = selected_model
        st.rerun()

    if live_models:
        st.markdown(
            f'<div style="color:#6c7086;font-size:11px;">📦 {len(live_models)} model(s) installed</div>',
            unsafe_allow_html=True
        )

    st.divider()

    # ── Quick Commands ─────────────────────────────────────
    st.markdown('<div class="section-header">⚡ Quick Ask</div>', unsafe_allow_html=True)

    quick_cmds = [
        "How do I check disk usage?",
        "Show CPU and memory usage",
        "List all running processes",
        "Check network connections",
        "Find large files on disk",
        "Monitor system logs in real time",
        "Check open ports",
        "List all docker containers",
    ]
    for qc in quick_cmds:
        if st.button(f"↗ {qc}", use_container_width=True, key=f"quick_{qc}"):
            ts = datetime.datetime.now().strftime("%H:%M:%S")
            st.session_state.chat_history.append({
                "role": "user", "content": qc, "timestamp": ts
            })
            st.session_state["_send_pending"] = qc
            st.rerun()

    st.divider()

    # ── Chat Controls ──────────────────────────────────────
    st.markdown('<div class="section-header">🗂 Chat</div>', unsafe_allow_html=True)

    if st.button("🗑 Clear Chat", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

    if st.button("💾 Export Chat (.txt)", use_container_width=True):
        chat_txt = ""
        for msg in st.session_state.chat_history:
            chat_txt += f"[{msg['role'].upper()}] {msg.get('timestamp','')}\n"
            chat_txt += f"{msg['content']}\n\n"
        st.download_button(
            "⬇ Download Chat",
            data=chat_txt,
            file_name=f"chat_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
            use_container_width=True
        )

    if st.button("💾 Export Chat (.json)", use_container_width=True):
        st.download_button(
            "⬇ Download JSON",
            data=json.dumps(st.session_state.chat_history, indent=2),
            file_name=f"chat_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )

###############################################################
# MAIN AREA — TABS
###############################################################
tab_chat, tab_terminal, tab_favorites, tab_history = st.tabs([
    "💬  Chat",
    "💻  Terminal",
    "⭐  Favorites",
    "📋  History"
])

###############################################################
# TAB 1 — CHAT
###############################################################
with tab_chat:
    st.markdown('<div class="section-header">💬 AI Assistant Chat</div>',
                unsafe_allow_html=True)

    # ── Chat Display ───────────────────────────────────────
    chat_container = st.container()
    with chat_container:
        if not st.session_state.chat_history:
            st.markdown(render_chat_message(
                "assistant",
                "**Welcome to AI Linux Command Assistant!** 🐧\n\n"
                "I can help you with:\n"
                "- 🔍 Finding the right Linux commands\n"
                "- 📊 System monitoring and diagnostics\n"
                "- 🧪 Running tests and benchmarks\n"
                "- 🛠 Debugging and troubleshooting\n"
                "- 📁 File and permission management\n"
                "- 🌐 Network diagnostics\n\n"
                "Try asking: *\"How do I check disk usage?\"*",
                datetime.datetime.now().strftime("%H:%M:%S")
            ), unsafe_allow_html=True)
        else:
            for msg in st.session_state.chat_history:
                st.markdown(
                    render_chat_message(
                        msg["role"],
                        msg["content"],
                        msg.get("timestamp", "")
                    ),
                    unsafe_allow_html=True
                )

    # ── Streaming Placeholder ──────────────────────────────
    stream_placeholder = st.empty()

    # ── Chat Input ─────────────────────────────────────────
    st.divider()
    col_input, col_send = st.columns([5, 1])
    with col_input:
        user_input = st.text_input(
            "message", label_visibility="collapsed",
            placeholder="Ask about any Linux command...",
            key="chat_input_box"
        )
    with col_send:
        send_btn = st.button("⮕ Send", use_container_width=True, type="primary")

    # ── Action Row ─────────────────────────────────────────
    col_a1, col_a2, col_a3, col_a4 = st.columns(4)
    with col_a1:
        run_last = st.button("▶ Run Last Command", use_container_width=True)
    with col_a2:
        copy_last = st.button("⎘ Copy Command", use_container_width=True)
    with col_a3:
        save_fav_btn = st.button("⭐ Save to Favorites", use_container_width=True)
    with col_a4:
        if st.session_state.last_ai_command:
            st.markdown(
                f'<div style="color:#a6e3a1;font-size:11px;padding-top:8px;'
                f'font-family:Consolas;">📌 {st.session_state.last_ai_command[:40]}...</div>'
                if len(st.session_state.last_ai_command) > 40
                else f'<div style="color:#a6e3a1;font-size:11px;padding-top:8px;'
                     f'font-family:Consolas;">📌 {st.session_state.last_ai_command}</div>',
                unsafe_allow_html=True
            )

    # ── Handle Send ───────────────────────────────────────
    pending = st.session_state.pop("_send_pending", None)
    message_to_send = pending or (user_input if (send_btn and user_input.strip()) else None)

    if message_to_send:
        ts = datetime.datetime.now().strftime("%H:%M:%S")

        # Add user message (only if not already added by quick button)
        if not pending:
            st.session_state.chat_history.append({
                "role": "user", "content": message_to_send, "timestamp": ts
            })

        # Build messages for Ollama
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        for msg in st.session_state.chat_history[-12:]:
            messages.append({"role": msg["role"], "content": msg["content"]})

        # Stream response
        full_response = ""
        with stream_placeholder.container():
            st.markdown(
                '<div style="color:#f9e2af;font-size:13px;">⟳ AI is thinking...</div>',
                unsafe_allow_html=True
            )
            response_box = st.empty()
            for chunk in stream_ollama(st.session_state.current_model, messages):
                full_response += chunk
                response_box.markdown(
                    render_chat_message("assistant", full_response + " ▌", ts),
                    unsafe_allow_html=True
                )

        stream_placeholder.empty()

        if full_response:
            ai_ts = datetime.datetime.now().strftime("%H:%M:%S")
            st.session_state.chat_history.append({
                "role": "assistant", "content": full_response, "timestamp": ai_ts
            })

            # Extract commands
            cmds = extract_commands(full_response)
            if cmds:
                st.session_state.last_ai_command = cmds[0]

        st.rerun()

    # ── Handle Run Last ────────────────────────────────────
    if run_last:
        if st.session_state.last_ai_command:
            st.session_state["_run_command"] = st.session_state.last_ai_command
            st.rerun()
        else:
            st.warning("No command available yet. Ask the AI first!")

    # ── Handle Copy ────────────────────────────────────────
    if copy_last:
        if st.session_state.last_ai_command:
            st.code(st.session_state.last_ai_command, language="bash")
            st.success("☝️ Select and copy the command above!")
        else:
            st.warning("No command available yet.")

    # ── Handle Save to Favorites ───────────────────────────
    if save_fav_btn:
        if st.session_state.last_ai_command:
            st.session_state["_prefill_fav_cmd"] = st.session_state.last_ai_command
            st.info("Go to ⭐ Favorites tab to save it!")
        else:
            st.warning("No command available yet.")

###############################################################
# TAB 2 — TERMINAL
###############################################################
with tab_terminal:
    st.markdown('<div class="section-header">💻 Terminal Output</div>',
                unsafe_allow_html=True)

    # ── Terminal Display ───────────────────────────────────
    st.markdown(render_terminal(), unsafe_allow_html=True)

    # ── Command Input ──────────────────────────────────────
    st.divider()
    col_cmd, col_run, col_clr = st.columns([5, 1, 1])
    with col_cmd:
        direct_cmd = st.text_input(
            "cmd", label_visibility="collapsed",
            placeholder="Enter Linux command to run...",
            key="direct_cmd_input",
            value=st.session_state.get("_prefill_cmd", "")
        )
        if "_prefill_cmd" in st.session_state:
            del st.session_state["_prefill_cmd"]

    with col_run:
        run_btn = st.button("▶ Run", use_container_width=True, type="primary")
    with col_clr:
        if st.button("✕ Clear", use_container_width=True):
            st.session_state.terminal_lines = []
            st.rerun()

    # ── Run Pending Command (from Chat tab) ────────────────
    pending_run = st.session_state.pop("_run_command", None)
    cmd_to_run  = pending_run or (direct_cmd if run_btn and direct_cmd.strip() else None)

    if cmd_to_run:
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        st.session_state.terminal_lines.append({
            "text": f"\n[{ts}] $ {cmd_to_run}\n",
            "type": "header"
        })

        with st.spinner(f"Running: {cmd_to_run}"):
            stdout, stderr, returncode, elapsed = run_command(cmd_to_run)

        if stdout:
            st.session_state.terminal_lines.append({"text": stdout, "type": "normal"})
        if stderr:
            st.session_state.terminal_lines.append({"text": stderr, "type": "error"})

        icon = "✔" if returncode == 0 else "✖"
        t    = "success" if returncode == 0 else "error"
        st.session_state.terminal_lines.append({
            "text": f"\n{icon} Exit: {returncode}  |  Time: {elapsed:.2f}s\n",
            "type": t
        })

        # Save to history
        if cmd_to_run not in st.session_state.command_history:
            st.session_state.command_history.insert(0, cmd_to_run)
            save_history()

        st.rerun()

    # ── Quick Run Buttons ──────────────────────────────────
    st.divider()
    st.markdown('<div class="section-header">⚡ Quick Run</div>', unsafe_allow_html=True)

    quick_run_cmds = [
        ("📊 CPU Info",        "lscpu | head -20"),
        ("💾 Disk Usage",      "df -h"),
        ("🧠 Memory",          "free -h"),
        ("⚙ Processes",       "ps aux --sort=-%cpu | head -20"),
        ("🌐 Network",         "ip addr show"),
        ("📁 Current Dir",     "ls -la"),
        ("🕐 Uptime",          "uptime"),
        ("👤 Current User",    "whoami && id"),
        ("🐧 OS Info",         "uname -a"),
        ("📦 Disk Inodes",     "df -i"),
    ]

    cols = st.columns(5)
    for i, (label, cmd) in enumerate(quick_run_cmds):
        with cols[i % 5]:
            if st.button(label, use_container_width=True, key=f"qrun_{i}"):
                st.session_state["_run_command"] = cmd
                st.rerun()

###############################################################
# TAB 3 — FAVORITES
###############################################################
with tab_favorites:
    st.markdown('<div class="section-header">⭐ Favorite Commands</div>',
                unsafe_allow_html=True)

    # ── Add New Favorite ───────────────────────────────────
    with st.expander("➕ Add New Favorite", expanded=bool(
            st.session_state.get("_prefill_fav_cmd"))):
        col_n, col_c = st.columns(2)
        with col_n:
            fav_name = st.text_input(
                "Name *",
                placeholder="e.g. Check Disk Usage",
                key="fav_name_input"
            )
        with col_c:
            fav_cat = st.selectbox(
                "Category", CATEGORIES,
                key="fav_cat_input"
            )

        fav_cmd = st.text_input(
            "Command *",
            value=st.session_state.pop("_prefill_fav_cmd", ""),
            placeholder="e.g. df -h",
            key="fav_cmd_input"
        )
        fav_desc = st.text_area(
            "Description (optional)",
            placeholder="What does this command do?",
            height=60,
            key="fav_desc_input"
        )

        if st.button("💾 Save Favorite", type="primary", use_container_width=True):
            if not fav_name.strip():
                st.error("⚠ Name is required!")
            elif not fav_cmd.strip():
                st.error("⚠ Command is required!")
            else:
                db_add(fav_name.strip(), fav_cmd.strip(),
                       fav_cat, fav_desc.strip())
                st.success(f"✅ Saved: {fav_name}")
                st.rerun()

    st.divider()

    # ── Search & Filter ────────────────────────────────────
    col_fs, col_fc = st.columns([3, 2])
    with col_fs:
        fav_search = st.text_input(
            "search", label_visibility="collapsed",
            placeholder="🔍 Search favorites...",
            key="fav_search_input"
        )
    with col_fc:
        fav_cat_filter = st.selectbox(
            "filter", ["All"] + CATEGORIES,
            label_visibility="collapsed",
            key="fav_cat_filter"
        )

    # ── Display Favorites ──────────────────────────────────
    rows = db_get_all(
        category_filter=fav_cat_filter if fav_cat_filter != "All" else None,
        search_kw=fav_search if fav_search.strip() else None
    )

    if not rows:
        st.markdown(
            '<div style="color:#6c7086;text-align:center;padding:20px;">'
            'No favorites yet. Add one above! ⭐</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f'<div style="color:#6c7086;font-size:12px;">'
            f'Showing {len(rows)} favorite(s)</div>',
            unsafe_allow_html=True
        )
        for row in rows:
            fav_id, name, command, category, desc, created = row
            with st.container():
                col_fi, col_fr, col_fd = st.columns([5, 1, 1])
                with col_fi:
                    st.markdown(f"""
                    <div class="fav-item">
                        <div class="fav-category">📁 {category}</div>
                        <div><b>{name}</b></div>
                        <div class="fav-command">$ {command}</div>
                        {"<div style='color:#6c7086;font-size:11px;'>"+desc+"</div>" if desc else ""}
                    </div>
                    """, unsafe_allow_html=True)
                with col_fr:
                    if st.button("▶", key=f"fav_run_{fav_id}",
                                 help="Run this command"):
                        st.session_state["_run_command"] = command
                        st.session_state["_switch_tab"]  = "terminal"
                        st.rerun()
                with col_fd:
                    if st.button("🗑", key=f"fav_del_{fav_id}",
                                 help="Delete this favorite"):
                        db_delete(fav_id)
                        st.success(f"Deleted: {name}")
                        st.rerun()

    st.divider()

    # ── Export / Import ────────────────────────────────────
    st.markdown('<div class="section-header">📤 Export / Import</div>',
                unsafe_allow_html=True)
    col_exp, col_imp = st.columns(2)
    with col_exp:
        json_data = db_export_json()
        st.download_button(
            "⬆ Export Favorites (.json)",
            data=json_data,
            file_name=f"favorites_{datetime.datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json",
            use_container_width=True
        )
    with col_imp:
        uploaded = st.file_uploader(
            "⬇ Import Favorites (.json)",
            type=["json"],
            key="fav_import_upload",
            label_visibility="collapsed"
        )
        if uploaded:
            try:
                db_import_json(uploaded.read().decode("utf-8"))
                st.success("✅ Favorites imported!")
                st.rerun()
            except Exception as e:
                st.error(f"Import error: {e}")

###############################################################
# TAB 4 — HISTORY
###############################################################
with tab_history:
    st.markdown('<div class="section-header">📋 Command History</div>',
                unsafe_allow_html=True)

    if not st.session_state.command_history:
        st.markdown(
            '<div style="color:#6c7086;text-align:center;padding:20px;">'
            'No commands run yet.</div>',
            unsafe_allow_html=True
        )
    else:
        col_hdr1, col_hdr2 = st.columns([4, 1])
        with col_hdr1:
            st.markdown(
                f'<div style="color:#6c7086;font-size:12px;">'
                f'{len(st.session_state.command_history)} command(s) in history</div>',
                unsafe_allow_html=True
            )
        with col_hdr2:
            if st.button("✕ Clear All", use_container_width=True):
                st.session_state.command_history = []
                save_history()
                st.rerun()

        st.divider()

        for i, cmd in enumerate(st.session_state.command_history):
            col_hi, col_hr, col_hs = st.columns([5, 1, 1])
            with col_hi:
                st.markdown(
                    f'<div class="hist-item">$ {cmd}</div>',
                    unsafe_allow_html=True
                )
            with col_hr:
                if st.button("▶", key=f"hist_run_{i}", help="Run again"):
                    st.session_state["_run_command"] = cmd
                    st.rerun()
            with col_hs:
                if st.button("⭐", key=f"hist_save_{i}", help="Save to favorites"):
                    st.session_state["_prefill_fav_cmd"] = cmd
                    st.info("Go to ⭐ Favorites tab to save it!")

    # ── Export History ─────────────────────────────────────
    if st.session_state.command_history:
        st.divider()
        hist_json = json.dumps(st.session_state.command_history, indent=2)
        st.download_button(
            "⬆ Export History (.json)",
            data=hist_json,
            file_name=f"history_{datetime.datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json",
            use_container_width=True
        )

###############################################################
# FOOTER STATUS BAR
###############################################################
st.divider()
col_f1, col_f2, col_f3, col_f4 = st.columns(4)
with col_f1:
    st.markdown(
        f'<div style="color:#6c7086;font-size:11px;">🧠 Model: '
        f'<span style="color:#89b4fa;">{st.session_state.current_model}</span></div>',
        unsafe_allow_html=True
    )
with col_f2:
    st.markdown(
        f'<div style="color:#6c7086;font-size:11px;">💬 Messages: '
        f'<span style="color:#cdd6f4;">{len(st.session_state.chat_history)}</span></div>',
        unsafe_allow_html=True
    )
with col_f3:
    st.markdown(
        f'<div style="color:#6c7086;font-size:11px;">📋 History: '
        f'<span style="color:#cdd6f4;">{len(st.session_state.command_history)}</span></div>',
        unsafe_allow_html=True
    )
with col_f4:
    fav_count = len(db_get_all())
    st.markdown(
        f'<div style="color:#6c7086;font-size:11px;">⭐ Favorites: '
        f'<span style="color:#f9e2af;">{fav_count}</span></div>',
        unsafe_allow_html=True
    )
