import os
from translate_externs import replace_names

for d, s, fs in os.walk('src'):
    for f in fs:
        new_code = []
        names = []
        for line in open(os.path.join(d, f)):
            line = line.rstrip()
            if line == '' or line.startswith('#'):
                continue
            if line.startswith('import'):
                _, name = line.split(' ')
                line += ' as ' + name.upper()
                names.append(name + '.')
            else:
                line, _ = replace_names(line, names, lambda n: n[:-1].upper()+'.')
            new_code.append(line)
        print '\n'.join(new_code)
