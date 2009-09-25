#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

import os
import sys
import numpy

sys.path.append("../../../../scripts/")
from plotutils import load, plotter



def plot_dc_current_gain():
    pp = plotter()
    mm=[]

    mm.append(("0 C", load("dc_current_gain_t0.data")))
    mm.append(("25 C",load("dc_current_gain_t25.data")))
    mm.append(("50 C",load("dc_current_gain_t50.data")))
    mm.append(("75 C",load("dc_current_gain_t75.data")))
    mm.append(("100 C",load("dc_current_gain_t100.data")))

    for t,m in mm:
        pp.semilogx(-m[:,1]*1000,m[:,1]/m[:,2],label=t)
    pp.xlabel("Ic [mA]")
    pp.ylabel("hfe")
    pp.grid()
    pp.legend(loc="best")
    pp.savefig("dc_current_gain.png",dpi=80)
    pp.close()

    for t,m in mm:
        pp.semilogx(-m[:,1]*1000,-m[:,3]*1000,label=t)
    pp.xlabel("Ic [mA]")
    pp.ylabel("V BE [mV]")
    pp.grid()
    pp.legend(loc='best')
    pp.savefig("base_emitter_voltage.png",dpi=80)
    pp.close()

def plot_saturation_voltages():
    pp = plotter()
    mm=[]

    mm.append(("0 C", load("saturation_voltages_t0.data")))
    mm.append(("25 C",load("saturation_voltages_t25.data")))
    mm.append(("50 C",load("saturation_voltages_t50.data")))
    mm.append(("75 C",load("saturation_voltages_t75.data")))
    mm.append(("100 C",load("saturation_voltages_t100.data")))

    for t,m in mm:
        ## only plot the values where Vce sat is smaller 1.00
        firstind = numpy.where(m[:,3] > -1.0)[0][0]
        pp.loglog(-m[firstind:,1]*1000,-m[firstind:,3]*1000,label=t)
    pp.xlabel("Ic [mA]")
    pp.ylabel("VCE sat [mV]")
    pp.grid()
    pp.legend(loc='best')
    pp.savefig("vce_saturation_voltage.png",dpi=80)
    pp.close()

    for t,m in mm:
        pp.semilogx(-m[:,1]*1000,-m[:,2]*1000,label=t)
    pp.xlabel("Ic [mA]")
    pp.ylabel("V BE sat [mV]")
    pp.grid()
    pp.legend(loc='best')
    pp.savefig("vbe_saturation_voltage.png",dpi=80)
    pp.close()


#################### MAIN

os.system("gnetlist -g spice-sdb -l ../../../../scripts/geda-parts.scm -o dc_current_gain.net dc_current_gain.sch")
os.system("gnetlist -g spice-sdb -l ../../../../scripts/geda-parts.scm -o saturation_voltages.net saturation_voltages.sch")
os.system("gnucap -b ../../../../testcircuits/pnp_bipolar/simulate.gnucap")
plot_dc_current_gain()
plot_saturation_voltages()

