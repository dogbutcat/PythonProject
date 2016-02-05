# This is a Single Type Array
member1 = ['Array1', 'Array2', 'Array3']
print(member1)
# This is a Mixture Array
member2 = ['A', 2, True, 'End']
print(member2)
# This is a Empty Array
empty = []
print(empty)
# This is Used for Append
member1.append('Array4')
print(len(member1))
# This is Used for Extend
member2.extend(['True', False])
print(member2)
# This is Used for Insert
member1.insert(0, 'Array4')
print(member1)
# This is Used for Select Index
print(member1[0])
# This is Used for Remove Index
member1.remove('Array4')
print(member1)
# This is Array Compare
print(member1 < member2)
# This is Used for Array Addition
member3 = member1 + member2
print(member3)

member3 = member1 * 3
print(member3)
# This is Used for Array finding
print('Array' in member1)
print('Array2' in member1)
#This is Used for Array
member4 = [1,2,['True','False'],'End']
for i in member4:
    if type(i) == list:
        for j in i:
            if 'True' == j:
                print(member4.index(i))
                break
            else:
                continue
