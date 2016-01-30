from serpent_setup import *

code = '''\
data junk[](length, data[])

def saveData(key, data:arr):
    with location = ref(self.junk[key].data[0]):
        with end = len(data):
            with i = 0:
                while(i < end):
                    sstore(location + i, data[i])
                    i += 1
            self.junk[key].length = end
            return(key)

def loadData(key):
    with location = ref(self.junk[key].data[0]):
        with count = self.junk[key].length:
            with result = array(count):
                with i = 0:
                    while i < count:
                        result[i] = sload(location + i)
                        i += 1
                    return(result:arr)

def appendData(key, item):
    with temp = alloc(128):
        temp[0] = 0 #first data structure in the contract
        temp[1] = key
        temp[2] = 1 #second member of the structure
        temp[3] = 0
        with location = sha3(temp, items=4):
            temp[2] = 0 #first member of the structure
            with len = sha3(temp, items=3):
                with end = sload(len):
                    sstore(location + end, item)
                    sstore(len, end + 1)

def doubleData(key):
    with location = ref(self.junk[key].data[0]):
        with end = self.junk[key].length:
            with i = 0:
                while i < end:
                    sstore(location + i, sload(location + i) * 2)
                    i += 1
'''

PRINT(serpent.compile_to_lll(code))

s = t.state()
c = s.abi_contract(code)

data = range(10)

try:
    PRINT(c.saveData(1, data, profiling=True))
    PRINT(c.loadData(1, profiling=True))
    PRINT(c.appendData(1, 10, profiling=True))
    PRINT(c.loadData(1, profiling=True))
    PRINT(c.doubleData(1, profiling=True))
    PRINT(c.loadData(1, profiling=True))
except:
    PRINT(REDIRECT.getvalue())
