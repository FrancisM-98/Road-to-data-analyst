import datetime, Codédex.Chapter_Modules.bday_message as bday_message

today = datetime.date.today()
next_birthday = datetime.date(2026,6,24)

time_difference = today - next_birthday

if today == next_birthday :
    print (bday_message)
else :
    print(f"My next birthday is in {time_difference} days away!")

print(time_difference)