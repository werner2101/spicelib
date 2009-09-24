#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

import Gnuplot
import popen2
import sys
import numpy
sys.path.append("../../../../scripts/")
import spice_read


def plot_voltages():
    labels = ["0C", "25C", "50C", "75C", "100C"]
    ret = 0

    plots = spice_read.spice_read("forward_voltage.data").get_plots()
    g = Gnuplot.Gnuplot()
    g('set data style lines')
    g('set logscale y')
    g('set terminal png')
    g('set output "dc_forward_voltage.png"')
    g.ylabel("If [mA]")
    g.xlabel("Uf [V]")
    g('set key left top')
    g('set grid')
    datasets = []
    for n,pl in enumerate(plots):
        If = -pl.get_scalevector().get_data()
        Uf = pl.get_datavectors()[0].get_data()
        if numpy.any(Uf<0.5) or numpy.any(Uf>200.0):
            print "forward voltage out of expected range [0.5, 200.0]"
            ret = 1
        datasets.append(Gnuplot.Data(Uf, If * 1000., title = labels[n]))
    g.plot(*datasets)

    g('set output "dc_reverse_voltage.png"')
    g.xlabel("Ur [V]")
    datasets = []
    plots = spice_read.spice_read("reverse_voltage.data").get_plots()
    for n,pl in enumerate(plots):
        Ir = pl.get_scalevector().get_data()
        Ur = -pl.get_datavectors()[0].get_data()

        if numpy.any(Ur<0.5) or numpy.any(Ur>200.0):
            print "reverse voltage out of expected range [0.5, 200.0]"
            ret = 2
        datasets.append(Gnuplot.Data(Ur, If * 1000., title = labels[n]))
    g.plot(*datasets)

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

command = "ngspice -b ../../../../testcircuits/zener_bidirectional/simulate.ngspice"
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
    ret_plot = plot_voltages()
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
