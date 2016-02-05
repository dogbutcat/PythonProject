def MyFirstFunction():
    'This is inner Function'
    print("This is included in Function")

MyFirstFunction()

print(MyFirstFunction.__doc__)

def MySecondFunction(a="a",b="b"):
    print(a+b)

MySecondFunction("a1","b2")

def CollectPara(*para):
    print(len(para))
    print(type(para))

print(CollectPara(1,'a'))

def ReturnVal():
    return [1,"a",2]

print(ReturnVal())
