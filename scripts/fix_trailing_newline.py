#!/usr/bin/python
# Read a spice model and fix the following things:
# add a headline with asterisk
# add trailing newline if missing

import sys, string

for filename in sys.argv[1:]:
    lines = open(filename,"rt").readlines()
    if len(lines) < 2:
        print "Error: fix_model.py:  symbolfile", f, " too short"
        sys.exit(1)
    f2 = open(filename, "wt")
    ## fix the first line
    if lines[0][0] != "*":
        f2.write("*\n")
    f2.write(string.join(lines,""))
    ## fix trailing newline
    if lines[-1][-1] != "\n":
        f2.write("\n")
    f2.close()
    del f2
