# Coding Challenge 2 - Part 5

letter_scores = {
    "aeioulnrst": 1,
    "dg": 2,
    "bcmp": 3,
    "fhvwy": 4,
    "k": 5,
    "jx": 8,
    "qz": 10
}

# User inputs word and makes it lowercase
word = input('Provide a word! ').lower()

# Create a list of word's letters
letters = list(word)

# Counts letter scores of word
count = 0
for i in letters:
    for key in letter_scores:
        if i in key:
            count += letter_scores[key]

print('The scrabble score for your word: ', count)
