import streamlit as st
import time
import os
import json
import google.generativeai as genai

# --- Page Configuration (MUST BE FIRST) ---
st.set_page_config(
    page_title="NEON GENESIS // Script Architect",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for Cyberpunk Aesthetic ---
st.markdown("""
<style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Rajdhani:wght@300;500;700&display=swap');

    /* General App Styling */
    .stApp {
        background-color: #0e1117;
        color: #e0e0e0;
        font-family: 'Rajdhani', sans-serif;
    }

    /* Headings */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Orbitron', sans-serif;
        color: #00f3ff; /* Cyan Neon */
        text-shadow: 0 0 10px #00f3ff, 0 0 20px #00f3ff;
    }
    
    /* Inputs */
    .stTextInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: #1c1f26;
        color: #00f3ff;
        border: 1px solid #333;
        border-radius: 0px; 
    }
    .stTextInput input:focus {
        border-color: #ff00ff; /* Pink Neon */
        box-shadow: 0 0 5px #ff00ff;
    }

    /* Cards / Containers */
    div[data-testid="stMetricValue"] {
        font-family: 'Orbitron', sans-serif;
        color: #ff00ff;
        text-shadow: 0 0 5px #ff00ff;
    }

    /* Primary Button */
    .stButton button {
        background: linear-gradient(45deg, #ff00ff, #00f3ff);
        color: #000;
        font-family: 'Orbitron', sans-serif;
        font-weight: bold;
        border: none;
        border-radius: 0px;
        padding: 0.5rem 1rem;
        transition: all 0.3s ease;
        text-transform: uppercase;
        width: 100%;
        margin-top: 5px;
    }
    .stButton button:hover {
        transform: scale(1.02);
        box-shadow: 0 0 15px #ff00ff, 0 0 15px #00f3ff;
        color: #fff;
    }

    /* Radio Selection */
    .stRadio label {
        color: #00f3ff !important;
        font-family: 'Rajdhani', sans-serif;
        font-size: 1.2rem;
    }

    /* Text Area */
    .stTextArea textarea {
        background-color: #111;
        color: #00ff9d; /* Matrix Green */
        font-family: 'Courier New', monospace;
        border: 1px solid #333;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #0b0d10;
        border-right: 1px solid #333;
    }
</style>
""", unsafe_allow_html=True)

# --- State Management ---
if 'history' not in st.session_state:
    st.session_state.history = []
if 'step' not in st.session_state:
    st.session_state.step = 1 # 1=Input, 2=Selection, 3=Output
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = []
if 'selected_angle_index' not in st.session_state:
    st.session_state.selected_angle_index = 0
if 'generated_script' not in st.session_state:
    st.session_state.generated_script = ""
if 'current_topic' not in st.session_state:
    st.session_state.current_topic = ""

# --- Helper Functions (Gemini API) ---
def get_gemini_response(model_name, prompt):
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"API Error: {e}")
        return None

def generate_angles_ai(topic, model_name, api_key, language):
    genai.configure(api_key=api_key)
    
    prompt = f"""
    Act as a Viral Content Strategist. I need 6 distinct video concepts for the topic: "{topic}".
    Language Context: {language}
    
    Return ONLY a raw JSON array. No markdown formatting, no code blocks.
    The array must contain exactly 6 objects, corresponding to these angles:
    1. The Contrarian (Flip the idea, go against grain)
    2. The Dark Psychology (Power, manipulation, hidden truths)
    3. The Historical (Connect to Spartan, Samurai, Stoics, etc)
    4. The Scientific (Biology, Dopamine, Evolution)
    5. The Aggressive (Direct attack on weakness, wake up call)
    6. The Story (A short parable or metaphor)

    Each object must have these keys:
    - "name": (String, one of the angle names above)
    - "icon": (String, a relevant emoji)
    - "title": (String, a viral clickbait title in {language})
    - "desc": (String, very brief 1-sentence description of the angle)
    - "viral_score": (Integer, predictable viral score 0-100 based on current trends)
    """
    
    response_text = get_gemini_response(model_name, prompt)
    
    if response_text:
        # Clean up potential markdown formatting from AI
        clean_text = response_text.replace("```json", "").replace("```", "").strip()
        try:
            return json.loads(clean_text)
        except json.JSONDecodeError:
            st.error("Failed to parse AI response. Raw output shown below.")
            st.text(response_text)
            return []
    return []

def generate_script_ai(topic, angle_data, model_name, api_key, language):
    genai.configure(api_key=api_key)
    
    angle_name = angle_data['name']
    title = angle_data['title']
    
    # Dynamic System Instruction
    if language == "Hinglish":
        system_role = "You are a viral scriptwriter for Indian YouTube Shorts. Write strictly in Hinglish (Hindi + English mix). Use Hindi for emotion and English for technical terms. Example: 'Focus ka matlab sirf kaam karna nahi hai.'"
    else:
        system_role = "You are a world-class viral scriptwriter. Write in punchy, high-retention English."
    
    prompt = f"""
    {system_role}
    
    Act as a Ghostwriter. Write a viral short-form video script (TikTok/Reels/Shorts).
    TOPIC: {topic}
    ANGLE: {angle_name}
    TITLE: {title}
    
    STRICT FORMAT GUIDELINES:
    - CRITICAL GLOBAL RULE: Do NOT include visual cues, camera angles, [brackets], (parentheses), or asterisks. Write ONLY the spoken words to be narrated.
    - Pure Spoken Text Only.
    
    STRUCTURE:
    Use exactly these headers:
    [HOOK]
    (The opening line to stop the scroll)
    
    [BODY]
    (The main value, story, or argument)
    
    [CTA]
    (The closing call to action)
    
    Tone: Matches the '{angle_name}' vibe strictly.
    """
    
    return get_gemini_response(model_name, prompt) or "Error generating script."

# --- Sidebar: Configuration ---
st.sidebar.title("⚙️ NEURAL LINK")

# Auto-Key Logic
secrets_path = os.path.join(".streamlit", "secrets.toml")
api_key = None

# Check secrets
if os.path.exists(secrets_path):
    try:
        api_key_from_secrets = st.secrets.get("GOOGLE_API_KEY")
        if api_key_from_secrets and api_key_from_secrets != "PASTE_YOUR_KEY_HERE":
            api_key = api_key_from_secrets
            st.sidebar.success("🔑 API Key Detected from Secrets")
        elif api_key_from_secrets == "PASTE_YOUR_KEY_HERE":
             st.sidebar.warning("⚠️ Please configure .streamlit/secrets.toml")
    except FileNotFoundError:
        pass

# Fallback to manual input
if not api_key:
    api_key = st.sidebar.text_input("Enter Gemini API Key", type="password", help="Get key from aistudio.google.com")

st.sidebar.markdown("### 🧠 SELECT AI BRAIN")
model_choice = st.sidebar.selectbox(
    "Model",
    [
        ("Gemini 3 Pro (The Mastermind)", "gemini-3-pro-preview"),
        ("Gemini 2.5 Pro (The Storyteller)", "gemini-2.5-pro"),
        ("Gemini 2.5 Flash (The Speedster)", "gemini-2.5-flash"),
    ],
    format_func=lambda x: x[0],
    index=2 # Default to Flash
)
selected_model_value = model_choice[1]

# Language Selector
st.sidebar.markdown("### 🗣️ SELECT LANGUAGE")
language = st.sidebar.selectbox(
    "Language",
    ["Hinglish", "English"],
    index=0
)

st.sidebar.markdown("---")
st.sidebar.title("💾 MEMORY BANK")

if st.sidebar.button("RESET SYSTEM"):
    st.session_state.step = 1
    st.session_state.generated_script = ""
    st.rerun()

if st.session_state.history:
    for item in reversed(st.session_state.history):
        with st.sidebar.expander(f"{item['timestamp']} | {item['angle']}"):
            st.write(f"**Topic:** {item['topic']}")
            st.write(f"**Score:** {item['score']}")
else:
    st.sidebar.caption("No analysis records found.")

# --- Main Interface ---
# Full width for writer focus
st.title("NEON GENESIS // SCRIPT ARCHITECT")
st.caption(f"CONNECTED TO: {selected_model_value.upper()} | MODE: {language.upper()}")
st.markdown("##")

if not api_key:
    st.warning("⚠️ SYSTEM PAUSED: API KEY REQUIRED IN SIDEBAR OR SECRETS.TOML")
    st.stop()

# ==========================================
# PHASE 1: INPUT
# ==========================================
if st.session_state.step == 1:
    st.markdown("### 📡 TARGET ACQUISITION")
    topic = st.text_input("ENTER CORE TOPIC", placeholder="e.g. Motivation, The Matrix, Focus...")
    
    if st.button("INITIATE 6-ANGLE ANALYSIS"):
        if topic:
            with st.spinner(f"TRANSMITTING TO {selected_model_value.upper()}..."):
                results = generate_angles_ai(topic, selected_model_value, api_key, language)
                if results and len(results) == 6:
                    st.session_state.analysis_results = results
                    st.session_state.current_topic = topic
                    st.session_state.step = 2
                    st.rerun()
                elif results:
                     st.error("AI returned incomplete data. Try again.")
        else:
            st.error("INPUT REQUIRED.")

# ==========================================
# PHASE 2: SELECTION
# ==========================================
elif st.session_state.step == 2:
    st.markdown(f"### 🧬 ANALYSIS COMPLETE: '{st.session_state.current_topic.upper()}'")
    st.caption("SELECT THE MOST VIRAL VECTOR TO PROCEED")
    
    results = st.session_state.analysis_results
    
    # Grid Layout for Cards
    c1, c2, c3 = st.columns(3)
    c4, c5, c6 = st.columns(3)
    columns = [c1, c2, c3, c4, c5, c6]
    
    selected_idx = st.radio(
        "Select Vector:", 
        options=range(len(results)),
        format_func=lambda x: f"{results[x]['name']} (Score: {results[x]['viral_score']})",
        label_visibility="collapsed",
        key="angle_selection_radio"
    )

    # Display Cards
    for i, col in enumerate(columns):
        angle = results[i]
        with col:
            # Highlight selected
            border_color = "#ff00ff" if i == selected_idx else "#333"
            
            st.markdown(f"""
            <div style="border: 1px solid {border_color}; padding: 15px; background: #151820; margin-bottom: 10px; height: 100%;">
                <h3 style="margin:0; font-size: 1.2rem;">{angle['icon']} {angle['name']}</h3>
                <p style="font-size: 0.9rem; color: #aaa; margin-bottom: 5px; min-height: 40px;">{angle['desc']}</p>
                <div style="font-weight: bold; font-size: 1.1rem; color: #fff; margin-bottom: 10px;">{angle['title']}</div>
                <hr style="border-color: #333;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="color: #00f3ff;">VIRAL SCORE</span>
                    <span style="font-size: 1.5rem; color: #ff00ff; font-family: 'Orbitron';">{angle['viral_score']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    if st.button("⚡ GENERATE MASTER DRAFT ⚡"):
        st.session_state.selected_angle_index = selected_idx
        st.session_state.step = 3
        st.rerun()
        
    if st.button("BACK TO SEARCH"):
        st.session_state.step = 1
        st.rerun()

# ==========================================
# PHASE 3: OUTPUT (WRITER MODE)
# ==========================================
elif st.session_state.step == 3:
    angle_data = st.session_state.analysis_results[st.session_state.selected_angle_index]
    
    # Generate Only If Not Already Generated (or assume re-gen on entry)
    if not st.session_state.generated_script:
        with st.spinner("WRITING MASTER DRAFT..."):
            script = generate_script_ai(st.session_state.current_topic, angle_data, selected_model_value, api_key, language)
            st.session_state.generated_script = script
            
            # Save to History
            st.session_state.history.append({
                "topic": st.session_state.current_topic,
                "angle": angle_data['name'],
                "score": angle_data['viral_score'],
                "timestamp": time.strftime("%H:%M")
            })

    st.markdown(f"### 📝 THE MASTER DRAFT: {angle_data['name'].upper()}")
    st.caption(f"Topic: {st.session_state.current_topic} | Title: {angle_data['title']}")
    
    # Editable Text Area
    edited_script = st.text_area(
        "The Master Draft (Editable)", 
        value=st.session_state.generated_script, 
        height=600,
        label_visibility="visible" # Explicitly requested
    )
    
    st.markdown("### 📋 COPY TO CLIPBOARD")
    st.code(edited_script, language="text")
        
    if st.button("START NEW ANALYSIS"):
        st.session_state.step = 1
        st.session_state.generated_script = ""
        st.rerun()
