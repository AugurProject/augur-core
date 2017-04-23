from load_contracts import ContractLoader
import pickle
c = ContractLoader('src', 'controller.se', ['mutex.se', 'cash.se', 'repContract.se'])
c.recompile('test')
output = open('data.pkl', 'wb')
pickle.dump(c, output)
output.close()

pkl_file = open('data.pkl', 'wb')
c = pickle.load(pkl_file)
pkl_file.close()