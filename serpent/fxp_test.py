from pyethereum import tester as t
import gmpy2
import random
import sys
import cStringIO
import os

gmpy2.get_context().precision = 256

def suppress_output(thunk):
    old_stdout = sys.stdout
    sys.stdout = cStringIO.StringIO()
    try:
        result = thunk()
    except:
        old_stdout.write(sys.stdout.read())
        sys.exit(1)
    else:
        sys.stdout = old_stdout
        return result

def pretty(d):
    if isinstance(d, (int, long)):
        return '{:x}'.format(d)
    if type(d) == float:
        return '{:+%}'.format(d)
    if type(d) == str:
        return '{!r}'.format(d)
    if type(d) == dict:
        return ', '.join(pretty(k)+'='+pretty(v) for k,v in d.items())
    else:
        raise TypeError('You got a funky type! %s' % str(type(d)))

def test(t, s, c):
    total_error = 0
    total_gas = 0
    for i in range(2,130,2):
        x = gmpy2.mpfr(i + 2*random.random())
        expected = int(gmpy2.exp(x)*2**64)
        result = suppress_output(lambda: s.profile(t.k0, c, 0, 'func', 'i', [int(x*2**64)]))
        total_error += abs((result['output'][0] - expected)/float(expected))
        total_gas += result['gas']
    return(total_gas/49.0, total_error/49.0)

def main():
    code = '''\
def init():
    fxp_init(0)

def func(n):
    result = fxp_exp(n)
    return(result)
inset('fxp_macros.se')
'''
    s = t.state()    
    sys.stdout.write('Compiling...\t')
    sys.stdout.flush()
    c = suppress_output(lambda: s.contract(code))
    print 'Done.'

    print 'Running Tests'
    avg_gas, avg_err = 0, 0
    for i in range(1):
        x, y= test(t, s, c)
        avg_gas += x
        avg_err += y
        sys.stdout.write('.')
        sys.stdout.flush()
    print 'Done.'
    print 'avg gas cost = {:E}; avg error = {:%}'.format(avg_gas/(i+1), avg_err/(i+1))

if __name__ == '__main__':
#    import cProfile
#    cProfile.run('main()')
    main()
