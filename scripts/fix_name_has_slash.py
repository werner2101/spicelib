#! /usr/bin/python
# vim: ts=4 :
# vim: sw=4 :

import sys
import tempfile
import re
import os
import optparse


SUBCKT_PAT = '^(\s*\.SUBCKT\s+)(\w+)/NS'

def fix(target, source, env):
    infn = str(source[0])
    outfn = str(target[0])
    f = open(infn, 'r')
    tfd, tfn = tempfile.mkstemp(dir=os.path.dirname(infn), text=True)
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
    os.rename(tfn, outfn)


if __name__ == '__main__':
    usage = "%prog [options] [FILE] ..."
    parser = optparse.OptionParser(usage)
    parser.add_option('-o', '--output', help="Save the output to FILE.  Does not work if multiple input files are specified", metavar='FILE')
    (options, args) = parser.parse_args(sys.argv[1:])
    if (options.output != None and len(args) != 1) or \
            (options.output == None and len(args) < 1):
        parser.print_usage()
        sys.exit(2)
    if options.output != None:
        fix(options.output, args[0])
    else:
        for f in args:
            fix(f, f)
