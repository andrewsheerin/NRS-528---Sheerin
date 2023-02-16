# Coding Challenge 2 - Part 2

list_a = ['dog', 'cat', 'rabbit', 'hamster', 'gerbil']
list_b = ['dog', 'hamster', 'snake']

# Task 1
same = []
for i in list_a:
    if i in list_b:
        same.append(i)

print('Items that are present in both lists are: ', same)

# Task 2
not_same = []
for i in list_a:
    if i not in list_b:
        not_same.append(i)

for i in list_b:
    if i not in list_a:
        not_same.append(i)

print('Items that do not overlap are: ', not_same)
