import streamlit as st
import requests
import time

# ── Page Config (Spacious layout with custom Gemini-style page title) ──
st.set_page_config(
    page_title="Enterprise Multi-Agent AI Assistant",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Core Visual Design System (Google Gemini CSS) ──
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Overrides */
    *, html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Enforce Outfit font for Headers/Titles */
    h1, h2, h3, .top-nav-title, .brand-text, .welcome-title, .welcome-title-sparkle, .card-title {
        font-family: 'Outfit', sans-serif !important;
    }
    
    .stApp {
        background-color: #131314 !important;
    }
    
    /* Hide default Streamlit decoration lines and headers */
    header {
        visibility: hidden !important;
    }
    
    /* Main Area Containers */
    .block-container {
        max-width: 820px !important;
        padding: 5.5rem 1.5rem 120px 1.5rem !important; /* Spacious bottom padding */
        margin: 0 auto !important;
    }
    
    /* ── Top Navigation Bar (Gemini Style) ── */
    .top-nav {
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        right: 0 !important;
        height: 56px !important;
        background-color: rgba(19, 19, 20, 0.85) !important;
        backdrop-filter: blur(12px) !important;
        border-bottom: 1px solid #282829 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        z-index: 998 !important;
    }
    .top-nav-title {
        font-size: 1rem !important;
        font-weight: 500 !important;
        color: #e3e3e3 !important;
        letter-spacing: 0.5px !important;
        display: flex !important;
        align-items: center !important;
        gap: 8px !important;
    }
    .top-nav-sparkle {
        font-size: 1.1rem;
        background: linear-gradient(135deg, #4285f4, #9b72cb);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: bold;
    }
    
    /* ── Sidebar (Gemini Sidebar Theme) ── */
    section[data-testid="stSidebar"] {
        background-color: #1e1f20 !important;
        border-right: none !important;
    }
    
    /* Sidebar Brand Styling */
    .sidebar-brand {
        padding: 1.5rem 0.75rem 1rem 0.75rem;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .brand-spark {
        font-size: 1.6rem;
        background: linear-gradient(135deg, #4285f4, #9b72cb);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: bold;
    }
    .brand-text {
        font-size: 1.15rem;
        font-weight: 500;
        color: #e3e3e3;
        letter-spacing: -0.2px;
    }
    .brand-subtitle {
        color: #8e8e8f;
        font-size: 0.7rem;
        margin-top: 2px;
        font-weight: 500;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    
    /* ── Global Button Overrides (Premium Google Pills) ── */
    div.stButton > button {
        border-radius: 24px !important;
        font-family: 'Inter', sans-serif !important;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: none !important;
    }
    
    /* Sidebar Pill Buttons (Gemini Style) */
    section[data-testid="stSidebar"] div.stButton > button {
        background-color: transparent !important;
        border: none !important;
        text-align: left !important;
        padding: 10px 16px !important;
        color: #c4c7c5 !important;
        font-size: 0.88rem !important;
        font-weight: 400 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: flex-start !important;
        margin-bottom: 4px !important;
    }
    section[data-testid="stSidebar"] div.stButton > button:hover {
        background-color: #2d2f31 !important;
        color: #e3e3e3 !important;
    }
    
    /* Sidebar "New Chat" Capsule Button Style */
    section[data-testid="stSidebar"] div.stButton:first-of-type > button {
        background-color: #2b2c2e !important;
        border: 1px solid #3c4043 !important;
        color: #e3e3e3 !important;
        padding: 10px 20px !important;
        display: flex !important;
        justify-content: center !important;
        font-weight: 500 !important;
        letter-spacing: 0.2px !important;
        margin-top: 4px !important;
    }
    section[data-testid="stSidebar"] div.stButton:first-of-type > button:hover {
        background-color: #35373a !important;
        border-color: #8e918f !important;
        color: #ffffff !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.3) !important;
    }
    
    /* ── Welcome Dashboard (Gemini Gradient Styling) ── */
    .welcome-container {
        text-align: left;
        padding: 4rem 0.5rem 2.5rem 0.5rem;
    }
    
    /* Grand Gradient Title */
    .welcome-title {
        font-size: 3.2rem;
        font-weight: 500;
        line-height: 1.2;
        letter-spacing: -1px;
        background: linear-gradient(74deg, #4285f4 0%, #9b72cb 20%, #d96570 45%, #f19e38 70%, #4285f4 95%);
        background-size: 200% 200%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: gradient-shift 8s ease infinite;
        margin-bottom: 0.5rem;
    }
    
    .welcome-subtitle {
        font-size: 3.2rem;
        font-weight: 500;
        line-height: 1.2;
        color: #3f3f40;
        letter-spacing: -1px;
        margin-bottom: 2rem;
    }
    
    @keyframes gradient-shift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* ── Chat Messages (Gemini Flat Minimalist Styling) ── */
    .user-msg {
        display: flex;
        justify-content: flex-end;
        margin-bottom: 1.5rem;
    }
    .user-msg-bubble {
        background-color: #1e1f20; /* Matching Sidebar and Containers */
        border-radius: 18px;
        padding: 10px 18px;
        max-width: 75%;
        color: #e3e3e3;
        font-size: 0.98rem;
        line-height: 1.55;
        white-space: pre-wrap;
    }
    
    /* Transparent and Spacing overrides for Assistant Chat Messages */
    div[data-testid="stChatMessage"] {
        background-color: transparent !important;
        border: none !important;
        padding: 1rem 0 !important;
        margin-bottom: 0.5rem !important;
    }
    div[data-testid="stChatMessageContent"] {
        color: #e3e3e3 !important;
        font-size: 1rem !important;
        line-height: 1.65 !important;
        padding-top: 2px !important;
    }
    .meta-line {
        font-size: 0.72rem;
        color: #8e8e8f;
        margin-top: 10px;
        display: flex;
        gap: 12px;
        align-items: center;
    }
    .meta-item {
        background-color: #1e1f20;
        border: 1px solid #2d2f31;
        padding: 2px 8px;
        border-radius: 4px;
    }
    
    /* ── Chat Input Bar (Gemini Pill Container) ── */
    div[data-testid="stHorizontalBlock"]:has(input[id*="chat_input"]) {
        position: fixed !important;
        bottom: 24px !important;
        left: 50% !important;
        transform: translateX(-50%) !important;
        width: calc(100% - 3rem) !important;
        max-width: 820px !important;
        background-color: #1e1f20 !important; /* Standard Gemini Input Bar background */
        border: none !important; /* Borderless */
        border-radius: 32px !important; /* Perfect Pill rounded shape */
        padding: 6px 12px 6px 18px !important;
        z-index: 1000 !important;
        box-shadow: 0 4px 16px rgba(0,0,0,0.25) !important;
        display: flex !important;
        align-items: center !important;
    }
    
    /* Remove padding inside columns of input block */
    div[data-testid="stHorizontalBlock"]:has(input[id*="chat_input"]) div[data-testid="column"] {
        padding: 0 !important;
        margin: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    
    /* Strip default text input styles inside the pill */
    div[data-testid="stHorizontalBlock"]:has(input[id*="chat_input"]) div[data-testid="stTextInput"] {
        width: 100% !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    div[data-testid="stHorizontalBlock"]:has(input[id*="chat_input"]) div[data-testid="stTextInput"] > div {
        background-color: transparent !important;
        border: none !important;
        padding: 0 !important;
        margin: 0 !important;
        box-shadow: none !important;
    }
    div[data-testid="stHorizontalBlock"]:has(input[id*="chat_input"]) input {
        background-color: transparent !important;
        border: none !important;
        color: #e3e3e3 !important;
        font-size: 0.98rem !important;
        padding: 10px 0 !important;
        box-shadow: none !important;
        width: 100% !important;
    }
    div[data-testid="stHorizontalBlock"]:has(input[id*="chat_input"]) input:focus {
        outline: none !important;
        box-shadow: none !important;
    }
    
    /* Submit button specific style (Circle dark button on right, now child 2) */
    div[data-testid="stHorizontalBlock"]:has(input[id*="chat_input"]) div[data-testid="column"]:nth-child(2) button {
        background-color: #131314 !important; /* Reverse dark background */
        color: #e3e3e3 !important;
        font-size: 1rem !important;
        border: none !important;
        width: 38px !important;
        height: 38px !important;
        border-radius: 50% !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
        padding: 0 !important;
        box-shadow: none !important;
    }
    div[data-testid="stHorizontalBlock"]:has(input[id*="chat_input"]) div[data-testid="column"]:nth-child(2) button:hover {
        background-color: #2f2f30 !important;
        color: #ffffff !important;
    }
    
    /* ── Suggestion Cards (Google Styled) ── */
    div[data-testid="stVerticalBlock"]:has(#suggestions-container-trigger) div.stButton > button {
        background-color: #1e1f20 !important; /* Flat card theme */
        border: 1px solid #2d2f31 !important; /* Clean soft border */
        border-radius: 18px !important; /* Spacious rounded cards */
        padding: 18px 22px !important;
        color: #e3e3e3 !important;
        text-align: left !important;
        width: 100% !important;
        min-height: 90px !important;
        display: flex !important;
        align-items: flex-start !important;
        flex-direction: column !important;
        justify-content: center !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.1) !important;
    }
    div[data-testid="stVerticalBlock"]:has(#suggestions-container-trigger) div.stButton > button:hover {
        background-color: #282a2c !important; /* Slightly lighter gray on hover */
        border-color: #4285f4 !important; /* Google Blue highlight border on hover */
        box-shadow: 0 4px 12px rgba(0,0,0,0.2) !important;
        transform: translateY(-2px) !important; /* Subtle floating micro-animation */
        color: #ffffff !important;
    }
    div[data-testid="stVerticalBlock"]:has(#suggestions-container-trigger) div.stButton > button p {
        font-family: 'Inter', sans-serif !important;
        font-size: 0.9rem !important;
        line-height: 1.45 !important;
        color: #c4c7c5 !important;
        font-weight: 400 !important;
        margin: 0 !important;
        text-align: left !important;
        white-space: pre-line !important; /* Support multiline card texts */
    }
    
    /* ── Footer ── */
    .app-footer {
        text-align: center;
        color: #8e8e8f;
        font-size: 0.72rem;
        padding: 2.5rem 0 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ── Session State Setup & Synchronization ──
if "sessions" not in st.session_state:
    st.session_state.sessions = [{"id": 0, "title": "New Chat", "history": []}]
if "active_session" not in st.session_state:
    st.session_state.active_session = 0
if "history" not in st.session_state:
    st.session_state.history = []
if "enable_search" not in st.session_state:
    st.session_state.enable_search = True
if "input_counter" not in st.session_state:
    st.session_state.input_counter = 0
if "suggested_prompt" not in st.session_state:
    st.session_state.suggested_prompt = None

def get_active_session():
    for s in st.session_state.sessions:
        if s["id"] == st.session_state.active_session:
            return s
    return st.session_state.sessions[0]

def save_active_session():
    s = get_active_session()
    s["history"] = st.session_state.history
    # Dynamically generate titles from first user prompt
    if s["title"] == "New Chat":
        for m in s["history"]:
            if m["role"] == "user":
                trimmed = m["content"][:32]
                s["title"] = trimmed + ("…" if len(m["content"]) > 32 else "")
                break

# Align current running history with active session
st.session_state.history = get_active_session()["history"]

# ── Sidebar Interface (Pill Rounded History Items) ──
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <div>
            <div style="display: flex; align-items: center; gap: 8px;">
                <span class="brand-spark">✦</span>
                <span class="brand-text">Multi-Agent AI</span>
            </div>
            <div class="brand-subtitle">Enterprise Assistant</div>
        </div>
    </div>
    <hr style="border-color: #282829; margin: 0.5rem 0 1rem 0;">
    """, unsafe_allow_html=True)
    
    # New Chat Pill button
    if st.button("＋  New Chat", key="new_chat_sidebar_btn", use_container_width=True):
        nid = max([s["id"] for s in st.session_state.sessions]) + 1 if st.session_state.sessions else 0
        st.session_state.sessions.insert(0, {"id": nid, "title": "New Chat", "history": []})
        st.session_state.active_session = nid
        st.session_state.history = []
        st.session_state.suggested_prompt = None
        st.rerun()
        
    st.markdown("""
    <div style="font-size: 0.72rem; color: #8e8e8f; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 500; padding: 1.25rem 1rem 0.5rem 1rem;">
        Conversations
    </div>
    """, unsafe_allow_html=True)
    
    # Render all historic sessions flat
    for s in st.session_state.sessions:
        is_active = s["id"] == st.session_state.active_session
        title_label = s["title"] or "New Chat"
        emoji_prefix = "💬" if is_active else "  "
        
        # Inject dynamic active highlighting class to sidebar buttons
        if is_active:
            st.markdown("""
            <style>
                section[data-testid="stSidebar"] div.stButton:has(button[key*="s_{id}"]) > button {{
                    background-color: #333537 !important; /* Active Google Pill Dark */
                    color: #ffffff !important;
                    font-weight: 500 !important;
                }}
            </style>
            """.format(id=s["id"]), unsafe_allow_html=True)
            
        if st.button(f"{emoji_prefix}  {title_label}", key=f"s_{s['id']}", use_container_width=True):
            save_active_session()
            st.session_state.active_session = s["id"]
            st.session_state.history = s["history"]
            st.session_state.suggested_prompt = None
            st.rerun()

# (Icons removed to maintain a standard, clean text field bar)

# ── Top Navbar Title ──
st.markdown("""
<div class="top-nav">
    <div class="top-nav-title">
        <span class="top-nav-sparkle">✦</span>
        Enterprise Multi-Agent AI Assistant
    </div>
</div>
""", unsafe_allow_html=True)

# ── Main Chat Area Layout ──
chat_container = st.container()

with chat_container:
    # 1. EMPTY HISTORY STATE: Render modern welcomer + Google-styled suggestion cards
    if not st.session_state.history:
        st.markdown("""
        <div class="welcome-container">
            <div class="welcome-title">Enterprise Multi-Agent</div>
            <div class="welcome-subtitle">AI Assistant</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Grid suggestions using standard buttons styled like cards
        st.markdown('<span id="suggestions-container-trigger"></span>', unsafe_allow_html=True)
        grid_col1, grid_col2 = st.columns(2)
        with grid_col1:
            if st.button("⚡ Calculate complex numbers\nWhat is 534 × 23 + 85?", key="sug_1", use_container_width=True):
                st.session_state.suggested_prompt = "Calculate 534 × 23 + 85"
            if st.button("📊 Compare business metrics\nCompare and compile sales differences", key="sug_2", use_container_width=True):
                st.session_state.suggested_prompt = "Compare sales Performance vs standard target metrics and compile a report"
        with grid_col2:
            if st.button("🔍 Search latest AI developments\nFind deep learning and agent breakthroughs", key="sug_3", use_container_width=True):
                st.session_state.suggested_prompt = "Search for the latest AI agent frameworks and summarize them"
            if st.button("📝 Draft enterprise summary\nCreate a structured executive template", key="sug_4", use_container_width=True):
                st.session_state.suggested_prompt = "Draft a template for an enterprise executive summary"
                
    # 2. CONVERSATION VIEW STATE: Render conversation thread
    else:
        for msg in st.session_state.history:
            if msg["role"] == "user":
                # Flat User chat bubble on right
                escaped_msg = msg["content"].replace("<", "&lt;").replace(">", "&gt;")
                st.markdown(f'<div class="user-msg"><div class="user-msg-bubble">{escaped_msg}</div></div>', unsafe_allow_html=True)
            else:
                # Left-aligned assistant with default avatar
                with st.chat_message("assistant"):
                    st.markdown(msg["content"])
                    if "tokens" in msg:
                        st.markdown(f"""
                        <div class="meta-line">
                            <span class="meta-item">⏱ {msg["time"]}s</span>
                            <span class="meta-item">⚡ {msg["tokens"]} tokens</span>
                        </div>
                        """, unsafe_allow_html=True)

# ── Model Configuration (Standard Defaults) ──
temperature, max_tokens, top_p = 0.7, 2048, 0.9

# ── Unified Chat Input Bar (Custom HTML layout fixed to bottom) ──
backend_url = "http://localhost:8000"
user_message_to_send = None

# Set up column layout for custom input bar (Clean 2-column layout: wide text input + send button)
cols = st.columns([0.92, 0.08])

# Column 0: The Custom Text Field
with cols[0]:
    chat_input_key = f"chat_input_{st.session_state.input_counter}"
    text_val = st.text_input(
        "",
        placeholder="Message AI Assistant...",
        key=chat_input_key,
        label_visibility="collapsed"
    )

# Column 1: Submit Button ▲
with cols[1]:
    submitted = st.button("▲", key=f"submit_btn_{st.session_state.input_counter}", help="Send message")

# ── Handle Submission Logic ──
# Case A: User clicked suggestion chip
if st.session_state.suggested_prompt:
    user_message_to_send = st.session_state.suggested_prompt
    st.session_state.suggested_prompt = None

# Case B: User submitted text inside custom input field
elif text_val:
    user_message_to_send = text_val

# Case C: User clicked circular arrow submit button with text in field
elif submitted and st.session_state.get(chat_input_key):
    user_message_to_send = st.session_state[chat_input_key]

# Trigger the Submission cycle if a message exists
if user_message_to_send:
    # 1. Update state history immediately
    st.session_state.history.append({"role": "user", "content": user_message_to_send})
    save_active_session()
    
    # 2. Reset Text Field by incrementing index counter
    st.session_state.input_counter += 1
    
    # 3. Complete submission
    st.rerun()

# ── API Execution Loop ──
# If the last message in history is a 'user' message, assistant should compute reply
if st.session_state.history and st.session_state.history[-1]["role"] == "user":
    user_prompt = st.session_state.history[-1]["content"]
    
    with chat_container:
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            with message_placeholder.container():
                st.markdown("""
                <div style="display: flex; align-items: center; gap: 8px; color: #888; font-size: 0.95rem;">
                    <span style="font-size: 1.2rem; background: linear-gradient(135deg, #4285f4, #9b72cb); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: bold; animation: pulse 1.5s infinite;">✦</span>
                    Thinking...
                </div>
                """, unsafe_allow_html=True)
            
            # Contact the agent backend API
            try:
                payload = {
                    "message": user_prompt,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "top_p": top_p,
                    "enable_search": st.session_state.enable_search
                }
                
                t0 = time.time()
                resp = requests.post(f"{backend_url}/api/agent", json=payload, timeout=90)
                dt = round(time.time() - t0, 2)
                
                if resp.status_code == 200:
                    data = resp.json()
                    answer = data.get("response", "")
                    tkn = data.get("total_token", 0)
                    
                    # Persist response and restart interface
                    st.session_state.history.append({
                        "role": "assistant",
                        "content": answer,
                        "tokens": tkn,
                        "time": dt
                    })
                    save_active_session()
                    st.rerun()
                else:
                    st.error(f"Error response ({resp.status_code}): {resp.text}")
            except Exception as e:
                st.error(f"Failed to connect to agent backend. Make sure the server is active on {backend_url}. Error: {e}")

# ── Persistent Elegant Footer ──
st.markdown('<div class="app-footer">Enterprise Multi-Agent AI Assistant may display inaccurate info. Always check important details.</div>', unsafe_allow_html=True)
