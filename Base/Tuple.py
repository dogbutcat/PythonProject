
tuple1=(1,2,3,4.5)
tuple2=tuple1
# tuple1[1]=44 #This is not Allowed for Tuple Array
print(type(tuple1))
# This is for tuple insertion
tuple1=tuple1[:3]+('temp',)+tuple1[3:]
print(tuple2)