def discounts(price,rate):
    # print(old_price) #Exist
    old_price = 10
    print(old_price)
    return price*rate

old_price = float(input("Please Enter the Price: "))
rate = float(input("Please Enter the Rate: "))
new_price = discounts(old_price,rate)
print(old_price)
print(new_price)