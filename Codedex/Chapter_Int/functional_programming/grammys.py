import functools
# List of songs with their durations (in minutes)
playlist = [('What Was I Made For?', 3.42), ('Just Like That', 5.05), ('Song 3', 6.55), ('Leave The Door Open', 4.02), ('I Can\'t Breath', 4.47), ('Bad Guy', 3.14)]

def minutes_to_seconds(x):
    minutes = int(x[1])
    seconds = (x[1] - minutes) * 100
    return int(minutes * 60 + round(seconds))

def longer_than_five_minutes(song):
    return minutes_to_seconds(song) > 300

print(list(filter(longer_than_five_minutes, playlist)))

def add_durations(acc, song):
    return acc + minutes_to_seconds(song)

total_seconds = functools.reduce(add_durations, playlist, 0)

minutes = total_seconds // 60
seconds = total_seconds % 60

print(f"{minutes}:{seconds:02d}")
