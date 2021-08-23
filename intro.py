def fibonacci(number):

    if(number == 0):
        return 0
    elif(number == 1 or number == 2):
        return 1
    else:
        return fibonacci(number-1)+fibonacci(number-2)

broj = fibonacci(9)
print (broj)
