# Coding Challenge 2.py - Part 3

# Task 1
string = 'hi dee hi how are you mr dee'

# split string into words and create dictionary to store words and count
words = string.split()
word_dict = {}

# fill dictionary with words and count
for i in words:
    if i in word_dict:
        word_dict[i] += 1
    else:
        word_dict[i] = 1

# print the key and value from dictionary
items = word_dict.items()
for key, value in items:
    print(key, value)


