import math

player = {'Name': 'Francis', 'Age': 27, 'Country': 'Swiss', 'Rank': 'Ascendant 1', 'Points': 1000}
player_2 = {'Name': 'John', 'Age': 24, 'Country': 'Italy', 'Rank': 'Diamond 1', 'Points': 750}
player_3 = {'Name': 'Alice', 'Age': 20, 'Country': 'France', 'Rank': 'Diamond 2', 'Points': 650}

print(player)
print(player_2)
print(player_3)

# Create a list of all players
players = [player, player_2, player_3]

# Loop through and print each player's country
for p in players:
    print(p['Country'])

average_points = math.floor(sum(p['Points'] for p in players) / len(players))
print(average_points)
