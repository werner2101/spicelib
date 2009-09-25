#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

import os
import sys
import numpy

sys.path.append("../../../../scripts/")
import spice_read
from plotutils import load, plotter

def plot_dc_amplifier():
    pp = plotter()
    
    plots = spice_read.spice_read("dc_amplifier.data").get_plots()
    x = plots[0].get_scalevector().get_data()
    vin = plots[0].get_datavectors()[0].get_data()
    vout = plots[0].get_datavectors()[1].get_data()
    
    pp.plot(x, vin, label="v(in)")
    pp.plot(x, vout, label="v(out)")
    pp.xlabel("Uin [V]")
    pp.ylabel("U [V]")
    pp.grid()
    pp.legend(loc="best")
    pp.savefig("dc_amplifier.png",dpi=80)
    pp.close()

#    for t,m in mm:
#        pp.plot(m[:,0], -m[:,2]*1000,label=t)
#    pp.xlabel("Uin [V]")
#    pp.ylabel("IC [mA]")
#    pp.grid()
#    pp.legend(loc='best')
#    pp.savefig("dc_IC.png",dpi=80)
#    pp.close()

#################### MAIN

ME = sys.argv[0] + ": "

command = "gnetlist -g spice-sdb -l ../../../../scripts/geda-parts.scm -o dc_amplifier.net dc_amplifier.sch"
print ME, "\n creating nestlist: ",  command
os.system(command)

command = "ngspice -b ../../../../testcircuits/opamp/simulate.ngspice"
print ME, "\n\n running simulation: ", command
os.system(command)

print ME, "\n\n plotting the results now"


plot_dc_amplifier()


