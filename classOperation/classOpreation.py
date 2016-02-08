# coding=utf-8

# new classOperation
class Animal:
    # Member
    color = 'green'
    weight = 10
    legs = 10
    shell = True
    mouth = 'big mouth'

    # Method
    def climb(self):
        print('Climbing')

    def run(self):
        print('Runing')

    def bite(self):
        print('Biting')

    def eat(self):
        print('Eating')

    def sleep(self):
        print('Sleeping')


t = Animal()
t.climb()


# Implement existed classOperation...clasee NewClass(BaseClass)
class MyList(list):
    pass


t = MyList()
t.append(1)
print(t)


class A:
    def fun(self):
        print('This is classOperation A!')


class B:
    def fun(self):
        print('This is classOperation B!')


a = A()
b = B()
a.fun()
b.fun()
