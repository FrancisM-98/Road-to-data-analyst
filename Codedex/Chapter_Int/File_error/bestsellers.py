import csv 

bestsellers = []

with open("bestseller - sheet1.csv", "r", newline="", encoding="utf-8") as file:
    csv_reader = csv.DictReader(file)
    for row in csv_reader:
        bestsellers.append(row)
        print(f"Book: {row['Book']}, Sales: {row['sales in millions']}")


with open("bestseller_info.csv", "w", newline="", encoding="utf-8") as file:
    csv_writer = csv.writer(file)
    csv_writer.writerow(["Book", "Sales in millions"])
    for row in bestsellers:
        csv_writer.writerow([row['Book'], row['sales in millions']])
