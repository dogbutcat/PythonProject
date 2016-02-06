import pickle

rdtxt = open('debug1.txt')
wrtxt = open('pickle_list.pkl', 'wb')

tempList = list(rdtxt)
# print(tempList)
pickle.dump(tempList, wrtxt)
rdtxt.close()
wrtxt.close()

rdtxt = open('pickle_list.pkl', 'rb')
for each_line in rdtxt:
    print(each_line)
rdtxt.seek(0, 0)
targetList = pickle.load(rdtxt)
print(targetList)
rdtxt.close()
