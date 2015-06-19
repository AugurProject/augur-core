import json
from time import strftime, gmtime
from http import simple_server
from ethereum import tester

STATE = tester.state()
RESPONSE = '''\
HTTP/1.1 200 OK\r
Date: %(date)s\r
Content-Type: application/json\r
Content-Length: %(length)d\r
\r
%(body)s'''

def get_time():
    return strftime('%a, %d %b %Y %T GMT', gmtime()) 

INVALID_REQUEST = -32600
METHOD_NOT_FOUND = -32601
INVALID_PARAMS = -32602
INTERNAL_ERROR = -32603
PARSE_ERROR = -32700
ERRORS = {
    INVALID_REQUEST:'Invalid Request',
    METHOD_NOT_FOUND:'Method not found',
    INVALID_PARAMS:'Invalid params',
    INTERNAL_ERROR:'Internal error',
    PARSE_ERROR:'Parse error',
}

def make_response(type, result, id=None):
    obj = {'jsonrpc':'2.0', type:result, 'id':id}
    body = json.dumps(obj)
    return RESPONSE % {'date':get_time(), 'length':len(body), 'body':}

def make_error(code, id=None):
    return make_response('error', {'code':code, 'message':ERRORS[code]}, id)

def check_errors(func):
    def wrapped(*args, **kwds):
        try:
            return func(*args, **kwds)
        except TypeError, ValueError:
            return BAD_PARAMS
        except:
            return SERVER_ERROR
    wrapped.__name__ = func.__name__
    return wrapped

class RPC_Server(object):
    def __init__(self, addr_port):
        self.addr_port = addr_port

    def __process_json_rpc(self, json_rpc):
        if type(json_rpc) == list:
            return map(self.__process_json_rpc, json_rpc)

    def __handler(self, request):
        try:
            body = json.loads(request['body'])
        except:
            return make_error(PARSE_ERROR)
        if 'id' not in body or 'json' not in body or 'method' not in body or 'params' not in body:
            return make_response(BAD_REQUEST)
        try:
            assert body['method'].startswith('eth')
            func =  getattr(self, body['method'])
        except:
            return make_response(NO_METHOD)
        return make_response(func(body['params']))
        
    def eth_coinbase(self):
        return '0x' + STATE.block.coinbase.encode('hex')
    
    def eth_getBalance(self, address):
        return STATE.block.account_to_dict(address[:2].decode('hex'))['balance']

    def eth_sendTransaction(self, tx):
        if all(f in tx for f in ('to', 'from', 'value')):
            pass
