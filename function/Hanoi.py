def hanoi(n, x, y, z):
    if n == 1:
        print(x, '->', y) # Direction
    else:
        # Move n-1 from Start to Middle
        hanoi(n - 1, x, z, y)
        print(x, '->', y) # Last One Move to End
        #   Move n-1 from Middle to End
        hanoi(n - 1, z, y, x)

n=4
hanoi(n,'x','y','z')