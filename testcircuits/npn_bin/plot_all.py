#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

import os
import sys
import popen2
import numpy

sys.path.append("../../../../scripts/")
from plotutils import load, plotter


def plot_dc_current():
    pp = plotter()
    mm=[]
    ret = 0
    
    mm.append(("0 C", load("dc_current_t0.data")))
    mm.append(("25 C",load("dc_current_t25.data")))
    mm.append(("50 C",load("dc_current_t50.data")))
    mm.append(("75 C",load("dc_current_t75.data")))
    mm.append(("100 C",load("dc_current_t100.data")))

    for t,m in mm:
        if numpy.any(-m[:,1] < -0.001) or numpy.any(-m[:,1]>1.0):
            print "Input current out of expected range [-0.001, 1.0]"
            ret = 1
        pp.plot(m[:,0], -m[:,1]*1000,label=t)
    pp.xlabel("Uin [V]")
    pp.ylabel("Iin [mA]")
    pp.grid()
    pp.legend(loc="best")
    pp.savefig("dc_IB.png",dpi=80)
    pp.close()

    for t,m in mm:
        if numpy.any(-m[:,2] < -0.001) or numpy.any(-m[:,2]>100.0):
            print "Collector current out of expected range [-0.001, 100.0]"
            ret = 1
        pp.plot(m[:,0], -m[:,2]*1000,label=t)
    pp.xlabel("Uin [V]")
    pp.ylabel("IC [mA]")
    pp.grid()
    pp.legend(loc='best')
    pp.savefig("dc_IC.png",dpi=80)
    pp.close()

    return ret

#################### MAIN


ME = sys.argv[0] + ": "

command = "gnetlist -g spice-sdb -l ../../../../scripts/geda-parts.scm -o dc_current.net dc_current.sch"

print ME, "creating netlist: ", command
pop = popen2.Popen4(command)
print pop.fromchild.read()
ret_gnetlist = pop.wait()
if ret_gnetlist != 0:
    print ME, "netlist creation failed with errorcode:", ret_gnetlist
else:
    print ME, "netlist creation was successful"

command = "gnucap -b ../../../../testcircuits/npn_bin/simulate.gnucap"
print ME, "running simulation: ", command
pop = popen2.Popen4(command)
print pop.fromchild.read()
ret_simulation = pop.wait()
if ret_simulation != 0:
    print ME, "simulation failed with errorcode:", ret_simulation
else:
    print ME, "simulation run was successful"

print ME, "testing and plotting"
try:
    ret_plot = plot_dc_current()
except Exception, data:
    print ME, "plotting function died:"
    print data
    sys.exit(1)
    
if ret_plot == 0:
    print ME, "finished testing and plotting successfully"
    sys.exit(0)
else:
    print ME, "testing or plotting failed"
    sys.exit(2)
