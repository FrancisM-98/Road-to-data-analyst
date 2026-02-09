import pandas as pd

# D&D characters data
characters_data = {
  'name': ['Thorne', 'Elira', 'Glim', 'Brug', 'Nyx', 'Kael', 'Mira', 'Drogan', 'Zara', 'Fenwick'],
  'race': ['Elf', 'Human', 'Gnome', 'Half-Orc', 'Tiefling', 'Dragonborn', 'Halfling', 'Dwarf', 'Aasimar', 'Goblin'],
  'class': ['Ranger', 'Cleric', 'Wizard', 'Barbarian', 'Rogue', 'Paladin', 'Bard', 'Fighter', 'Sorcerer', 'Warlock'],
  'level': [5, 3, 4, 2, 6, 7, 3, 5, 4, 2],
  'hp': [42, 28, 33, 25, 48, 56, 30, 44, 36, 24],
  'alignment': [
    'Chaotic Good', 'Lawful Good', 'Neutral', 'Chaotic Neutral', 'Chaotic Evil',
    'Lawful Neutral', 'Neutral Good', 'Neutral', 'Chaotic Good', 'Lawful Evil'
  ]
}

# Create the DataFrame
characters = pd.DataFrame(characters_data)

character_names = characters["name"]
print(character_names)

basic_stats = characters[['name', 'level', 'hp']]
print(basic_stats)

high_level = characters[characters['level'] >= 5]
print(high_level)

halfling_bards = characters[(characters['race'] == 'Halfling') & (characters['class'] == 'Bard')]
print(halfling_bards)

magic_users = characters[characters['class'].isin(['Wizard', 'Sorcerer', 'Warlock'])]
print(magic_users)

characters["hp_per_level"] = (characters["hp"] / characters["level"] * 20).round() / 20
print(characters[["name", "hp_per_level"]])

