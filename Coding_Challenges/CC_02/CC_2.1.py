# 1. List values
# Using this list:
#
# [1, 2, 3, 6, 8, 12, 20, 32, 46, 85]
# You need to do two separate things here and report both in your Python file. You should have two solutions in this
# file, one for item 1 and one for item 2. Item 2 is tricky so if you get stuck try your best (no penalty), for a
# hint check out the solution by desiato here.
#
# Make a new list that has all the elements less than 5 from this list in it and print out this new list.
# Write this in one line of Python (you do not need to append to a list just print the output).

list1 = [1, 2, 3, 6, 8, 12, 20, 32, 46, 85]
list2 = []

# Task 1
for i in list1:
    if i < 5:
        list2.append(i)
print(list2)

# Task 2
print([i for i in list1 if i < 5])
