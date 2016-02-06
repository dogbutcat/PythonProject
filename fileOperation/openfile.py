txt = open('debug1.txt')
print(txt.read(10))
(txt.seek(1, 0))
tmp = list(txt)
# print(tmp)
for each_line in tmp:
    print(each_line)
print('\n\n')
txt.seek(0,0)
for each_line in txt:
    print(each_line)
txt.close()

txt = open('new.txt','w')
txt.write('Hello,Test')
txt.close()

txt = open('new.txt')
for each_line in txt:
    print(each_line)