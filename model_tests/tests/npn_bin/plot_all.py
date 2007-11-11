#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

import pylab
import os


def plot_dc_current():
    mm=[]

    mm.append(("0 C", pylab.load("dc_current_t0.data")))
    mm.append(("25 C",pylab.load("dc_current_t25.data")))
    mm.append(("50 C",pylab.load("dc_current_t50.data")))
    mm.append(("75 C",pylab.load("dc_current_t75.data")))
    mm.append(("100 C",pylab.load("dc_current_t100.data")))

    for t,m in mm:
        pylab.plot(m[:,0], -m[:,1]*1000,label=t)
    pylab.xlabel("Uin [V]")
    pylab.ylabel("Iin [mA]")
    pylab.grid()
    pylab.legend(loc="best")
    pylab.savefig("dc_IB.png",dpi=80)
    pylab.close()

    for t,m in mm:
        pylab.plot(m[:,0], -m[:,2]*1000,label=t)
    pylab.xlabel("Uin [V]")
    pylab.ylabel("IC [mA]")
    pylab.grid()
    pylab.legend(loc='best')
    pylab.savefig("dc_IC.png",dpi=80)
    pylab.close()

#################### MAIN

os.system("gnetlist -g spice-sdb -o dc_current.net dc_current.sch")
os.system("gnucap -b simulate.gnucap")
plot_dc_current()


