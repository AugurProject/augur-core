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
                if bit($b, $i):
                    $acc += $a / 2^(64 - $i)
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
            with $f = $x&({fixedpoint_step} - 1):
                with $e_a = self.exp_table[$index]:
                    with $e_b = smallexp($f):
                        smallmul($e_a, $e_b)

# $a/$b < 3/2, so...
# 1 + ($a - $b)/$b < 3/2,
# ($a - $b)/$b < 1/2
# $c/$b < 1/2, $c = $a - $b
# 2*$c < $b
# 1/q > 2, q = $c/$b
macro bigdiv($a, $b):
    with $c = $a - $b:
        with $q = 2^63 - 1:
            with $acc = 0:
                with $i = 62:
                    with $shift = 4:
                        while $i >= 0:
                            if $acc + $b / $shift > $c:
                                $q -= 2^$i
                            else:
                                $acc += $b / $shift
                            $i -= 1
                            $shift *= 2
                        $q + 1

macro fxp_log_pc($x):
    #finds the index of the closest precomputed value of log <= log($x)
    with $lo = 0:
        with $hi = {table_size} - 1:
            with $mid = ($lo + $hi)/2:
                while $lo < $hi:
                    if self.exp_table[$mid] < $x:
                        $lo = $mid + 1
                    else:
                        $hi = $mid - 1
                    $mid = ($lo + $hi)/2
                $mid

macro fxp_log1p($x):
    if $x == 0:
        0
    else:
        with $xpow = $x*$x / 2^64:
            with $result = $x + $xpow / 2:
                {taylor_log_code}

macro fxp_log($x):
    with $y_i = fxp_log_pc($x):
        with $e_y = self.exp_table[$y_i]:
            with $A = bigdiv($x, $e_y):
                $y_i*{fixedpoint_step} + fxp_log1p($A)

macro fxp_sqrt($x):
    with $guess = $x/2:
        $guess = ($guess + $n*2^64/$guess)/2
        $guess = ($guess + $n*2^64/$guess)/2
        $guess = ($guess + $n*2^64/$guess)/2
        $guess = ($guess + $n*2^64/$guess)/2
        $guess = ($guess + $n*2^64/$guess)/2
        $guess = ($guess + $n*2^64/$guess)/2
        $guess = ($guess + $n*2^64/$guess)/2
        $guess = ($guess + $n*2^64/$guess)/2
        $guess = ($guess + $n*2^64/$guess)/2
        $guess = ($guess + $n*2^64/$guess)/2
        ($guess + $n*2^64/$guess)/2

macro fxp_pow($a, $b):
    fxp_exp($b*fxp_log($a)/2^64)
'''

def get_highest_fractional_bit(n):
    bits = bin(int(gmpy2.exp(1.0/2**n)*2**64))[2:]
    for i, b in enumerate(bits):
        if b=='1' and i>0:
            return 65-i

def gen_table_init(step, table_size):
    table_init_code = ''
    for i in xrange(table_size):
        entry = hex(int(gmpy2.exp(step*i)*2**64)).rstrip('L')
        code = 'self.exp_table[{}] = {}'.format(i, entry)
        table_init_code += code + '\n' + ' '*4
    return table_init_code[:-5]

def gen_exp_taylor(n):
    '''Generates the longest useful taylor series for 2^(64-n) bit fixedpoint number'''
    f = lambda x: x*f(x-1) if x>1 else 1
    x = 1 << (64 - n)
    xpow = (x*x) >> 64
    i = 2
    code = ''
    while (xpow*x >> 64) / f(i+1) > 0:
        code += '$result += $xpow / {}'.format(hex(f(i)).strip('L'))
        code += '\n'+16*' '
        code += '$xpow = $xpow*$x / 2^64'
        code += '\n'+16*' '
        xpow = (xpow*x) >> 64
        i += 1
    code += '$result + $xpow / {}'.format(hex(f(i)).strip('L'))
    return code

def gen_log1p_taylor(n):
    x = 1 << (64 - n)
    xpow = (x*x*x) >> 128
    code = ''
    i = 3
    while (xpow*x >> 64)/(i + 1) > 0:
        code += '$result %s= $xpow / %d' % ('-' if i%2 else '+', i)
        code += '\n' + 16*' '
        code += '$xpow = $xpow*$x / 2^64'
        code += '\n' + 16*' '
        xpow = (xpow*x) >> 64
        i += 1
    code += '$result %s $xpow / %d' % ('-' if i%2 else '+', i)
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
    taylor_code = gen_exp_taylor(inverse_log2_step_size)
    taylor_log_code = gen_log1p_taylor(inverse_log2_step_size)
    highest_fractional_bit = get_highest_fractional_bit(inverse_log2_step_size)
    f = open('fxp_macros.se', 'w')
    f.write(code_template.format(**locals()))
    f.close()
    sys.exit(0)

if __name__ == '__main__':
    main()
