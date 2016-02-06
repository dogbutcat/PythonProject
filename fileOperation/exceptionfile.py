try:
    name = open('debug.txt')
    raise EOFError('a','b')
    for each_line in name:
        print(name)
    name.close()

except Exception as ex: # except OSError as ... # except (OSError,TypeError) as ...
    print(ex)
# finally:R