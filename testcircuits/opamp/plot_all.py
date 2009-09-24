#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

import Gnuplot
import os
import sys
import numpy
sys.path.append("../../../../scripts/")
import spice_read

def plot_dc_amplifier():
    
    plots = spice_read.spice_read("dc_amplifier.data").get_plots()
    x = plots[0].get_scalevector().get_data()
    vin = plots[0].get_datavectors()[0].get_data()
    vout = plots[0].get_datavectors()[1].get_data()
    
    g = Gnuplot.Gnuplot()
    g('set data style lines')
    g('set terminal png')
    g('set output "dc_amplifier.png"')
    g.xlabel("Uin [V]")
    g.ylabel("U [V]")
    g('set grid')
    g('set key left top')
    d1 = Gnuplot.Data(x, vin, title="v(in)")
    d2 = Gnuplot.Data(x, vin, title="v(in)")
    g.plot(d1, d2)

#    for t,m in mm:
#        pylab.plot(m[:,0], -m[:,2]*1000,label=t)
#    pylab.xlabel("Uin [V]")
#    pylab.ylabel("IC [mA]")
#    pylab.grid()
#    pylab.legend(loc='best')
#    pylab.savefig("dc_IC.png",dpi=80)
#    pylab.close()

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


