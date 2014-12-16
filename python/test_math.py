#!/usr/bin/env python2
import pyethereum
#import colorama #we should colorize the output
import random
import math


def pretty(floats):
	# right aligned, show sign, 6 significant digits, scientific notation
	return ['{:>-E}'.format(f) for f in floats]

def main():
    s = pyethereum.tester.state()
    c = s.contract('../serpent/fixedpoint.se')

    xs = [i + random.random() for i in range(0,100,2)]
    expected = [map(f, xs) for f in [math.exp, math.log, math.sqrt]]
    results = [None] * 3
    for funid in range(3):
    	results[funid] = zip(*[s.send(pyethereum.tester.k0, c, 0, funid=funid, abi=[int(x*2**64)]) for x in xs])
    	results[funid][0] = [val/float(2**64) for val in results[funid][0]]

    pretty_xs = pretty(xs)
    len_xs = len(xs)
    funcnames = ['exp','log','sqrt']
    for i in range(3):
    	pretty_expected = pretty(expected[i])
    	pretty_results = pretty(results[i][0])
    	pretty_gas = [str(v).rjust(12) for v in results[i][1]]
    	labels = ['Input','Expected','Result','Gas Cost']
    	table = [[l.center(12) for l in labels]]
    	table += zip(*[pretty_xs, pretty_expected, pretty_results, pretty_gas])
    	print '+' + '-'*(12*4+3) + '+'
    	print '+' + ('{:^%d}'%(12*4+3)).format(funcnames[i]) + '+'
    	print '+' + '-'*(12*4+3) + '+'
    	print '+' + '+'.join('-'*12 for i in range(4)) + '+'
    	for row in table:
    		print '|'+'|'.join(row)+'|'
    		print '+'+'+'.join('-'*12 for i in range(4)) + '+'

if __name__ == '__main__':
    main()
