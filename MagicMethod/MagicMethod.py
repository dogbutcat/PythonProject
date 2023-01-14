# coding=utf-8


class Rectangle:
    def __init__(self, x, y):  # MagicMethod
        self.x = x
        self.y = y

    def getPeri(self):
        return (self.x + self.y) * 2

    def getArea(self):
        return (self.x * self.y)


t = Rectangle(2, 3)
print(t.getArea(), t.getPeri())


class CapStr(str):
    def __new__(cls, string):
        string = string.upper()
        return str.__new__(cls, string)


print(CapStr('This is Test String!'))


class C:
    def __init__(self):
        print('This is __init__ Method!')

    def __del__(self): # After All Reference has deleted then it works
        print('This is __del__ Method')


c1=C()
c2=c1
c3=c2
del c1
print('c1 is deleted!')
# del c3
# print('c3 is deleted!')
# del c2
# print('c2 is deleted!')
# del c1
# print('c1 is deleted!')
