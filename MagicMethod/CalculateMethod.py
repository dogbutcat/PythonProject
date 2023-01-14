# coding=utf-8
class New_int(int):
    def __add__(self, other):
        return int.__sub__(self, other)

    def __sub__(self, other):
        return int.__add__(self, other)

        # def __new__(cls):
        #     return int.__new__(cls,0)

        # def __new__(cls, other):
        #     return int.__new__(cls, other)
        #
        # def __new__(cls):
        #     return int.__new__(cls,0)


b = a = New_int()
# a.__add__(5) # Error
b = New_int(5)
print(b)
# b = New_int(6)
print(type(b))
print(a + b)
