import streamlit as st
import requests
import time

# --- Page Configurations ---
st.set_page_config(
    page_title="Enterprise Multi-Agent AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Premium Custom Styling ---
st.markdown("""
<style>
    /* Google Font Import */
    @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;700&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', 'Google Sans', sans-serif;
    }
    
    /* Main Background & Text Color Override */
    .stApp {
        background-color: #0f0f11 !important;
        color: #e3e3e3 !important;
    }
    
    /* Sidebar Custom Styling */
    section[data-testid="stSidebar"] {
        background-color: #131314 !important;
        border-right: 1px solid #2d2f31 !important;
    }
    
    section[data-testid="stSidebar"] .stMarkdown, section[data-testid="stSidebar"] p {
        color: #c4c7c5 !important;
    }
    
    /* ---- Premium Sidebar Slider Styling ---- */
    section[data-testid="stSidebar"] .stSlider > div > div > div {
        background-color: #2d2f31 !important;
    }
    section[data-testid="stSidebar"] .stSlider [data-testid="stThumbValue"] {
        color: #8ab4f8 !important;
        font-weight: 600 !important;
        font-size: 0.8rem !important;
    }
    section[data-testid="stSidebar"] .stSlider label {
        color: #c4c7c5 !important;
        font-weight: 500 !important;
        font-size: 0.85rem !important;
    }
    
    /* ---- Premium Sidebar Button Styling ---- */
    section[data-testid="stSidebar"] .stButton > button {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%) !important;
        color: #f28b82 !important;
        border: 1px solid rgba(234, 67, 53, 0.25) !important;
        border-radius: 14px !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        padding: 0.65rem 1rem !important;
        transition: all 0.3s cubic-bezier(0.2, 0.8, 0.2, 1) !important;
        letter-spacing: 0.3px !important;
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: linear-gradient(135deg, #2a1a2e 0%, #2e1a3e 100%) !important;
        border-color: rgba(234, 67, 53, 0.5) !important;
        box-shadow: 0 4px 20px rgba(234, 67, 53, 0.15) !important;
        transform: translateY(-1px) !important;
    }
    
    /* Sidebar parameter card */
    .param-card {
        background-color: #1a1b1e;
        border: 1px solid #2d2f31;
        border-radius: 16px;
        padding: 1rem 1.1rem;
        margin-bottom: 0.75rem;
        transition: all 0.3s cubic-bezier(0.2, 0.8, 0.2, 1);
    }
    .param-card:hover {
        border-color: #3c4043;
        background-color: #1e1f22;
        box-shadow: 0 4px 16px rgba(0,0,0,0.2);
    }
    .param-header {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 4px;
    }
    .param-icon {
        font-size: 1.1rem;
    }
    .param-name {
        font-family: 'Google Sans', sans-serif;
        font-size: 0.9rem;
        font-weight: 600;
        color: #e3e3e3;
    }
    .param-desc {
        font-size: 0.72rem;
        color: #9e9e9e;
        line-height: 1.35;
        margin-bottom: 6px;
    }

    /* ---- Chat History Sidebar Items ---- */
    .history-item {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 0.6rem 0.85rem;
        border-radius: 12px;
        cursor: pointer;
        transition: all 0.2s ease;
        margin-bottom: 4px;
        border: 1px solid transparent;
    }
    .history-item:hover {
        background-color: rgba(255,255,255,0.05);
        border-color: #2d2f31;
    }
    .history-item-active {
        background-color: rgba(66, 133, 244, 0.1) !important;
        border-color: rgba(66, 133, 244, 0.3) !important;
    }
    .history-icon {
        font-size: 0.9rem;
        opacity: 0.7;
    }
    .history-label {
        font-size: 0.82rem;
        color: #c4c7c5;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        max-width: 180px;
    }
    
    /* Elegant Title Styling with Mesh Gradients */
    .gemini-title-container {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 0.5rem;
    }
    
    .gemini-title {
        font-family: 'Google Sans', sans-serif;
        background: linear-gradient(74deg, #4285f4 0%, #9b72cb 25%, #d96570 50%, #f4b400 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: 700;
        letter-spacing: -0.8px;
    }
    
    .gemini-subtitle {
        font-size: 1.1rem;
        color: #c4c7c5;
        margin-bottom: 2rem;
        font-weight: 400;
        line-height: 1.6;
    }
    
    /* Premium Google Material 3 Cards */
    .google-card {
        background-color: #1e1f20;
        border: 1px solid #2d2f31;
        border-radius: 20px;
        padding: 1.5rem;
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.2);
        transition: all 0.3s cubic-bezier(0.2, 0.8, 0.2, 1);
        margin-bottom: 1.5rem;
    }
    
    .google-card:hover {
        transform: translateY(-2px);
        background-color: #242526;
        border-color: #4285f4;
        box-shadow: 0 8px 32px rgba(66, 133, 244, 0.15);
    }
    
    \n    /* ---- Chat Bubble Styling ---- */

    /* Make st.chat_message container transparent (used for assistant only) */
    div[data-testid="stChatMessage"] {
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0.4rem 0 !important;
        margin-bottom: 0.75rem !important;
    }

    /* Assistant message content bubble */
    div[data-testid="stChatMessageContent"] {
        background-color: #1e1f20 !important;
        border: 1px solid #2d2f31 !important;
        border-radius: 4px 20px 20px 20px !important;
        padding: 0.9rem 1.3rem !important;
        font-size: 1rem !important;
        line-height: 1.7 !important;
        color: #e3e3e3 !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15) !important;
        width: fit-content !important;
        max-width: 100% !important;
    }
    
    /* ---- Custom User Bubble (rendered via HTML) ---- */
    .user-bubble-row {
        display: flex;
        justify-content: flex-end;
        align-items: flex-start;
        gap: 12px;
        margin-bottom: 1.25rem;
        padding: 0.4rem 0;
    }

    .user-bubble {
        background: linear-gradient(135deg, #2b3a67 0%, #1e294b 100%);
        border: 1px solid rgba(66, 133, 244, 0.25);
        color: #ffffff;
        border-radius: 20px 20px 4px 20px;
        padding: 0.9rem 1.3rem;
        font-size: 1rem;
        line-height: 1.7;
        max-width: 100%;
        width: fit-content;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        font-family: 'Plus Jakarta Sans', 'Google Sans', sans-serif;
        word-wrap: break-word;
    }

    .user-avatar {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        background: linear-gradient(135deg, #4285f4, #9b72cb);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1rem;
        flex-shrink: 0;
        color: #ffffff;
        font-weight: 700;
    }

    /* Custom Footer Styling */
    .footer-note {
        font-size: 0.8rem;
        color: #9e9e9e;
        text-align: center;
        margin-top: 3rem;
        border-top: 1px solid #2d2f31;
        padding-top: 1.5rem;
    }
    
    /* Constrain the main chat column width like ChatGPT/Claude */
    .block-container {
        max-width: 1200px !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        padding-top: 3rem !important;
        padding-bottom: 6rem !important;
        margin: 0 auto !important;
    }
    
    /* Make chat input bar match the chat area width exactly */
    div[data-testid="stBottom"] {
        background-color: #0f0f11 !important;
        padding-top: 1rem !important;
    }
    div[data-testid="stBottom"] > div {
        max-width: 1200px !important;
        margin: 0 auto !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }
    div[data-testid="stChatInput"] {
        border-radius: 28px !important;
        background-color: #1e1f20 !important;
        border: 1px solid #3c4043 !important;
        box-shadow: 0 8px 28px rgba(0,0,0,0.5) !important;
        width: 100% !important;
    }
    
    /* Token detail styling */
    .token-detail {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-size: 0.78rem;
        color: #9e9e9e;
        margin-top: 8px;
        background-color: rgba(255, 255, 255, 0.04);
        padding: 4px 10px;
        border-radius: 100px;
        border: 1px solid rgba(255, 255, 255, 0.06);
    }
</style>
""", unsafe_allow_html=True)

# --- State Management ---
if "sessions" not in st.session_state:
    # sessions: list of dicts {"id": int, "title": str, "history": list}
    st.session_state.sessions = [{"id": 0, "title": "New Chat", "history": []}]
if "active_session" not in st.session_state:
    st.session_state.active_session = 0
if "agent_history" not in st.session_state:
    st.session_state.agent_history = []

# Sync agent_history with active session
def get_active_session():
    for s in st.session_state.sessions:
        if s["id"] == st.session_state.active_session:
            return s
    return st.session_state.sessions[0]

def save_active_history():
    session = get_active_session()
    session["history"] = st.session_state.agent_history
    # Auto-title from first user message
    if session["title"] == "New Chat":
        for msg in session["history"]:
            if msg["role"] == "user":
                session["title"] = msg["content"][:40] + ("..." if len(msg["content"]) > 40 else "")
                break

# Load active session history
st.session_state.agent_history = get_active_session()["history"]
# --- Sidebar Configurations ---
st.sidebar.markdown(
    """
    <div style='text-align: center; margin-bottom: 1.5rem;'>
        <img src="https://img.icons8.com/nolan/96/artificial-intelligence.png" width="80"/>
        <h2 style='font-family: Google Sans; margin-top: 0.5rem; margin-bottom: 0px;'>AI Hub</h2>
        <p style='color: #9e9e9e; font-size: 0.85rem;'>Enterprise Multi-Agent Assistant</p>
    </div>
    """, 
    unsafe_allow_html=True
)

# API Endpoint Server Configuration
backend_url = "http://localhost:8000"

# --- Model Hyperparameters (Premium UI) ---
st.sidebar.markdown("<hr style='margin: 20px 0; opacity: 0.1;'>", unsafe_allow_html=True)
st.sidebar.markdown("""
<div style="display: flex; align-items: center; gap: 8px; margin-bottom: 1rem;">
    <span style="font-size: 1.3rem;">⚙️</span>
    <span style="font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1.2px; color: #8ab4f8; font-weight: 700; font-family: 'Google Sans', sans-serif;">Model Hyperparameters</span>
</div>
""", unsafe_allow_html=True)

# Temperature
st.sidebar.markdown("""
<div class="param-card">
    <div class="param-header">
        <span class="param-icon">🌡️</span>
        <span class="param-name">Temperature</span>
    </div>
</div>
""", unsafe_allow_html=True)
temperature = st.sidebar.slider("Temperature", min_value=0.0, max_value=2.0, value=0.7, step=0.1, label_visibility="collapsed")

# Max Tokens
st.sidebar.markdown("""
<div class="param-card">
    <div class="param-header">
        <span class="param-icon">📏</span>
        <span class="param-name">Max Output Tokens</span>
    </div>
</div>
""", unsafe_allow_html=True)
max_tokens = st.sidebar.slider("Max Tokens", min_value=256, max_value=8192, value=2048, step=256, label_visibility="collapsed")

# Top P
st.sidebar.markdown("""
<div class="param-card">
    <div class="param-header">
        <span class="param-icon">🎯</span>
        <span class="param-name">Top P (Nucleus Sampling)</span>
    </div>
</div>
""", unsafe_allow_html=True)
top_p = st.sidebar.slider("Top P", min_value=0.0, max_value=1.0, value=0.9, step=0.05, label_visibility="collapsed")

# --- Clear Chat ---
st.sidebar.markdown("<hr style='margin: 24px 0; opacity: 0.1;'>", unsafe_allow_html=True)
st.sidebar.markdown("""
<div style="display: flex; align-items: center; gap: 8px; margin-bottom: 0.75rem;">
    <span style="font-size: 1.1rem;">🗂️</span>
    <span style="font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1.2px; color: #9e9e9e; font-weight: 600;">Session</span>
</div>
""", unsafe_allow_html=True)
if st.sidebar.button("🧹  Clear Conversation", use_container_width=True):
    st.session_state.agent_history = []
    save_active_history()
    st.rerun()

# --- Chat History ---
st.sidebar.markdown("<hr style='margin: 24px 0; opacity: 0.1;'>", unsafe_allow_html=True)
st.sidebar.markdown("""
<div style="display: flex; align-items: center; gap: 8px; margin-bottom: 0.75rem;">
    <span style="font-size: 1.1rem;">💬</span>
    <span style="font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1.2px; color: #8ab4f8; font-weight: 700; font-family: 'Google Sans', sans-serif;">Chat History</span>
</div>
""", unsafe_allow_html=True)

# New Chat button
if st.sidebar.button("✨  New Chat", use_container_width=True):
    new_id = max(s["id"] for s in st.session_state.sessions) + 1
    st.session_state.sessions.insert(0, {"id": new_id, "title": "New Chat", "history": []})
    st.session_state.active_session = new_id
    st.session_state.agent_history = []
    st.rerun()

# Display session list
for session in st.session_state.sessions:
    is_active = session["id"] == st.session_state.active_session
    icon = "🟢" if is_active else "💭"
    label = session["title"] if session["title"] else "New Chat"
    btn_key = f"session_{session['id']}"
    if st.sidebar.button(f"{icon}  {label}", key=btn_key, use_container_width=True):
        # Save current session before switching
        save_active_history()
        st.session_state.active_session = session["id"]
        st.session_state.agent_history = session["history"]
        st.rerun()


# --- Helper: Render a user message bubble via raw HTML (right-aligned) ---
def render_user_bubble(text):
    """Renders a user chat bubble aligned to the right side using raw HTML."""
    import html as html_mod
    safe_text = html_mod.escape(text)
    st.markdown(f"""
    <div class="user-bubble-row">
        <div class="user-bubble">{safe_text}</div>
        <div class="user-avatar">U</div>
    </div>
    """, unsafe_allow_html=True)


# --- Main Presentation Layout ---
st.markdown(
    """
    <div class="gemini-title-container">
        <h1 class="gemini-title" style="font-size: 2.5rem;">Enterprise Multi-Agent AI Assistant</h1>
    </div>
    """, 
    unsafe_allow_html=True
)
st.markdown("<p class=\"gemini-subtitle\">A next-generation enterprise workspace. Communicate with advanced language models and trigger advanced multi-agent orchestrations with secure execution pipelines.</p>", unsafe_allow_html=True)

# --- Multi-Agent System ---
st.markdown("### 🤖 Multi-Agent Playfield")
st.caption("Leverage LangGraph workflows to route logic across highly specialized tools (e.g. secure calculations) to achieve complex operations.")
st.markdown("<br>", unsafe_allow_html=True)

# Agent Chat Container
agent_container = st.container()

with agent_container:
    # If no history, display a beautiful premium "Quick Start" grid
    if len(st.session_state.agent_history) == 0:
        st.markdown("""
        <div style="text-align: center; margin-top: 2rem; margin-bottom: 2rem;">
            <h2 style="font-family: 'Google Sans', sans-serif; font-weight: 500; font-size: 1.8rem; color: #ffffff;">How can I assist your workflow today?</h2>
        </div>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1.2rem; margin-bottom: 2rem;">
            <div class="google-card" style="padding: 1.2rem; margin-bottom: 0;">
                <h4 style="margin: 0 0 8px 0; color: #8ab4f8; font-size: 0.95rem; font-family: 'Google Sans';">⚡ Secure Calculator</h4>
                <p style="margin: 0; font-size: 0.85rem; color: #c4c7c5; line-height: 1.4;">Execute complex mathematical expressions with secure sandbox computations.</p>
            </div>
            <div class="google-card" style="padding: 1.2rem; margin-bottom: 0;">
                <h4 style="margin: 0 0 8px 0; color: #81c995; font-size: 0.95rem; font-family: 'Google Sans';">🔍 Multi-Agent Search</h4>
                <p style="margin: 0; font-size: 0.85rem; color: #c4c7c5; line-height: 1.4;">Route search queries dynamically across specialized agent roles.</p>
            </div>
            <div class="google-card" style="padding: 1.2rem; margin-bottom: 0;">
                <h4 style="margin: 0 0 8px 0; color: #fdd663; font-size: 0.95rem; font-family: 'Google Sans';">📈 Data Planning</h4>
                <p style="margin: 0; font-size: 0.85rem; color: #c4c7c5; line-height: 1.4;">Generate structured analysis logs with full mathematical verification.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Display existing agent interactions
        for msg in st.session_state.agent_history:
            if msg["role"] == "user":
                # User message: render as custom HTML on the RIGHT side
                render_user_bubble(msg["content"])
            else:
                # Assistant message: render via st.chat_message on the LEFT side
                with st.chat_message("assistant"):
                    st.markdown(msg["content"])
                    if "total_token" in msg:
                        st.markdown(f"""
                        <div class="token-detail">
                            <span>⚡ <b>Tokens:</b> {msg['total_token']}</span>
                            <span>•</span>
                            <span>⏱️ <b>Response:</b> {msg['time']}s</span>
                        </div>
                        """, unsafe_allow_html=True)

# Agent input
if agent_prompt := st.chat_input("Assign a complex workflow task (e.g., 'Compute 534 * 23 plus 85')...", key="agent_input_box"):
    # Display user task on the right
    with agent_container:
        render_user_bubble(agent_prompt)
    
    st.session_state.agent_history.append({"role": "user", "content": agent_prompt})
    save_active_history()
    
    # Send API request
    with st.spinner("Coordinating agents and tool executions..."):
        try:
            payload = {
                "message": agent_prompt,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "top_p": top_p
            }
            start_time = time.time()
            response = requests.post(f"{backend_url}/api/agent", json=payload, timeout=90)
            elapsed_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                text_response = data.get("response", "")
                total_token = data.get("total_token", 0)
                
                # Display agent response on the left
                with agent_container:
                    with st.chat_message("assistant"):
                        st.markdown(text_response)
                        st.markdown(f"""
                        <div class="token-detail">
                            <span>⚡ <b>Tokens:</b> {total_token}</span>
                            <span>•</span>
                            <span>⏱️ <b>Response:</b> {round(elapsed_time, 2)}s</span>
                        </div>
                        """, unsafe_allow_html=True)
                        
                st.session_state.agent_history.append({
                    "role": "assistant", 
                    "content": text_response,
                    "total_token": total_token,
                    "time": round(elapsed_time, 2)
                })
                save_active_history()
                st.rerun()
            else:
                st.error(f"Error {response.status_code}: {response.text}")
        except Exception as e:
            st.error(f"Connection failed: {str(e)}")

# --- Bottom Brand Footer ---
st.markdown(
    """
    <div class="footer-note">
        <p>Powered by <b>Enterprise AI</b> & LangGraph orchestrators. Enterprise Data Protection active.</p>
    </div>
    """, 
    unsafe_allow_html=True
)
