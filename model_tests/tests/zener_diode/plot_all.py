#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

import pylab
import os
import sys
sys.path.append("../../../../scripts/")
import spice_read


def plot_forward_voltage():
    labels = ["0C", "25C", "50C", "75C", "100C"]

    plots = spice_read.spice_read("forward_voltage.data").get_plots()
    for n,pl in enumerate(plots):
        x = pl.get_scalevector().get_data()
        yv =pl.get_datavectors()[0]
        y = yv.get_data()
        pylab.semilogy(y,-x,label = labels[n])
    pylab.ylabel("If [mA]")
    pylab.xlabel("Uf [V]")
    pylab.grid()
    pylab.legend(loc="best")
    pylab.savefig("dc_forward_voltage.png",dpi=80)
    pylab.close()

    plots = spice_read.spice_read("reverse_voltage.data").get_plots()
    for n,pl in enumerate(plots):
        x = pl.get_scalevector().get_data()
        yv =pl.get_datavectors()[0]
        y = yv.get_data()
        pylab.semilogy(-y,x,label = labels[n])
    pylab.ylabel("Ir [mA]")
    pylab.xlabel("Ur [V]")
    pylab.grid()
    pylab.legend(loc="best")
    pylab.savefig("dc_reverse_voltage.png",dpi=80)
    pylab.close()

#################### MAIN

os.system("gnetlist -g spice-sdb -o dc_current.net dc_current.sch")
#os.system("gnucap -b simulate.gnucap")
os.system("ngspice -b simulate.ngspice")
plot_forward_voltage()


