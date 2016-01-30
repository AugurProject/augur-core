from serpent_setup import *

code1 = '''\
data junk[](length, data[])

def saveData(key, data:arr):
    self.junk[key].length = len(data)
    with i = 0:
        while i < len(data):
            self.junk[key].data[i] = data[i]
            i += 1

def loadData(key):
    with i = 0:
        with vals = array(self.junk[key].length):
            while i < len(vals):
                vals[i] = self.junk[key].data[i]
                i += 1
            return(vals:arr)

def appendData(key, item):
    self.junk[key].data[self.junk[key].length] = item
    self.junk[key].length += 1

def doubleData(key):
    with i = 0:
        while i < self.junk[key].length:
            self.junk[key].data[i] *= 2
            i += 1
'''

code2 = '''\
data junk[](length, data[])

def saveData(key, data:arr):
    with location = ref(self.junk[key].data[0]):
        with end = len(data):
            with i = 0:
                while(i < end):
                    sstore(location + 1,  data[i])
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
    with location = ref(self.junk[key].data[0]):
        with end = self.junk[key].length:
            sstore(location + end, item)
            self.junk[key].length = end + 1

def doubleData(key):
    with location = ref(self.junk[key].data[0]):
        with end = self.junk[key].length:
            with i = 0:
                while i < end:
                    sstore(location + i, sload(location + i) * 2)
                    i += 1
'''

code3 = '''\
data junk[](length, data[])

def saveData(key, data:arr):
    self.junk[key].length = len(data)
    save(self.junk[key].data[0], data, items=len(data))

def loadData(key):
    return(load(self.junk[key].data[0], items=self.junk[key].length):arr)

def appendData(key, item):
    with data = load(self.junk[key].data[0], items=self.junk[key].length):
        with new_data = array(len(data) + 1):
            mcopy(new_data, data, items=len(data))
            new_data[len(data)] = item
            save(self.junk[key].data[0], new_data, items=len(new_data))
            self.junk[key].length += 1

def doubleData(key):
    with i = 0:
        with vals = load(self.junk[key].data[0], items=self.junk[key].length):
            while i < self.junk[key].length:
                vals[i] *= 2
                i += 1
            save(self.junk[key].data[0], vals, items=len(vals))
'''

def code_test(code, name):
    s = t.state()
    c = s.abi_contract(code)
    key = 0xCAFEBABE

    data = range(10)
    table = SimpleTable(name + ' - data: ' + str(data),
                  ['', 'gas used', 'output', 'runtime'])
    r1 = c.saveData(key, data, profiling=True)
    table.add_row(['saveData', r1['gas'], r1['output'], r1['time']])
    r2 = c.loadData(key, profiling=True)
    table.add_row(['loadData', r2['gas'], r2['output'], r2['time']])
    r3 = c.appendData(key, 10, profiling=True)
    table.add_row(['appendData', r3['gas'], r3['output'], r3['time']])
    r4 = c.doubleData(key, profiling=True)
    table.add_row(['doubleData', r4['gas'], r4['output'], r4['time']])
    return table

def test_save_load():
    s = t.state()
    for i, code in enumerate((code1, code2, code3)):
        name = 'code%d'%(i+1)
        table = code_test(code, name)
        table.print_table()
        PRINT()        

if __name__ == '__main__':
    test_save_load()
