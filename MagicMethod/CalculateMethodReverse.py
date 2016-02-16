# coding=utf-8
class Rint(int):
    def __radd__(self, other):
        return int.__sub__(self, other)

    def __rsub__(self, other):
        return int.__sub__(self, other)

    def __pos__(self):
        return self + 1

    def __neg__(self):
        return self - 1


a = Rint(4)
b = Rint(6)
print(1 - a)
print(a + b)
print(-b)
