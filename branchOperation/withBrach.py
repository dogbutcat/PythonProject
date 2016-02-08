# coding=utf-8
try:
    with open('data.txt','r') as f:
        for each_line in f:
            print(each_line)
except OSError as reason:
    print(reason.message)