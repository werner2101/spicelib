#!/usr/bin/python

import sys,re

if len(sys.argv) < 4:
    print "usage: " + sys.argv[0] + " querystring repacestring file1 [file2, ..]"
    sys.exit(-1)

query = sys.argv[1]
repl = sys.argv[2]

error = False

for filename in sys.argv[3:]:
    content = open(filename, "r").read()
    content2 = content.replace(query, repl)
    if content == content2:
        print '  ERROR: searchstring not found "%s"' %(query)
        error = True
    else:
        print '  Fixed file "%s"' %(filename)
        open(filename,"w").write(content2)

if error:
    sys.exit(-1)

