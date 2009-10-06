#! /usr/bin/python
# vim: ts=4 :
# vim: sw=4 :

import sys
import tempfile
import re
import os


SUBCKT_PAT = '^(\s*\.SUBCKT\s+)(\w+)/NS'

def fix(files):
    for fn in files:
        f = open(fn, 'r')
        tfd, tfn = tempfile.mkstemp(text=True)
        for line in f:
            match = re.search(SUBCKT_PAT, line)
            if match:
                old_name = match.group(2)
                name = old_name.split('/')[0]
                os.write(tfd, (re.sub(SUBCKT_PAT, match.group(1) + name, line)))
            else:
                os.write(tfd, line)
        os.close(tfd)
        f.close()
        os.rename(tfn, fn)


if __name__ == '__main__':
    fix(sys.argv[1:])
