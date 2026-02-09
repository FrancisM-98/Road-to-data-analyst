import pandas as pd

contacts = {
    "name": ["Francis", "Mehdi","Chris","Raf"],
    "age": [27,26,25,24],
    "phone": ["079 915 67 27","079 234 19 21","079 111 22 33","076 800 11 42"],
    "colour" : ["Blue","Red","Green","Yellow"],
}

contacts_df = pd.DataFrame(contacts)

print(contacts_df)


