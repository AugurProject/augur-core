def subsets(lst):
    if lst == []:
        return [[]]
    head = lst[-1]
    rest = subsets(lst[:-1])
    return rest + [s + [head] for s in rest]

print subsets(range(4))
