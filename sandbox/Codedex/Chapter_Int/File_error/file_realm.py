liked_songs = {
    "7 minutes drill": "j.cole",
    "21 questions": "50 cent",
    "black and yellow": "snoop dogg",
    "monster": "21 savage",
    "luther": "Kendrick Lamar",
    "On BS": "Drake"
}


def write_liked_songs(liked_songs, file_name):
    file = open(file_name, "w")
    file.write(str(liked_songs))
    file.close()

write_liked_songs(liked_songs, "liked_songs.txt")

    