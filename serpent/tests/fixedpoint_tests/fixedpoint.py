# This software computes the natural log and exponential functions in 192.64 fixedpoint for Augur
# Copyright (C)  2014 Chris Calderon, Joey Krug, Jack Peterson
#    This program is free software; you can redistribute it &&/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is free software: you can redistribute it &&/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
# Any questions please contact chris-da-dev@augur.net

# This code uses a 256 bit fixedpoint format.
# The bottom 64 bits of each number is the
# "decimal" part; the highest bit represents
# the multiple of 1/2, the next bit 1/4, etc.
# the top 192 bits represent the "integer" part,
# in the usual binary way.
# So the fixedpoint version of 1 is 1 << 64, a.k.a. 2**64.
#
# This code is written to work on both python and serpent.
# To test check the output of this code in python, do something like:
## import gmpy2
## import fixedpoint
## gmpy2.get_context().precision = 256
## 
## def exp_err(n):
##     expected = int(gmpy2.exp(n)*2**64)
##     result = fixedpoint.exp_e(n*2**64)
##     return float(abs(result - expected))/expected

def exp_e(x):
    # Computes e^x by switching to base 2.
    # Let y = x/ln2, a = floor(y), and b = y - a.
    # Then e^x = 2^(a+b) = 2^a*2^b.
    # 2^a is a bit shit, and 2^b is approximated
    # with a lagrange interpolation (recall that b
    # is the decimal part of y, so 0 <= b < 1.
    one = 0x10000000000000000
    ln2 = 0xb17217f7d1cf79ac

    y = x * one / ln2
    shift = 2**(y / one)
    z = y % one
    zpow = z
    result = one
    result += 0xb172182739bc0e46 * zpow / one
    zpow = zpow * z / one
    result += 0x3d7f78a624cfb9b5 * zpow / one
    zpow = zpow * z / one
    result += 0xe359bcfeb6e4531 * zpow / one
    zpow = zpow * z / one
    result += 0x27601df2fc048dc * zpow / one
    zpow = zpow * z / one
    result += 0x5808a728816ee8 * zpow / one
    zpow = zpow * z / one
    result += 0x95dedef350bc9 * zpow / one
    zpow = zpow * z / one
    result += 0x16aee6e8ef346 * zpow / one
    return(shift*result)

def ln(x):
    # Computes natural log by switching to base 2.
    # Let y = floor(log2(x)), and z = x/y.
    # Then ln(x) = (y + log2(z))/log2(e),
    # with 1 <= z < 2. y is computed with a binary
    # search, and log2(z) is computed using a
    # lagrange interpolation.
    one = 0x10000000000000000
    log2e = 0x171547652b82fe177

    #binary search for floor(log2(x))
    y = x / one
    lo = 0
    hi = 191
    mid = (lo + hi)/2
    while lo < hi:
        if 2**mid > y:
            hi = mid - 1
        else:
            lo = mid + 1
        mid = (lo + hi)/2
    ilog2 = lo

    #lagrange interpolation for log2
    z = x / (2**ilog2)
    zpow = one
    result = 0
    result += -0x443b9c5adb08cc45f*zpow/one
    zpow = zpow*z/one
    result += 0xf0a52590f17c71a3f*zpow/one
    zpow = zpow*z/one
    result += -0x2478f22e787502b023*zpow/one
    zpow = zpow*z/one
    result += 0x48c6de1480526b8d4c*zpow/one
    zpow = zpow*z/one
    result += -0x70c18cae824656408c*zpow/one
    zpow = zpow*z/one
    result += 0x883c81ec0ce7abebb2*zpow/one
    zpow = zpow*z/one
    result += -0x81814da94fe52ca9f5*zpow/one
    zpow = zpow*z/one
    result += 0x616361924625d1acf5*zpow/one
    zpow = zpow*z/one
    result += -0x39f9a16fb9292a608d*zpow/one
    zpow = zpow*z/one
    result += 0x1b3049a5740b21d65f*zpow/one
    zpow = zpow*z/one
    result += -0x9ee1408bd5ad96f3e*zpow/one
    zpow = zpow*z/one
    result += 0x2c465c91703b7a7f4*zpow/one
    zpow = zpow*z/one
    result += -0x918d2d5f045a4d63*zpow/one
    zpow = zpow*z/one
    result += 0x14ca095145f44f78*zpow/one
    zpow = zpow*z/one
    result += -0x1d806fc412c1b99*zpow/one
    zpow = zpow*z/one
    result += 0x13950b4e1e89cc*zpow/one

    return((ilog2*one + result)*one/log2e)
