def factorial(n):
    if n == 1:
        return 1
    else:
        return n * factorial(n - 1)


def factorialNormail(n):
    result = 1
    tempList = range(1, n + 1)
    for i in tempList:
        result *= i
    return result


print(factorial(4))
print(factorialNormail(3))

#迭代效率低下
def RabbitCount(n):
    if n == 1:
        return 1
    elif n == 2:
        return 1
    else:
        return RabbitCount(n - 2) + RabbitCount(n - 1)


print(RabbitCount(10))

# 效率比迭代高很多
def RabbitCountNormal(n):
    n1 = 1
    n2 = 1
    n3 = 1
    if n < 1:
        print("Number is Wrong! ")
        return -1

    while (n - 2) > 0:
        n3 = n2 + n1
        n1 = n2
        n2 = n3
        n -= 1

    return n3


print(RabbitCountNormal(10))
