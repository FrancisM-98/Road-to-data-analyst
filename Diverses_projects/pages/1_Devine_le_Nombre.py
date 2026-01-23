"""
Devine le Nombre - Party Game
Faites deviner un nombre en proposant un mot lié au thème !
"""
import streamlit as st
import random

# Page config
st.set_page_config(
    page_title="Devine le Nombre 🔢",
    page_icon="🔢",
    layout="centered"
)

# Themes list
THEMES = [
    "films", "animaux", "pays", "nourriture", "sports", 
    "musique", "histoire", "science", "technologie", "art", 
    "littérature", "artistes", "jeux vidéo", "célébrités", "marques"
]

# Custom CSS
st.markdown("""
<style>
    .game-header {
        text-align: center;
        margin-bottom: 2rem;
    }
    .title {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: 800;
    }
    .theme-card {
        background: linear-gradient(145deg, #1a1a2e 0%, #16213e 100%);
        border-radius: 20px;
        padding: 2rem;
        text-align: center;
        border: 2px solid rgba(240, 147, 251, 0.3);
        margin: 1rem 0;
    }
    .theme-label {
        color: #a0a0a0;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 0.5rem;
    }
    .theme-value {
        color: #ffffff;
        font-size: 2rem;
        font-weight: 700;
    }
    .number-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        border-radius: 20px;
        padding: 2rem;
        text-align: center;
        margin: 1rem 0;
    }
    .number-label {
        color: rgba(255,255,255,0.8);
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 0.5rem;
    }
    .number-value {
        color: #ffffff;
        font-size: 4rem;
        font-weight: 800;
    }
    .number-hidden {
        color: #ffffff;
        font-size: 2rem;
        font-weight: 600;
    }
    .instructions {
        background: rgba(102, 126, 234, 0.1);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1.5rem 0;
        border-left: 4px solid #667eea;
    }
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 30px;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
    }
</style>
""", unsafe_allow_html=True)

def generate_new_round():
    """Generate a new theme and number"""
    st.session_state.theme = random.choice(THEMES)
    st.session_state.number = random.randint(1, 10)
    st.session_state.show_number = False

# Initialize session state
if 'theme' not in st.session_state:
    generate_new_round()
if 'show_number' not in st.session_state:
    st.session_state.show_number = False

# Header
st.markdown('<div class="game-header">', unsafe_allow_html=True)
st.markdown('<h1 class="title">🔢 Devine le Nombre</h1>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Instructions
st.markdown("""
<div class="instructions">
    <strong>📋 Comment jouer :</strong><br>
    1. Un joueur voit le <strong>thème</strong> et la <strong>note</strong> (1-10)<br>
    2. Il propose un mot du thème qui représente cette note<br>
    3. Les autres joueurs devinent la note !<br><br>
    <em>Exemple : Thème "Artistes", Note 10 → "J.Cole" (car c'est un GOAT !)</em>
</div>
""", unsafe_allow_html=True)

# Game controls
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("🎲 Nouveau Thème", use_container_width=True):
        generate_new_round()
        st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# Display Theme Card
st.markdown(f"""
<div class="theme-card">
    <div class="theme-label">Thème</div>
    <div class="theme-value">🎯 {st.session_state.theme.upper()}</div>
</div>
""", unsafe_allow_html=True)

# Number display with button toggle (faster than toggle widget)
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    button_label = "🙈 Cacher la note" if st.session_state.show_number else "👁️ Afficher la note"
    if st.button(button_label, use_container_width=True, key="toggle_number"):
        st.session_state.show_number = not st.session_state.show_number
        st.rerun()

if st.session_state.show_number:
    st.markdown(f"""
    <div class="number-card">
        <div class="number-label">Note à faire deviner</div>
        <div class="number-value">{st.session_state.number}</div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="number-card">
        <div class="number-label">Note à faire deviner</div>
        <div class="number-hidden">🙈 Caché</div>
    </div>
    """, unsafe_allow_html=True)

# Back to hub button
st.markdown("<br>", unsafe_allow_html=True)
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("🏠 Retour au Hub", use_container_width=True):
        st.switch_page("GameHub.py")
