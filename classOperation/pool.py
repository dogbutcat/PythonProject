# coding=utf-8
class Fish:
    def __init__(self,x):
        self.num = x

class Turtle:
    def __init__(self,x):
        self.num = x

class Pool:

    turtle = 0
    fish = 0
    def __init__(self,x,y):
        self.turtle = Turtle(x)
        self.fish=Fish(y)

    def print_num(self):
        print("Turtle: %d Fish: %d" % (self.turtle.num,self.fish.num))

    # @staticmethod
    def print_num():
        print("Turtle: %d Fish: %d" % (Pool.turtle,Pool.fish))

t = Pool(1,2)
t.print_num()

Pool.print_num()