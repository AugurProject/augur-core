from serpent_setup import *

code = '''\
def delete(data:arr, index):
    mcopy(data+(items=index), data+(items=(index+1)), items=(len(data) - index - 1))
    shrink(data, len(data) - 1)
    return(data:arr)
'''

s = t.state() #t is in serpent_setup.py
c = s.abi_contract(code)
data = range(20)
indeces = [0, 1, 14, 18, 19]

PRINT('serpent code:')
PRINT(code)
PRINT()
PRINT('lll:')
PRINT(serpent.compile_to_lll(code))

for index in indeces:
    PRINT('Test index %d' % index)
    PRINT('before delete:', data) #PRINT is defined in serpent_setup.py
    result = c.delete(data, index)
    PRINT('after delete: ', result)
    copy = data[:]
    copy.pop(index)
    PRINT('expected:     ', copy)
    if copy == result:
        PRINT(PASSED) #PASSED and FAILED are defined in serpent_setup.py
    else:
        PRINT(FAILED)
    
