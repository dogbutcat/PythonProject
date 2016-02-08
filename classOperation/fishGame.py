# coding=utf-8

import random as r

class fish:
    def __init__(self):
        self.x = r.randint(0,10)
        self.y = r.randint(0,10)

    def move(self):
        self.x-=1
        print('My Postion is: ',self.x,self.y)

class Goldfish(fish):
    pass

class Carp(fish):
    pass

class Salmon(fish):
    pass

class Shark(fish):
    def __init__(self): # By default, it will override the Base function
        # fish.__init__(self) # Add x to Impletment No self would be Error
        # super().__init__() # in Python 3
        self.hungry =True

    def eat(self):
        if self.hungry == True:
            print('Need to Eat')
            self.hungry=False
        else:
            print('That\'s Enough!')

f = fish()
f.move()

s = Shark()
s.move()