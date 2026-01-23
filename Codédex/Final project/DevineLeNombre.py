# Génération code de base du jeu
import random

themes = ["films", "animaux", "pays", "nourriture", "sports", "musique", "histoire", "science", "technologie", "art", "littérature"]

# Website for the Final project
import streamlit as st
import random

def play():
    theme_choisi = random.choice(themes)
    note = random.randint(1, 10)
    st.session_state.theme_choisi = theme_choisi
    st.session_state.note = note

st.title("Devine la note du thème !")
st.write("Bienvenue dans le jeu Devine la note du thème !")
st.write("L'objectif est de deviner la note attribuée à un thème donné en proposant des mots associés à ce thème.")
st.write("Cliquez sur 'Play' pour commencer une nouvelle partie.")

# Initialize game started flag
if 'game_started' not in st.session_state:
    st.session_state.game_started = False

with st.container():
    # Center the button horizontally using columns
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("Play"):
            play()  # Call the play function to generate and display new theme/note
            st.session_state.game_started = True

# Display theme and note full-width after game starts
if st.session_state.game_started:
    st.write(f"Thème attribué : {st.session_state.theme_choisi}")
    st.write(f"Note attribuée : {st.session_state.note}")
    st.write("Faites deviner le thème attribué en donnant un mot du thème qui correspondrait le mieux à la note attribuée.")
            
    