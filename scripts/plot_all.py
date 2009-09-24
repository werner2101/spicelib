#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

import Gnuplot
import sys
import popen2
import StringIO
import numpy
import spice_read



def PlotMakerFactory(section):
  """Return a PlotMaker instance suitable for section.

  section should be a string: diode, pnp_rbase, etc
  """
  cls_dict = {
      'diode': PlotMakerDiode,
#      'npn_bin': PlotMakerNpnBin,
#      'npn_bipolar': PlotMakerNpnBipolar,
#      'npn_darlington': PlotMakerNpnDarlington,
#      'npn_rbase': PlotMakerNpnRbase,
#      'opamp': PlotMakerOpamp,
#      'pnp_bin': PlotMakerPnpBin,
#      'pnp_bipolar': PlotMakerPnpBipolar,
#      'pnp_darlington': PlotMakerPnpDarlington,
#      'pnp_rbase': PlotMakerPnpRbase,
      'zener_bidirectional': PlotMakerZenerBidirectional,
      'zener_diode': PlotMakerZenerDiode,
      }
  return cls_dict[section]()



class PlotMakerBase(object):
  """class for producing plots of devices' key response curves"""

class PlotMakerDiode(PlotMakerBase):
  def plot_forward_voltage(self):
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
        if numpy.any(Uf<0.0) or numpy.any(Uf>3.0):
            print "forward voltage out of expected range [0.0, 3.0]"
            ret = 1
        datasets.append(Gnuplot.Data(Uf, If * 1000., title = labels[n]))
    g.plot(*datasets)

    return ret
  
  def main(self):
    ME = __name__ + ": "

    command = "gnetlist -g spice-sdb -l ../../../../scripts/geda-parts.scm -o dc_current.net dc_current.sch"
    longmsg = StringIO.StringIO()

    print >>longmsg, ME, "creating netlist: ", command
    pop = popen2.Popen4(command)
    print >>longmsg, pop.fromchild.read()
    ret_gnetlist = pop.wait()
    if ret_gnetlist != 0:
        print >>longmsg, ME, "netlist creation failed with errorcode:", ret_gnetlist
    else:
        print >>longmsg, ME, "netlist creation was successful"

    command = "ngspice -b ../../../../testcircuits/diode/simulate.ngspice"
    print >>longmsg, ME, "running simulation: ", command
    pop = popen2.Popen4(command)
    print >>longmsg, pop.fromchild.read()
    ret_simulation = pop.wait()
    if ret_simulation != 0:
        print >>longmsg, ME, "simulation failed with errorcode:", ret_simulation
    else:
        print >>longmsg, ME, "simulation run was successful"

    print >>longmsg, ME, "testing and plotting"
    try:
        ret_plot = self.plot_forward_voltage()
    except Exception, data:
        print >>longmsg, ME, "plotting function died:"
        print >>longmsg, data
        result = 1

    else:
      if ret_plot == 0:
          print >>longmsg, ME, "finished testing and plotting successfully"
          result = 0
      else:
          print >>longmsg, ME, "testing or plotting failed"
          result = 2
      
    return longmsg.getvalue(), result

class PlotMakerZenerBidirectional(PlotMakerBase):
  def plot_voltages(self):
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

  def main(self):
    ME = __name__ + ": "

    longmsg = StringIO.StringIO()
    command = "gnetlist -g spice-sdb -l ../../../../scripts/geda-parts.scm -o dc_current.net dc_current.sch"

    print >>longmsg, ME, "creating netlist: ", command
    pop = popen2.Popen4(command)
    print >>longmsg, pop.fromchild.read()
    ret_gnetlist = pop.wait()
    if ret_gnetlist != 0:
        print >>longmsg, ME, "netlist creation failed with errorcode:", ret_gnetlist
    else:
        print >>longmsg, ME, "netlist creation was successful"

    command = "ngspice -b ../../../../testcircuits/zener_bidirectional/simulate.ngspice"
    print >>longmsg, ME, "running simulation: ", command
    pop = popen2.Popen4(command)
    print >>longmsg, pop.fromchild.read()
    ret_simulation = pop.wait()
    if ret_simulation != 0:
        print >>longmsg, ME, "simulation failed with errorcode:", ret_simulation
    else:
        print >>longmsg, ME, "simulation run was successful"

    print >>longmsg, ME, "testing and plotting"
    try:
        ret_plot = self.plot_voltages()
    except Exception, data:
        print >>longmsg, ME, "plotting function died:"
        print >>longmsg, data
        result = 1

    else:
      if ret_plot == 0:
          print >>longmsg, ME, "finished testing and plotting successfully"
          result = 0
      else:
          print >>longmsg, ME, "testing or plotting failed"
          result = 2

    return longmsg.getvalue(), result


class PlotMakerZenerDiode(PlotMakerBase):
  def plot_forward_voltage(self):
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
          # uf test for If < 200mA
          ind = numpy.where(If<0.2)[0]
          if numpy.any(Uf[ind] < 0.0) or numpy.any(Uf[ind]>2.0):
              print "forward voltage out of expected range [0.0, 2.0]"
              ret = 1
          datasets.append(Gnuplot.Data(Uf, If * 1000., title = labels[n]))
      g.plot(*datasets)

      g('set output "dc_reverse_voltage.png"')
      g.xlabel("Ur [V]")
      datasets = []
      plots = spice_read.spice_read("reverse_voltage.data").get_plots()
      for n,pl in enumerate(plots):
          x = pl.get_scalevector().get_data()
          yv =pl.get_datavectors()[0]
          y = yv.get_data()
          if numpy.any(-y<0.0) or numpy.any(-y>200.0):
              print "reverse voltage out of expected range [0.5, 200.0]"
              ret = 2
          datasets.append(Gnuplot.Data(-y, x*1000.0, title = labels[n]))
      g.plot(*datasets)

      return ret

  def main(self):
    ME = sys.argv[0] + ": "

    longmsg = StringIO.StringIO()
    command = "gnetlist -g spice-sdb -l ../../../../scripts/geda-parts.scm -o dc_current.net dc_current.sch"

    print >>longmsg, ME, "creating netlist: ", command
    pop = popen2.Popen4(command)
    print >>longmsg, pop.fromchild.read()
    ret_gnetlist = pop.wait()
    if ret_gnetlist != 0:
        print >>longmsg, ME, "netlist creation failed with errorcode:", ret_gnetlist
    else:
        print >>longmsg, ME, "netlist creation was successful"

    command = "ngspice -b simulate.ngspice"
    print >>longmsg, ME, "running simulation: ", command
    pop = popen2.Popen4(command)
    print >>longmsg, pop.fromchild.read()
    ret_simulation = pop.wait()
    if ret_simulation != 0:
        print >>longmsg, ME, "simulation failed with errorcode:", ret_simulation
    else:
        print >>longmsg, ME, "simulation run was successful"

    print >>longmsg, ME, "testing and plotting"
    try:
        ret_plot = self.plot_forward_voltage()
    except Exception, data:
        print >>longmsg, ME, "plotting function died:"
        print >>longmsg, data
        result = 1
        
    else:
      if ret_plot == 0:
          print >>longmsg, ME, "finished testing and plotting successfully"
          result = 0
      else:
          print >>longmsg, ME, "testing or plotting failed"
          result = 2

    return longmsg.getvalue(), result
