#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

import os
import sys

sys.path.append("../../../../scripts/")
from plotutils import load, plotter


def plot_dc_current():
    pp = plotter()
    mm=[]

    mm.append(("0 C", load("dc_current_t0.data")))
    mm.append(("25 C",load("dc_current_t25.data")))
    mm.append(("50 C",load("dc_current_t50.data")))
    mm.append(("75 C",load("dc_current_t75.data")))
    mm.append(("100 C",load("dc_current_t100.data")))

    for t,m in mm:
        pp.plot(m[:,0], -m[:,1]*1000,label=t)
    pp.xlabel("Uin [V]")
    pp.ylabel("IB [mA]")
    pp.grid()
    pp.legend(loc="best")
    pp.savefig("dc_IB.png",dpi=80)
    pp.close()

    for t,m in mm:
        pp.plot(m[:,0], -m[:,2]*1000,label=t)
    pp.xlabel("Uin [V]")
    pp.ylabel("IC [mA]")
    pp.grid()
    pp.legend(loc='best')
    pp.savefig("dc_IC.png",dpi=80)
    pp.close()

#################### MAIN

os.system("gnetlist -g spice-sdb -l ../../../../scripts/geda-parts.scm -o dc_current.net dc_current.sch")

os.system("gnucap -b ../../../../testcircuits/npn_rbase/simulate.gnucap")
plot_dc_current()


