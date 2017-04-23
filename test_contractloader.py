from load_contracts import ContractLoader
import dill
c = ContractLoader('src', 'controller.se', ['mutex.se', 'cash.se', 'repContract.se'])
c.recompile('test')

output = open('data.dill', 'wb')
dill.dump(c, output)
output.close()

dill_file = open('data.dill', 'rb')
c = dill.load(dill_file)
dill_file.close()


from load_contracts import ContractLoader
import dill
c = ContractLoader('src', 'controller.se', ['mutex.se', 'cash.se', 'repContract.se'], None)
