import random, functools

prefixes = ['Mystic', 'Golden', 'Dark', 'Shadow', 'Silver']
suffixes = ['storm', 'song', 'fire', 'blade', 'whisper']

def create_fantasy_name(list_1, list_2):
  return random.choice(list_1) + ' ' + random.choice(list_2)

def capitalize_suffix(name):
  name = name.capitalize()
  return name

# Capitalize suffixes using map and store back in suffixes
suffixes = list(map(capitalize_suffix, suffixes))

# Generate 10 fantasy names using list comprehension
random_names = [create_fantasy_name(prefixes, suffixes) for _ in range(10)]

def fire_in_name(name):
  return 'Fire' in name

def concatenate_names(name1, name2):
  return name1 + ", " + name2

# Filter names containing 'Fire'
filtered_names = list(filter(fire_in_name, random_names))

def display_name_info():
  print("Generated Fantasy Names:")
  for name in random_names:
    print(name)
  
  print("\nNames with 'Fire':")
  print(filtered_names)
  
  print("\nConcatenated Fire Names:")
  if filtered_names:
      # Reduce filtered names into a single string
      reduced_names = functools.reduce(concatenate_names, filtered_names)
      print(reduced_names)
  else:
      print("No names with 'Fire' to concatenate.")

# Call the display function
display_name_info()
