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

def json_rpc_handler(request):
    pass

