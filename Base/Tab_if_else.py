a=b=0
b=5
if a==b:
    if a<b:
        print(a)
    else:
        print(b)
a=a if a>b else b
print(a)