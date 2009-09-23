#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

import Gnuplot
import os
import numpy



def load(fname,comments='#',delimiter=None, skiprows=0,
         usecols=None, unpack=False, dtype=numpy.float_):
    """
    Load ASCII data from *fname* into an array and return the array.
    Adapted from pylab.load
    pylab is copyright John D. Hunter and licensed under the matplotlib license:

    License agreement for matplotlib 0.99.1

    1. This LICENSE AGREEMENT is between John D. Hunter (“JDH”), and the Individual or Organization (“Licensee”) accessing and otherwise using matplotlib software in source or binary form and its associated documentation.

    2. Subject to the terms and conditions of this License Agreement, JDH hereby grants Licensee a nonexclusive, royalty-free, world-wide license to reproduce, analyze, test, perform and/or display publicly, prepare derivative works, distribute, and otherwise use matplotlib 0.99.1 alone or in any derivative version, provided, however, that JDH’s License Agreement and JDH’s notice of copyright, i.e., “Copyright (c) 2002-2009 John D. Hunter; All Rights Reserved” are retained in matplotlib 0.99.1 alone or in any derivative version prepared by Licensee.

    3. In the event Licensee prepares a derivative work that is based on or incorporates matplotlib 0.99.1 or any part thereof, and wants to make the derivative work available to others as provided herein, then Licensee hereby agrees to include in any such work a brief summary of the changes made to matplotlib 0.99.1.

    4. JDH is making matplotlib 0.99.1 available to Licensee on an “AS IS” basis. JDH MAKES NO REPRESENTATIONS OR WARRANTIES, EXPRESS OR IMPLIED. BY WAY OF EXAMPLE, BUT NOT LIMITATION, JDH MAKES NO AND DISCLAIMS ANY REPRESENTATION OR WARRANTY OF MERCHANTABILITY OR FITNESS FOR ANY PARTICULAR PURPOSE OR THAT THE USE OF MATPLOTLIB 0.99.1 WILL NOT INFRINGE ANY THIRD PARTY RIGHTS.

    5. JDH SHALL NOT BE LIABLE TO LICENSEE OR ANY OTHER USERS OF MATPLOTLIB 0.99.1 FOR ANY INCIDENTAL, SPECIAL, OR CONSEQUENTIAL DAMAGES OR LOSS AS A RESULT OF MODIFYING, DISTRIBUTING, OR OTHERWISE USING MATPLOTLIB 0.99.1, OR ANY DERIVATIVE THEREOF, EVEN IF ADVISED OF THE POSSIBILITY THEREOF.

    6. This License Agreement will automatically terminate upon a material breach of its terms and conditions.

    7. Nothing in this License Agreement shall be deemed to create any relationship of agency, partnership, or joint venture between JDH and Licensee. This License Agreement does not grant permission to use JDH trademarks or trade name in a trademark sense to endorse or promote products or services of Licensee, or any third party.

    8. By copying, installing or otherwise using matplotlib 0.99.1, Licensee agrees to be bound by the terms and conditions of this License Agreement.
    """

    converters = {}
    fh = open(fname, 'r')
    X = []

    def splitfunc(x):
        return x.split(delimiter)

    converterseq = None
    for i,line in enumerate(fh):
        line = line.split(comments, 1)[0].strip()
        if not len(line): continue
        if converterseq is None:
            converterseq = [converters.get(j,float)
                               for j,val in enumerate(splitfunc(line))]
        row = [converterseq[j](val)
                  for j,val in enumerate(splitfunc(line))]
        thisLen = len(row)
        X.append(row)

    X = numpy.array(X, dtype)
    r,c = X.shape
    if r==1 or c==1:
        X.shape = max(r,c),
    return X


def plot_dc_current_gain():
    mm=[]

    mm.append(("0 C", load("dc_current_gain_t0.data")))
    mm.append(("25 C",load("dc_current_gain_t25.data")))
    mm.append(("50 C",load("dc_current_gain_t50.data")))
    mm.append(("75 C",load("dc_current_gain_t75.data")))
    mm.append(("100 C",load("dc_current_gain_t100.data")))

    g = Gnuplot.Gnuplot()
    g('set data style lines')
    g('set logscale x')
    g('set terminal png')
    g('set output "dc_current_gain.png"')
    g.xlabel("Ic [mA]")
    g.ylabel("hfe")
    g('set grid')
    datasets = []
    for t,m in mm:
        datasets.append(Gnuplot.Data(-m[:,1]*1000, m[:,1]/m[:,2], title = t))
    g.plot(*datasets)

    g('set output "base_emitter_voltage.png"')
    g.ylabel("V BE [mV]")
    g('set key left top')
    datasets = []
    for t,m in mm:
        datasets.append(Gnuplot.Data(-m[:,1]*1000, -m[:,3]*1000, title = t))
    g.plot(*datasets)

def plot_saturation_voltages():
    mm=[]

    mm.append(("0 C", load("saturation_voltages_t0.data")))
    mm.append(("25 C",load("saturation_voltages_t25.data")))
    mm.append(("50 C",load("saturation_voltages_t50.data")))
    mm.append(("75 C",load("saturation_voltages_t75.data")))
    mm.append(("100 C",load("saturation_voltages_t100.data")))

    g = Gnuplot.Gnuplot()
    g('set data style lines')
    g('set logscale xy')
    g('set terminal png')
    g('set output "vce_saturation_voltage.png"')
    g.xlabel("Ic [mA]")
    g.ylabel("VCE sat [mV]")
    g('set grid')
    g('set key right bottom')
    datasets = []
    for t,m in mm:
        ## only plot the values where Vce sat is smaller 2.00
        firstind = numpy.nonzero(numpy.ravel(m[:,3] > -2.0))[0][0]
        datasets.append(Gnuplot.Data(-m[firstind:,1]*1000, -m[firstind:,3]*1000, title = t))
    g.plot(*datasets)

    g('set logscale x')
    g('set output "vbe_saturation_voltage.png"')
    g('set key left top')
    g.ylabel("V BE sat [mV]")
    datasets = []
    for t,m in mm:
        datasets.append(Gnuplot.Data(-m[:,1]*1000, -m[:,2]*1000, title = t))
    g.plot(*datasets)


#################### MAIN

os.system("gnetlist -g spice-sdb -l ../../../../scripts/geda-parts.scm -o dc_current_gain.net dc_current_gain.sch")
os.system("gnetlist -g spice-sdb -l ../../../../scripts/geda-parts.scm -o saturation_voltages.net saturation_voltages.sch")
os.system("gnucap -b simulate.gnucap")
plot_dc_current_gain()
plot_saturation_voltages()

