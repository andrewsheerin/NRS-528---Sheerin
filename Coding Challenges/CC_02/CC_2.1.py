# Coding Challenge 2 - Part 1

list1 = [1, 2, 3, 6, 8, 12, 20, 32, 46, 85]
list2 = []

# Task 1
for i in list1:
    if i < 5:
        list2.append(i)
print(list2)

# Task 2
print([i for i in list1 if i < 5])
