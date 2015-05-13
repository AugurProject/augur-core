import os
import sys
from colorama import Fore, Back, Style, init; init()
from string import lower

NAMES = {
    'CLOSEEIGHT':'closeMarketEight',
    'CLOSEFOUR': 'closeMarketFour',
    'CLOSETWO': 'closeMarketTwo',
    'CLOSEONE': 'closeMarketOne',
    'EXPEVENTS': 'expiringEvents',
    'EXPIRING': 'expiringEvents',
    'FXP': 'fxMath',
    'QUORUM':'checkQuorum',
}

normal_names = '''\
BRANCHES CASH CENTER INFO INTERPOLATE MARKETS PAYOUT REDEEM_ADJUST REDEEM_CENTER \
REDEEM_INTERPOLATE REDEEM_PAYOUT REDEEM_RESOLVE REDEEM_SCORE REPORINTG RESOLVE \
SCORE STATISTICS'''.split(' ')

NAMES.update(dict(zip(normal_names, map(lower, normal_names))))

def is_extern(line):
    return line.startswith('extern')

def extern_to_import(line):
    i = line.find(':')
    name = line[7:i]
    if name.endswith('.se'):
        name = name[:-3]
    return 'import ' + name

def is_old_address(line):
    return ('=' in line) and not (line[0] in ' \t')

def highlight(name):
    return Style.BRIGHT + Fore.BLACK + Back.YELLOW + name + Style.RESET_ALL

def digits(num):
    return len(str(num))

def linenum(num, w):
    return Fore.GREEN + Back.BLUE + str(num).rjust(digits(w)) + Style.RESET_ALL + Style.BRIGHT + ' : ' + Style.RESET_ALL

def find_name(line):
    for name in NAMES.keys():
        if line.startswith(name):
            return name
    return False

def replace_names(line):
    replacements = []
    i = 0
    while i < len(line):
        name = find_name(line[i:])
        if name:
            new_name = NAMES[name]
            line = line[:i] + new_name + line[i + len(name):]
            replacements.append((i, i + len(new_name)))
            i += len(new_name)
        else:
            i += 1
    return line, replacements

def highlight_replacements(line, replacements):
    da, db = 0, 0
    for a, b in replacements:
        a, b = a + da, b + db
        highlighted = highlight(line[a:b])
        line = line[:a] + highlighted + line[b:]
        dl = len(highlighted) - (b - a)
        da, db = da + dl, db + dl
    return line

def show(code, replacementses):
    l = len(code)
    for i, (line, replacements) in enumerate(zip(code, replacementses)):
        print linenum(i, l - 1) + highlight_replacements(line, replacements).rstrip()
        
for d, s, f in os.walk('src'):
    for F in f:
        fi = open(os.path.join(d, F))
        print 'Processing', fi.name
        new_code = []
        replacementses = []
        for line in fi:
            if is_extern(line):
                new_code.append(extern_to_import(line))
                replacementses.append([])
            elif is_old_address(line):
                pass
            elif line.startswith('inset'):
                new_code.append(line.replace('../', '../../'))
                replacementses.append([])
            else:
                new_line, replacements = replace_names(line)
                new_code.append(new_line)
                replacementses.append(replacements)

        show(new_code, replacementses)
        choice = raw_input('write code? (y/n/q): ')
        if choice == 'y':
            fi.close()
            fi = open(fi.name, 'w')
            fi.write('\n'.join(new_code))
            fi.close()
        elif choice == 'n':
            continue
        else:
            print 'ABORTING'
            sys.exit(0)
