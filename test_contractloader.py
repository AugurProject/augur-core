from load_contracts import ContractLoader
import dill
import cloudpickle
c = ContractLoader('src', 'controller.se', ['mutex.se', 'cash.se', 'repContract.se'])
c.recompile('test')

output = open('data.dill', 'wb')
dill.dump(c, output)
output.close()

output = open('data.cp', 'wb')
cloudpickle.dump(c, output)
output.close()

dill_file = open('data.dill', 'rb')
c = dill.load(dill_file)
dill_file.close()