def digui(i):
    if i == 1:
        return 1
    else:
        return digui(i-1)*i

a=digui(5)
print(a)