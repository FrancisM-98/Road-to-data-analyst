numbers = [57, 10, 82, 36, 89, 46, 13, 23, 92, 48]

def even_flag (num):
    return num % 2 == 0
def odd_flag (num):
    return num % 2 != 0

print(f"Original numbers: {numbers}")
print(f"Even numbers: {list(filter(even_flag, numbers))}")
print(f"Odd numbers: {list(filter(odd_flag, numbers))}")