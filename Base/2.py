import random

target = random.randint(1,10)
temp = input('Please Enter an Number: ')
num = int(temp)
while 1==1:
    if num == target:
        print('You Enter a True Number!')
        break
    elif num > target:
        print('The Number is larger than Target')
    else:
        print('The Number is smaller than Target')
    num = input('Please Enter another Number: ')