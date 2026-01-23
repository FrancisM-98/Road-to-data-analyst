print("Surface area calculator")

shape = [
    "1) Square "
    "2) Rectangle "
    "3) Triangle "
    "4) Circle "
]

print(shape)
print("Which shape do you want to calculate the surface area of? (Enter the number)")
choice = input("Enter your choice: ")

if choice == "1":
    side = float(input("Enter the side length: "))
    print("The surface area of the square is: ", side * side)
elif choice == "2":
    length = float(input("Enter the length: "))
    width = float(input("Enter the width: "))
    print("The surface area of the rectangle is: ", length * width)
elif choice == "3":
    base = float(input("Enter the base length: "))
    height = float(input("Enter the height: "))
    print("The surface area of the triangle is: ", 0.5 * base * height)
elif choice == "4":
    radius = float(input("Enter the radius: "))
    print("The surface area of the circle is: ", 3.14 * radius * radius)
else:
    print("Invalid choice")
