num = {1, 2, 3}
print(type(num))

num2 = {1, 2, 3, 3, 4, 5}
print(num2)

num3 = [1, 2, 3, 3, 5, 5, 1, 0]
tmp = []
for i in num3:
    if i not in tmp:
        tmp.append(i)

print(tmp)
# OR
print(list(set(num3)))

numset={1,2,3,4,5}
numset.add(6)
print('numset: ',numset)
frozenset(numset)
# numset.add(7)
set(numset)
numset.add(7)
print(numset)