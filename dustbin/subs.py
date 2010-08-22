
def subred(one, two):
    """reduce function for finding common starts to a set of strings"""
    res = []
    i = 0
    for i, s in enumerate(one):
        if two[i] != s:
            break
        res.append(s)
    return ''.join(res)

if __name__ == '__main__':
    tdata = ['one', 'only', 'on top']
    print(reduce(subred, tdata))
