#!/usr/bin/python2
import gmpy2
import sys

code_template = '''
data exp_table[{table_size}]

macro fxp_init($x):
    {table_init_code}

macro bit($x, $i):
    ($x / 2^$i)&1

# $b is at most 65 bits long (i.e. close to 1)
# also, 1 < $b < e^{step:.3f}
macro smallmul($a, $b):
    with $i = {highest_fractional_bit}:
        with $acc = $a:
            while $i > 0:
                $acc += $a / (bit($b, $i) * 2^(65 - $i))
                $i -= 1
            $acc

# e^$x, where 0 < $x < {step:.3f}
macro smallexp($x):
    if $x == 0:
        2^64
    else:
        with $result = 2^64 + $x: #first two terms of taylor series
            with $xpow = $x*$x / 2^64:
                {taylor_code}

#positive exponents only!
macro fxp_exp($x):
    with $index = $x / {fixedpoint_step}:
        if $index > ({table_size} - 2):
            2^255-1
        else:
            with $e_a = self.exp_table[$index]:
                with $e_b = smallexp($x&({fixedpoint_step} - 1)):
                    smallmul($e_a, $e_b)
'''

def get_highest_fractional_bit(n):
    bits = bin(int(gmpy2.exp(1.0/2**n)*2**64))[3:]
    for i, b in enumerate(bits):
        if b=='1':
            return 65-i-1

def gen_table_init(step, table_size):
    table_init_code = ''
    for i in xrange(table_size):
        entry = hex(int(gmpy2.exp(step*i)*2**64)).rstrip('L')
        code = 'self.exp_table[{}] = {}'.format(i, entry)
        table_init_code += code + '\n' + ' '*4
    return table_init_code[:-5]

def gen_taylor(n):
    '''Generates the longest useful taylor series for 2^(64-n) bit number'''
    f = lambda x: x*f(x-1) if x>1 else 1
    x = 1 << (64 - n)
    xpow = (x*x) >> 64
    i = 2
    code = ''
    while xpow / f(i+1) > 0:
        code += '$result += $xpow / {}'.format(hex(f(i)).strip('L'))
        code += '\n'+16*' '
        code += '$xpow = $xpow*$x / 2^64'
        code += '\n'+16*' '
        xpow = (xpow*x) >> 64
        i += 1
    code += '$result + $xpow / {}'.format(hex(f(i)).strip('L'))
    return code

def main():
    #step_size = 1/1; inverse_log2_step_size = 1
    #step_size = 1/2; inverse_log2_step_size = 2
    #step_size = 1/4; inverse_log2_step_size = 3
    #step_size = 1/8; inverse_log2_step_size = 4
    gmpy2.get_context().precision = 256
    inverse_log2_step_size = int(sys.argv[1])
    fixedpoint_step = hex(1 << (64 - inverse_log2_step_size))
    table_size = 1 << (inverse_log2_step_size + 7)
    step = 1.0 / (1 << inverse_log2_step_size)
    table_init_code = gen_table_init(step, table_size)
    taylor_code = gen_taylor(inverse_log2_step_size)
    highest_fractional_bit = get_highest_fractional_bit(inverse_log2_step_size)
    f = open('fxp_macros.se', 'w')
    f.write(code_template.format(**locals()))
    f.close()
    sys.exit(0)

if __name__ == '__main__':
    main()
