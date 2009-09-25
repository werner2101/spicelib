#!/usr/bin/python

import numpy


PLOTTER = 'gnuplot'
#PLOTTER = 'matplotlib'


if PLOTTER == 'gnuplot':
    import Gnuplot
else:
    import matplotlib.pyplot


class gnuplot_wrapper:
    def __init__(self):
        self.g = Gnuplot.Gnuplot()
        self.g('set data style line')
        self.g('set terminal png')
        self.g('set key left top')
        self.dataset = []

    def plot(self,x,y,label=None):
        self.dataset.append(Gnuplot.Data(x,y,title=label))

    def semilogx(self,x,y,label=None):
        self.g('set logscale x')
        self.plot(x,y,label)

    def semilogy(self,x,y,label=None):
        self.g('set logscale y')
        self.plot(x,y,label)

    def loglog(self,x,y,label=None):
        self.g('set logscale xy')
        self.plot(x,y,label)

    def savefig(self, filename, **kwargs):
        self.g('set output "%s"' % filename)
        self.g.plot(*self.dataset)

    def legend(self, *args, **kwargs):
        pass

    def grid(self, loc=None):
        self.g('set grid')
    
    def close(self):
        self.dataset = []

    def xlabel(self, label):
        self.g.xlabel(label)
        
    def ylabel(self, label):
        self.g.ylabel(label)

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
