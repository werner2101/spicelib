#!/usr/bin/python
# some models have a .ENDS statement even if there is no
# subcircuit definition.
# comment out the wrong .ENDS statement

import sys, re

for filename in sys.argv[1:]:
    lines = open(filename,'rt').readlines()
    outlines = []
    wrong_ends = False
    
    for line in lines:
        if re.match('\.subckt', line.lower()):
            break
        if re.match('\.ends',line.lower()):
            outlines.append('* WRONG .ENDS BUGFIX: ' + line)
            wrong_ends = True
        else:
            outlines.append(line)

    if wrong_ends:
        open(filename,'wt').writelines(outlines)
        print '  Fixed file "%s"' %(filename)

                    
            
                        
        

