# coding=utf-8
class A:
    x = 3


class B(A):
    pass


print issubclass(A, B)  # False

print(issubclass(B, A))  # True

print isinstance('str', object)

print('Has Attr: %s' % hasattr(A, 'x'))

print getattr(A, 'x')

setattr(A, 'x', 5)

print(getattr(A, 'x'))

delattr(A, 'x') # Attribute has been deleted

try:
    print(A.x)

except AttributeError as reason:
    print(reason.message)


class C:
    def __init__(self,size=10):
        self.size = size
    def getsize(self):
        return self.size
    def setsize(self,value):
        self.size = value
    def delsize(self):
        del self.size
    x=property(getsize,setsize,delsize,'This is x Property.')

c = C()
print c.x