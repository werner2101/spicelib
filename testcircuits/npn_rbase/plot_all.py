#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

import Gnuplot
import pylab  #TODO: replace pylab.load function
import os


def plot_dc_current():
    mm=[]

    mm.append(("0 C", pylab.load("dc_current_t0.data")))
    mm.append(("25 C",pylab.load("dc_current_t25.data")))
    mm.append(("50 C",pylab.load("dc_current_t50.data")))
    mm.append(("75 C",pylab.load("dc_current_t75.data")))
    mm.append(("100 C",pylab.load("dc_current_t100.data")))

    g = Gnuplot.Gnuplot()
    g('set data style lines')
    g('set terminal png')
    g('set output "dc_IB.png"')
    g.xlabel("Uin [V]")
    g.ylabel("IB [mA]")
    g('set grid')
    g('set key left top')
    datasets = []
    for t,m in mm:
        datasets.append(Gnuplot.Data(m[:,0], -m[:,1]*1000, title = t))
    g.plot(*datasets)

    g('set output "dc_IC.png"')
    g.ylabel("IC [mA]")
    datasets = []
    for t,m in mm:
        datasets.append(Gnuplot.Data(m[:,0], -m[:,2]*1000, title = t))
    g.plot(*datasets)

#################### MAIN

os.system("gnetlist -g spice-sdb -l ../../../../scripts/geda-parts.scm -o dc_current.net dc_current.sch")

os.system("gnucap -b simulate.gnucap")
plot_dc_current()


