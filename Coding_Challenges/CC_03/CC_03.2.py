# 2. Push sys.argv to the limit
# Construct a rudimentary Python script that takes a series of inputs as a command from a bat file using sys.argv,
# and does something to them. The rules:
#
# 1. Minimum of three arguments to be used.
# 2. You must do something simple in 15 lines or less within the Python file.
# 3. Print or file generated output should be produced.

# This script takes three arguments from the batch file 'CC_03.2.bat' and orders them alphabetically, regardless of case
import sys

sorted_list = sorted([str(sys.argv[1]).lower(), str(sys.argv[2]).lower(), str(sys.argv[3]).lower()])

print('Your ordered list of words is: ' + str(sorted_list[0]) + ', ' + str(sorted_list[1]) + ', ' + str(sorted_list[2]))

