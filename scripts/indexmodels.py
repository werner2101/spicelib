#!/usr/bin/python

import sys,re,string



PREFIX="NXP"
NUMBER=101001



TRANSISTOR_TEMPLATE="""
$headline
[$part _$number]
symbol=.sym
value=$part
modelname=$part
file=$filename
refdes=$refdes
pinseq_c=1
pinseq_b=2
pinseq_e=3
pinnr_c=C
pinnr_b=B
pinnr_e=E
footprint=none
description=TBD
test_refdes=$test_refdes
model_status=test
"""

DIODE_TEMPLATE="""
$headline
[$part _$number]
symbol=.sym
value=$part
modelname=$part
file=$filename
refdes=$refdes
pinseq_a=1
pinseq_k=2
pinnr_a=A
pinnr_k=K
footprint=none
description=TBD
test_refdes=$test_refdes
model_status=$status
"""


values = {"headline":"",
          "part":"",
          "number":"",
          "filename":"",
          "refdes":"D?",
          "test_refdes":"D1",
          "status":"test"}




#tt = string.Template(TRANSISTOR_TEMPLATE)
tt = string.Template(DIODE_TEMPLATE)

for f in sys.argv[1:]:
    lines = open(f,"rt").readlines()
    v = values.copy()
    for l in lines:
        if re.match(".SUBCKT",l) or re.match(".MODEL",l):
            toks = string.split(string.strip(l))
            v["part"] = toks[1]
            v["filename"] = f
            v["number"] = PREFIX + str(NUMBER)[1:]
            NUMBER = NUMBER + 1
            if re.match(".MODEL",l):            
                v["refdes"] = "D?"
                v["test_refdes"] = "D1"
            else:
                v["refdes"] = "X?"
                v["test_refdes"] = "X1"
            n = len(toks)
            if n > 4:
                v["headline"] = "\n# Subcircuit with " + "%i" %(n-2) + " connections"
                v["status"] = "undefined"
            print tt.safe_substitute(v)
            break


            
