count = 5


def MyFunc():
    global count
    count = 10
    print(count)


MyFunc()
print(count)


def fun1():
    print("fun1 is called")

    def fun2():
        print("fun2 is called")

    fun2()


fun1()

def funx(x):
    def funy(y):
        return x*y
    return funy

print(funx(5)(8))

def funx1(x):
    def funy(y):
        def funz(z):
            return x*y*z
        return funz
    return funy

print(funx1(5)(8)(10))