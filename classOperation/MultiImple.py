# coding=utf-8
class base1:
    def func(self):
        print('This is base1.func!')

class base2:
    def func1(self):
        print('This is base2.func!')

class Imp(base1,base2):
    pass

t = Imp()
t.func()
t.func1()

p=Imp()
p.func()
p.func1()
