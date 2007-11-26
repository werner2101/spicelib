#!/usr/bin/python

import sys,re

if len(sys.argv) < 4:
    print "usage: " + sys.argv[0] + " querystring repacestring file1 [file2, ..]"
    sys.exit()

query = sys.argv[1]
repl = sys.argv[2]

for f in sys.argv[3:]:
    print sys.argv[0] + ': replace "%s" with "%s" in file "%s"' %(query,repl,f)
    content = open(f, "r").read()
    open(f,"w").write(content.replace(query, repl))

