"""
Game Hub - Main Entry Point
A collection of fun party games!
"""
import streamlit as st

# Page config
st.set_page_config(
    page_title="Game Hub 🎮",
    page_icon="🎮",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for modern styling
st.markdown("""
<style>
    .main-title {
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.5rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        text-align: center;
        color: #6c757d;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    .game-card {
        background: linear-gradient(145deg, #1a1a2e 0%, #16213e 100%);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
        border: 1px solid rgba(102, 126, 234, 0.3);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .game-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 40px rgba(102, 126, 234, 0.3);
    }
    .game-title {
        color: #ffffff;
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .game-description {
        color: #a0a0a0;
        font-size: 1rem;
    }
    .game-emoji {
        font-size: 3rem;
        margin-bottom: 1rem;
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
        width: 100%;
    }
    .stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# Main content
st.markdown('<h1 class="main-title">🎮 Game Hub</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Sélectionnez un jeu pour commencer !</p>', unsafe_allow_html=True)

# Games list - Add new games here!
games = [
    {
        "name": "Devine le Nombre",
        "emoji": "🔢",
        "description": "Faites deviner un nombre (1-10) à vos amis en proposant un mot lié au thème !",
        "page": "1_Devine_le_Nombre"
    },
    # Add more games here in the future:
    # {
    #     "name": "Another Game",
    #     "emoji": "🎯",
    #     "description": "Description of the game",
    #     "page": "2_Another_Game"
    # },
]

# Display game cards
for game in games:
    st.markdown(f"""
    <div class="game-card">
        <div class="game-emoji">{game['emoji']}</div>
        <div class="game-title">{game['name']}</div>
        <div class="game-description">{game['description']}</div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button(f"Jouer à {game['name']}", key=game['page']):
        st.switch_page(f"pages/{game['page']}.py")

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #6c757d;'>🎉 Plus de jeux à venir bientôt !</p>",
    unsafe_allow_html=True
)
