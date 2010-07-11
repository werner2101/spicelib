#!/usr/bin/python
# vim: ts=4
# vim: sw=4

import numpy
from spicelibconf import *


if PLOTTER == 'gnuplot':
    import Gnuplot
    Gnuplot.GnuplotOpts.default_term = "png"
else:
    import matplotlib.pyplot


class gnuplot_subplot(object):
    """structure for a single subplot for gnuplot"""
    def __init__(self):
        self.data = []
        self.ylabel = ''
        self.xlabel = ''
        self.logscale = ''

class gnuplot_wrapper(object):
    """
    A wrapper for gnuplot that behaves like matplotlib.pyplot.
    It is used to switch between gnuplot and matplotlib.

    Note: Create a new wrapper instance for each plot.
    """
    def __init__(self):
        self.g = Gnuplot.Gnuplot()
        self.g('set data style line')
        self.g('set terminal png')
        self.g('set key left top')
        self.subplots = [ gnuplot_subplot() ]
        self.current_subplot = self.subplots[0]
        self.layout = (1,1)

    def subplot(self, x, y, i):
        while len(self.subplots) < x*y:
            self.subplots.append(gnuplot_subplot())
        self.layout = (x,y)
        self.current_subplot = self.subplots[i-1]

    def plot(self,x,y=None,label=None):
        if y == None:
            x, y = range(len(x)), x
        self.current_subplot.data.append(Gnuplot.Data(x, y, title=label))

    def semilogx(self,x,y,label=None):
        self.current_subplot.logscale = 'x'
        self.plot(x,y,label)

    def semilogy(self,x,y,label=None):
        self.current_subplot.logscale = 'y'
        self.plot(x,y,label)

    def loglog(self,x,y,label=None):
        self.current_subplot.logscale = 'xy'
        self.plot(x,y,label)

    def xlabel(self, label):
        self.current_subplot.xlabel = label
        
    def ylabel(self, label):
        self.current_subplot.ylabel = label

    def legend(self, *args, **kwargs):
        pass

    def grid(self, loc=None):
        self.g('set grid')
    
    def savefig(self, filename, **kwargs):
        self.g('set output "%s"' % filename)
        if len(self.subplots) > 1:
            rows, cols = self.layout
            self.g('set multiplot layout %d, %d' % (rows, cols))
        for sub in self.subplots:
            self.g('unset logscale')
            if sub.logscale != '':
                self.g('set logscale %s' % sub.logscale)
            self.g.xlabel(sub.xlabel)
            self.g.ylabel(sub.ylabel)
            self.g.plot(*sub.data)

    def close(self):
        #XXX We should empty the dataset here, as shown below.
        #However, Gnuplot.plot returns before the plotting is complete,
        #creating a race condition.  If we delete the dataset here, it leads
        #to plotting errors because Gnuplot's data dissappears before it
        #can be used.  So we do nothing.  This means that this object
        #cannot be reused, and it is a memory leak, but the cyclic garbage
        #collector should be able to handle that.
        #self.subplots = []
        pass


def plotter():
    if PLOTTER == 'gnuplot':
        return gnuplot_wrapper()
    else:
        return matplotlib.pyplot


def load(fname,comments='#',delimiter=None, skiprows=0,
         usecols=None, unpack=False, dtype=numpy.float_):
    """
    Load ASCII data from *fname* into an array and return the array.
    Adapted from pylab.load
    pylab is copyright John D. Hunter and licensed under the matplotlib license:

    License agreement for matplotlib 0.99.1

    1. This LICENSE AGREEMENT is between John D. Hunter ("JDH"), and
    the Individual or Organization ("Licensee") accessing and
    otherwise using matplotlib software in source or binary form and
    its associated documentation.

    2. Subject to the terms and conditions of this License Agreement,
    JDH hereby grants Licensee a nonexclusive, royalty-free,
    world-wide license to reproduce, analyze, test, perform and/or
    display publicly, prepare derivative works, distribute, and
    otherwise use matplotlib 0.99.1 alone or in any derivative
    version, provided, however, that JDH's License Agreement and JDH's
    notice of copyright, i.e., "Copyright (c) 2002-2009 John
    D. Hunter; All Rights Reserved" are retained in matplotlib 0.99.1
    alone or in any derivative version prepared by Licensee.

    3. In the event Licensee prepares a derivative work that is based
    on or incorporates matplotlib 0.99.1 or any part thereof, and
    wants to make the derivative work available to others as provided
    herein, then Licensee hereby agrees to include in any such work a
    brief summary of the changes made to matplotlib 0.99.1.

    4. JDH is making matplotlib 0.99.1 available to Licensee on an "AS
    IS" basis. JDH MAKES NO REPRESENTATIONS OR WARRANTIES, EXPRESS OR
    IMPLIED. BY WAY OF EXAMPLE, BUT NOT LIMITATION, JDH MAKES NO AND
    DISCLAIMS ANY REPRESENTATION OR WARRANTY OF MERCHANTABILITY OR
    FITNESS FOR ANY PARTICULAR PURPOSE OR THAT THE USE OF MATPLOTLIB
    0.99.1 WILL NOT INFRINGE ANY THIRD PARTY RIGHTS.

    5. JDH SHALL NOT BE LIABLE TO LICENSEE OR ANY OTHER USERS OF
    MATPLOTLIB 0.99.1 FOR ANY INCIDENTAL, SPECIAL, OR CONSEQUENTIAL
    DAMAGES OR LOSS AS A RESULT OF MODIFYING, DISTRIBUTING, OR
    OTHERWISE USING MATPLOTLIB 0.99.1, OR ANY DERIVATIVE THEREOF, EVEN
    IF ADVISED OF THE POSSIBILITY THEREOF.

    6. This License Agreement will automatically terminate upon a
    material breach of its terms and conditions.

    7. Nothing in this License Agreement shall be deemed to create any
    relationship of agency, partnership, or joint venture between JDH
    and Licensee. This License Agreement does not grant permission to
    use JDH trademarks or trade name in a trademark sense to endorse
    or promote products or services of Licensee, or any third party.

    8. By copying, installing or otherwise using matplotlib 0.99.1,
    Licensee agrees to be bound by the terms and conditions of this
    License Agreement.
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


def test_gnuplot_wrapper():
    """ Test function for the matplotlib gnuplot wrapper """
    pl = gnuplot_wrapper()
    pl.plot([1,2,3], label='test123')
    pl.savefig('123.png')
    pl.close()

    pl = gnuplot_wrapper()

    pl.subplot(2,2,1)
    pl.plot([1,2,3,7],[3,2,4,3])

    pl.subplot(2,2,2)
    pl.semilogx([1,2,34],[0.1,2,3], label='semilogx')
    pl.xlabel('xxx1')

    pl.subplot(2,2,3)
    pl.semilogy([1,2,34],[0.1,2,3], label='semilogy')
    pl.semilogy([2,3,4],[0.9,5,2], label='semilogy2')
    pl.ylabel('yyy1')

    pl.subplot(2,2,4)
    pl.loglog([1,10,100], [2, 4, 8], label='loglog')

    pl.grid()
    pl.savefig('2x2_test.png')
    pl.close()


if __name__ == '__main__':
    import Gnuplot
    test_gnuplot_wrapper()
    
