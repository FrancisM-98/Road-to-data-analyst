# Génération code de base du jeu
import random

themes = ["films", "animaux", "pays", "nourriture", "sports", "musique", "histoire", "science", "technologie", "art", "littérature"]
note = random.randint(1, 10)
theme_choisi = random.choice(themes)
print(f"Thème attribué : {theme_choisi}, Note attribuée : {note}")
print("Faites deviner le thème attribué en donnant un mot du thème qui correspondrait le mieux à la note attribuée.")

# Website for the Final project
import streamlit as st
import random
st.title("Devine la note du thème !")
st.write("Bienvenue dans le jeu Devine la note du thème !")
st.write("L'objectif est de deviner la note attribuée à un thème donné en proposant des mots associés à ce thème.")
st.button("Commencer une nouvelle partie")
