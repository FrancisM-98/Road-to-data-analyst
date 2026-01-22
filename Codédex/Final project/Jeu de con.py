# Génération code de base du jeu
import random

themes = ["films", "animaux", "pays", "nourriture", "sports", "musique", "histoire", "science", "technologie", "art", "littérature"]
note = random.randint(1, 10)
theme_choisi = random.choice(themes)
print(f"Thème attribué : {theme_choisi}, Note attribuée : {note}")
print("Faites deviner le thème attribué en donnant un mot du thème qui correspondrait le mieux à la note attribuée.")


