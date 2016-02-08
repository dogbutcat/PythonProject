# coding=utf-8
try:
    print(int('123'))

except ValueError as reason:
    print('Error' + reason)
else:
    print('Nothing is except')

print('<hr>')

try:
    print(int('str'))

except ValueError as reason:
    print('Error! ' + reason.message)
else:
    print('Nothing is except') # Dont deal this After Exception