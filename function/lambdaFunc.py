g = lambda x: 2 * x - 1

print(g(5))

g = lambda x, y: x + y
print(g(5, 5))

print(list(filter(None, [1, 0, 3, True, False])))

temp = range(0, 10, 2)


def odd(x):
    return x % 2


print(list(filter(odd, temp)))

print(filter(lambda x: x % 2, range(10)))
