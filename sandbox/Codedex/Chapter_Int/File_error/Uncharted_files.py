sent_message = "Hey there! This is a secret message!"

with open("sent_message.txt", "w") as file:
    file.write(sent_message)

with open("sent_message.txt", "r+") as file:
    original_message = file.read()
    print(original_message)
    file.seek(0)
    unsent_message = "This message has been unsent."
    file.write(unsent_message)
    file.truncate()
    file.seek(0)
    print(file.read())