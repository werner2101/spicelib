#!/usr/bin/python
# vim: ts=4 :
# vim: sw=4 :

import sys, re, string, os
import shutil
import popen2
import StringIO
import ConfigParser
import numpy

import spice_read
from plotutils import load, plotter

#################### SETUP VARS
TEMPLATE_FILE = "testcircuits/index_template.html"
REL_DIR = "../"   # relation between this script and the BASE_DIR

BASE_DIR='/home/somers/spicelib/scons/'
#BASE_DIR = os.path.join(os.getcwd(),
#                        os.path.dirname(sys.argv[0]),
#                        REL_DIR)

#################### GLOBAL DEFINITIONS

ROW_TEMPLATE = """
<tr><td>$partname</td>
    <td>$value</td>
    <td>$model_url</td>
    <td>$symbol</td>
    <td bgcolor="$checksum_test_color">$checksum_test</td>
    <td bgcolor="$model_status_color">$model_status</td>
    <td bgcolor="$model_test_color">$model_test</td>
    <td>$description $documentation</td>
</tr> """

COLORS = {"broken": "#FF3F3F",
          "good": "#7FFF7F",
          "---": "#CFCFCF",
          "test": "#FFFF7F",
          "missing1": "#FFFF7F",
          "missing2": "#FFFF7F",
          "failed": "#FF3F3F",
          "succeeded": "#7FFF7F",
          "NIY": "#CFCFCF",
          "undefined": "#CFCFCF",
          "default": "#FFFFFF"}

TESTDEFS = {"npn.sym": { "dir" : BASE_DIR + "testcircuits/npn_bipolar/",
                         "schematics" : ["dc_current_gain.sch",
                                         "saturation_voltages.sch"],
                         "htmltemplate": "index.html",
                         "files": ["simulate.gnucap"]},
            "pnp.sym": { "dir" : BASE_DIR + "testcircuits/pnp_bipolar/",
                         "schematics" : ["dc_current_gain.sch",
                                         "saturation_voltages.sch"],
                         "htmltemplate": "index.html",
                         "files": ["simulate.gnucap"]},
            "npn_darlington.sym": { "dir" : BASE_DIR + "testcircuits/npn_darlington/",
                                    "schematics" : ["dc_current_gain.sch",
                                                    "saturation_voltages.sch"],
                                    "htmltemplate": "index.html",
                                    "files": ["simulate.gnucap"]},
            "pnp_darlington.sym": { "dir" : BASE_DIR + "testcircuits/pnp_darlington/",
                                    "schematics" : ["dc_current_gain.sch",
                                                    "saturation_voltages.sch"],
                                    "htmltemplate": "index.html",
                                    "files": ["simulate.gnucap"]},
            "npn_bin.sym": { "dir" : BASE_DIR + "testcircuits/npn_bin/",
                                    "schematics" : ["dc_current.sch"],
                                    "htmltemplate": "index.html",
                                    "files": ["simulate.gnucap"]},
            "pnp_bin.sym": { "dir" : BASE_DIR + "testcircuits/pnp_bin/",
                                    "schematics" : ["dc_current.sch"],
                                    "htmltemplate": "index.html",
                                    "files": ["simulate.gnucap"]},
            "npn_rbase.sym": { "dir" : BASE_DIR + "testcircuits/npn_rbase/",
                                    "schematics" : ["dc_current.sch"],
                                    "htmltemplate": "index.html",
                                    "files": ["simulate.gnucap"]},
            "pnp_rbase.sym": { "dir" : BASE_DIR + "testcircuits/pnp_rbase/",
                                    "schematics" : ["dc_current.sch"],
                                    "htmltemplate": "index.html",
                                    "files": ["simulate.gnucap"]},
            "diode.sym": { "dir" : BASE_DIR + "testcircuits/diode/",
                                    "schematics" : ["dc_current.sch"],
                                    "htmltemplate": "index.html",
                                    "files": ["simulate.ngspice"]},
            "zener_diode.sym": { "dir" : BASE_DIR + "testcircuits/zener_diode/",
                                    "schematics" : ["dc_current.sch"],
                                    "htmltemplate": "index.html",
                                    "files": ["simulate.ngspice"]},
            "zener_bidirectional.sym": { "dir" : BASE_DIR + "testcircuits/zener_bidirectional/",
                                    "schematics" : ["dc_current.sch"],
                                    "htmltemplate": "index.html",
                                    "files": ["simulate.ngspice"]},
            "opamp.sym": { "dir" : BASE_DIR + "testcircuits/opamp/",
                                    "schematics" : ["dc_amplifier.sch"],
                                    "htmltemplate": "index.html",
                                    "files": ["simulate.ngspice"]}
            }


#################### CLASSES

class modelpart(object):
    def __new__(cls, name, testdir, modeldir, properties):
        d = dict(properties)
        section = os.path.splitext(d['symbol'])[0]

        class_ = {'diode': modelDiode,
                  'zener_diode': modelZenerDiode,
                  'zener_bidirectional': modelZenerBidirectional,
                  'npn': modelNPNBipolar,
                  'pnp': modelPNPBipolar,
                  'pnp_rbase': modelPNPRbase,
                  'npn_rbase': modelNPNRbase,
                  'pnp_bin': modelPNPBin,
                  'npn_bin': modelNPNBin,
                  'npn_darlington': modelNPNDarlington,
                  'pnp_darlington': modelPNPDarlington,
                  'opamp': modelOpamp}.get(section, modelpartBase)

        return class_(name, testdir, modeldir, properties)


class modelpartBase(object):
    section = 'undefined'

    def __init__(self, name, testdir, modeldir, properties):
        self.name = name
        self.testdir = testdir
        self.modeldir = modeldir
        self.properties = dict(properties)

        self.golden_checksum = None
        self.current_checksum = None
        self.checksum_status = None
        self.test_status = None

    def test(self):
        if TESTDEFS.has_key(self.properties["symbol"]):
            test = TESTDEFS[self.properties["symbol"]]
            ## copy all test files and the controller to dest
            if not os.path.isdir(self.testdir):
                os.makedirs(self.testdir)

            repl = {}
            repl.update(self.properties)
            repl['partname'] = self.name

            ## apply the properties to all schematic files
            for f in test["schematics"]:
                sch = string.Template(open(test["dir"] + f,"rt").read())
                open(os.path.join(self.testdir, f), "wt").write(sch.safe_substitute(repl))

            ## run the tests
            save_cwd = os.getcwd()
            os.chdir(self.testdir)
            self.test_message, result = self.plot_all()
            os.chdir(save_cwd)

            if result == 0:
                self.test_status = 'succeeded'
            else:
                self.test_status = 'failed'

            ## create the html file with the test results
            repl['test_result'] = self.test_message
            repl['modelpath'] = os.path.join('../../../../', self.modeldir, self.properties['file'])
            make_doc_hyperlink(repl)
            html = string.Template(open(test["dir"] + test["htmltemplate"], "rt").read())
            open(os.path.join(self.testdir, "index.html"),"wt").write(html.safe_substitute(repl))

        else:
            self.test_message = "no test definition available"
            return False, self.test_message

    def checksums(self, golden, current):
        if golden == False and current == False:
            self.checksum_status = 'neither'
        elif golden != False and current == False:
            self.checksum_status = 'missing1'
        elif golden == False and current != False:
            self.checksum_status = 'missing2'
        elif golden == current:
            self.checksum_status = 'good'
        else:
            self.checksum_status = 'failed'

        self.golden_checksum = golden
        self.current_checksum = current

    def html_status(self):
        repl = {}
        repl.update(self.properties)

        if os.path.exists(os.path.join(self.testdir, 'index.html')):
            repl['partname'] = '<a href="%s">%s</a>' % (os.path.join(self.name, 'index.html'), self.name)
        else:
            repl["partname"] = self.name

        make_doc_hyperlink(repl, docname='(d) ')

        repl["model_url"] = '<a href="../../../' + self.modeldir +'/'+repl["file"]+'">'+repl["file"]+'</a>'
        repl["model_status_color"] = color(repl["model_status"])
        repl["model_test"] = self.test_status
        repl["model_test_color"] = color(self.test_status)
        repl["checksum_test"] = self.checksum_status
        repl["checksum_test_color"] = color(self.checksum_status)

        row_template = string.Template(ROW_TEMPLATE)
        if not os.path.isdir(self.testdir):
            os.makedirs(self.testdir)
        status = row_template.safe_substitute(repl)
        open(os.path.join(self.testdir, 'status.htm'), 'w').write(status)
        return status

    def plot_all(self):
        ME = os.path.split(__file__)[1]
        longmsg = StringIO.StringIO()
        result = 0

        for sch in TESTDEFS[self.properties['symbol']]['schematics']:
            net = os.path.splitext(sch)[0] + '.net'
            command = "gnetlist -g spice-sdb -l ../../../../scripts/geda-parts.scm -o %s %s" \
                      %(net, sch)
            print >>longmsg, ME, "creating netlist: ", command
            pop = popen2.Popen4(command)
            ret_gnetlist = pop.wait()
            print >>longmsg, pop.fromchild.read()
            if ret_gnetlist != 0:
                print >>longmsg, ME, "netlist creation failed with errorcode:", ret_gnetlist
            else:
                print >>longmsg, ME, "netlist creation was successful"

        command = self.simulator + " -b ../../../../testcircuits/" + self.section + "/simulate." + self.simulator
        print >>longmsg, ME, "running simulation: ", command
        pop = popen2.Popen4(command)
        print >>longmsg, pop.fromchild.read()
        ret_simulation = pop.wait()
        if ret_simulation != 0:
            print >>longmsg, ME, "simulation failed with errorcode:", ret_simulation
        else:
            print >>longmsg, ME, "simulation run was successful"
  
        print >>longmsg, ME, "testing and plotting"
        for meth in self.plot_methods:
            try:
                ret_plot = getattr(self, meth)()
            except Exception, data:
                print >>longmsg, ME, "plotting function died:"
                print >>longmsg, data
                result = 1
            else:
                if ret_plot != 0:
                    print >>longmsg, ME, "testing or plotting failed"
                    result = 2
        if result == 0:
            print >>longmsg, ME, "finished testing and plotting successfully"
        return longmsg.getvalue(), result


class modelDiode(modelpartBase):
    section = 'diode'
    plot_methods = ['plot_forward_voltage', 'plot_reverse_voltage']
    simulator = 'ngspice'

    def forward_voltage_ok(self, If, Uf):
        if numpy.any(Uf<0.0) or numpy.any(Uf>3.0):
            print "forward voltage out of expected range [0.0, 3.0]"
            return False
        else:
            return True

    def plot_forward_voltage(self):
        pp = plotter()
        labels = ["0C", "25C", "50C", "75C", "100C"]
        ret = 0
        plots = spice_read.spice_read("forward_voltage.data").get_plots()
        for n,pl in enumerate(plots):
            If = -pl.get_scalevector().get_data()
            Uf = pl.get_datavectors()[0].get_data()
            if not self.forward_voltage_ok(If, Uf):
                ret = 1
            if not numpy.any(numpy.isnan(If)) and not numpy.any(numpy.isnan(Uf)):
                pp.semilogy(Uf, If*1000.0,label = labels[n])
        pp.ylabel("If [mA]")
        pp.xlabel("Uf [V]")
        pp.grid()
        pp.legend(loc="best")
        pp.savefig("dc_forward_voltage.png",dpi=80)
        pp.close()
        return ret
  
    def plot_reverse_voltage(self):
        #Basic diode has no reverse voltage plot
        return 0


class modelZenerDiode(modelDiode):
    section = 'zener_diode'

    def forward_voltage_ok(self, If, Uf):
        ind = numpy.where(If < 0.2)[0]
        if numpy.any(Uf[ind] < 0.0) or numpy.any(Uf[ind] > 2.0):
            print "forward voltage out of expected range [0.0, 2.0]"
            return False
        else:
            return True

    def reverse_voltage_ok(self, Ir, Ur):
        if numpy.any(-Ur < 0.0) or numpy.any(-Ur > 200.0):
            print "reverse voltage out of expected range [0.0, 200.0]"
            return False
        else:
            return True

    def plot_reverse_voltage(self):
        pp = plotter()
        labels = ["0C", "25C", "50C", "75C", "100C"]
        ret = 0
        plots = spice_read.spice_read("reverse_voltage.data").get_plots()
        for n,pl in enumerate(plots):
            Ir = pl.get_scalevector().get_data()
            Ur = pl.get_datavectors()[0].get_data()
            if not self.reverse_voltage_ok(Ir, Ur):
                ret = 2
            if not numpy.any(numpy.isnan(Ir)) and not numpy.any(numpy.isnan(Ur)):
                pp.semilogy(-Ur, Ir * 1000.0, label = labels[n])
        pp.ylabel("Ir [mA]")
        pp.xlabel("Ur [V]")
        pp.grid()
        pp.legend(loc="best")
        pp.savefig("dc_reverse_voltage.png",dpi=80)
        pp.close()
        return ret


class modelZenerBidirectional(modelZenerDiode):
    section = 'zener_bidirectional'

    def forward_voltage_ok(self, If, Uf):
        if numpy.any(Uf < 0.5) or numpy.any(Uf > 200.0):
            print "forward voltage out of expected range [0.5, 200.0]"
            return False
        else:
            return True

    def reverse_voltage_ok(self, Ir, Ur):
        if numpy.any(Ur < -200.) or numpy.any(Ur > -0.5):
            print "reverse voltage out of expected range [0.5, 200]"
            return False
        else:
          return True


class modelTransistor(modelpartBase):
    pass


class modelBipolar(modelTransistor):
    plot_methods = ['plot_dc_current_gain', 'plot_saturation_voltages']
    simulator = 'gnucap'

    def plot_dc_current_gain(self):
        pp = plotter()
        mm=[]
        mm.append(("0 C", load("dc_current_gain_t0.data")))
        mm.append(("25 C",load("dc_current_gain_t25.data")))
        mm.append(("50 C",load("dc_current_gain_t50.data")))
        mm.append(("75 C",load("dc_current_gain_t75.data")))
        mm.append(("100 C",load("dc_current_gain_t100.data")))

        for t,m in mm:
            hfe = m[:,1] / m[:,2]
            Ic = -m[:,1]
            pp.semilogx(Ic * 1000, hfe, label=t)
        pp.xlabel("Ic [mA]")
        pp.ylabel("hfe")
        pp.grid()
        pp.legend(loc="best")
        pp.savefig("dc_current_gain.png",dpi=80)
        pp.close()

        for t,m in mm:
            pp.semilogx(-m[:,1]*1000, self.icc_sign * m[:,3]*1000,label=t)
        pp.xlabel("Ic [mA]")
        pp.ylabel("V BE [mV]")
        pp.grid()
        pp.legend(loc='best')
        pp.savefig("base_emitter_voltage.png",dpi=80)
        pp.close()
        return 0

    def plot_saturation_voltages(self):
        pp = plotter()
        mm=[]
        mm.append(("0 C", load("saturation_voltages_t0.data")))
        mm.append(("25 C",load("saturation_voltages_t25.data")))
        mm.append(("50 C",load("saturation_voltages_t50.data")))
        mm.append(("75 C",load("saturation_voltages_t75.data")))
        mm.append(("100 C",load("saturation_voltages_t100.data")))

        for t,m in mm:
            ## only plot the values where Vce sat is smaller than a limit
            firstind = numpy.where(self.icc_sign * m[:,3] < self.VCEsat_plot_limit)[0][0]
            Ic = -m[firstind:,1]
            pp.loglog(Ic * 1000, self.icc_sign * m[firstind:,3]*1000,label=t)
        pp.xlabel("Ic [mA]")
        pp.ylabel("VCE sat [mV]")
        pp.grid()
        pp.legend(loc='best')
        pp.savefig("vce_saturation_voltage.png",dpi=80)
        pp.close()

        for t,m in mm:
            pp.semilogx(-m[:,1]*1000, self.icc_sign * m[:,2]*1000,label=t)
        pp.xlabel("Ic [mA]")
        pp.ylabel("V BE sat [mV]")
        pp.grid()
        pp.legend(loc='best')
        pp.savefig("vbe_saturation_voltage.png",dpi=80)
        pp.close()
        return 0


class modelNPNBipolar(modelBipolar):
    VCEsat_plot_limit = 1.0  #amps
    section = 'npn_bipolar'
    icc_sign = 1. #Sign of the collector current


class modelNPNDarlington(modelBipolar):
    VCEsat_plot_limit = 2.0  #amps
    section = 'npn_darlington'
    icc_sign = 1. #Sign of the collector current


class modelPNPBipolar(modelBipolar):
    VCEsat_plot_limit = 1.0  #amps
    section = 'pnp_bipolar'
    icc_sign = -1. #Sign of the collector current


class modelPNPDarlington(modelBipolar):
    VCEsat_plot_limit = 2.0  #amps
    section = 'pnp_darlington'
    icc_sign = -1. #Sign of the collector current


class modelResistorEquippedTransistor(modelBipolar):
    """Base class transistors with base and/or collector resistors"""
    plot_methods = ['plot_dc_current']

    def base_current_ok(self, Uin, Iin):
        return True #stub function, must be overridden by child classes

    def collector_current_ok(self, Uin, Ic):
        return True #stub function, must be overridden by child classes

    def plot_dc_current(self):
        ret = 0
        pp = plotter()
        mm=[]

        mm.append(("0 C", load("dc_current_t0.data")))
        mm.append(("25 C",load("dc_current_t25.data")))
        mm.append(("50 C",load("dc_current_t50.data")))
        mm.append(("75 C",load("dc_current_t75.data")))
        mm.append(("100 C",load("dc_current_t100.data")))

        for t,m in mm:
            Uin = m[:,0]
            Iin = -m[:,1]
            if not self.base_current_ok(Uin, Iin):
                ret = 1
            pp.plot(Uin, Iin * 1000,label=t)
        pp.xlabel("Uin [V]")
        pp.ylabel("IB [mA]")
        pp.grid()
        pp.legend(loc="best")
        pp.savefig("dc_IB.png",dpi=80)
        pp.close()

        for t,m in mm:
            Uin = m[:,0]
            Ic = -m[:,2]
            if not self.collector_current_ok(Uin, Ic):
                ret = 1
            pp.plot(Uin, Ic * 1000,label=t)
        pp.xlabel("Uin [V]")
        pp.ylabel("IC [mA]")
        pp.grid()
        pp.legend(loc='best')
        pp.savefig("dc_IC.png",dpi=80)
        pp.close()
        return ret


class modelPNPRbase(modelResistorEquippedTransistor):
    section = 'pnp_rbase'


class modelNPNRbase(modelResistorEquippedTransistor):
    section = 'npn_rbase'


class modelBipolarBin(modelResistorEquippedTransistor):
    plot_methods = ['plot_dc_current']
    simulator = 'gnucap'

    def base_current_ok(self, Uin, Iin):
        if numpy.any(Iin < -.001) or numpy.any(Iin > 1.0):
            print "input current out of expected range [-0.001, 1.0]"
            return False
        else:
            return True

    def collector_current_ok(self, Uin, Ic):
        if numpy.any(Ic < -.001) or numpy.any(Ic > 100.0):
            print "collector current out of expected range [-0.001, 100.0]"
            return False
        else:
            return True


class modelPNPBin(modelBipolarBin):
    section = 'pnp_bin'


class modelNPNBin(modelBipolarBin):
    section = 'npn_bin'


class modelOpamp(modelpartBase):
    section = 'opamp'
    plot_methods = ['plot_dc_amplifier']
    simulator = 'ngspice'
    def plot_dc_amplifier(self):
        pp = plotter()
        
        plots = spice_read.spice_read("dc_amplifier.data").get_plots()
        x = plots[0].get_scalevector().get_data()
        vin = plots[0].get_datavectors()[0].get_data()
        vout = plots[0].get_datavectors()[1].get_data()
        
        pp.plot(x, vin, label="v(in)")
        pp.plot(x, vout, label="v(out)")
        pp.xlabel("Uin [V]")
        pp.ylabel("U [V]")
        pp.grid()
        pp.legend(loc="best")
        pp.savefig("dc_amplifier.png",dpi=80)
        pp.close()
        return 0


class modellibrary(object):

    def __init__(self, indexfilename):
        self.indexfilename = indexfilename
        self.load_library_index()
        self.test_library_index()

    def load_library_index(self):
        self.index = ConfigParser.ConfigParser()
        self.index.read(self.indexfilename)
        self.testdir = self.index.get("GLOBAL","TESTDIR")
        self.modeldir = self.index.get("GLOBAL","MODELDIR")
        self.description = self.index.get("GLOBAL","DESCRIPTION")
        self.golden_md5 = self.load_md5sums(BASE_DIR + self.index.get("GLOBAL","GOLDEN_CHECKSUMS"))
        self.current_md5 = self.load_md5sums(BASE_DIR + self.index.get("GLOBAL","CURRENT_CHECKSUMS"))

        self.modelparts = {}

        for sec in self.index.sections():
            if sec == "GLOBAL":
                continue
            part = modelpart(sec, self.testdir + sec, self.modeldir, self.index.items(sec))
            self.modelparts[part.name] = part

            modelpath = self.modeldir + part.properties['file']
            part.checksums(self.golden_md5.get(modelpath, False),
                           self.current_md5.get(modelpath, False))

    def test_library_index(self):
        """
        test the used model files against the files in the index
        """
        files_index = set()
        self.modelfiles_used_twice = set()

        for sec in self.index.sections():
            if sec == "GLOBAL":
                continue
            modelfile = self.index.get(sec, 'file')
            if modelfile in files_index:
                self.modelfiles_used_twice.add(modelfile)
            else:
                files_index.add(modelfile)

        modeldir = self.index.get('GLOBAL', 'MODELDIR')
        files_directory = set(os.listdir(modeldir))
        self.modelfiles_unused = files_directory - files_index
        self.modelfiles_not_found = files_index - files_directory
            
    def load_md5sums(self, filename):
        lines = open(filename, "rt").readlines()
        md5 = {}
        for l in lines:
            tok = string.split(string.strip(l),"  ")
            md5[tok[1]] = tok[0]
        return md5

    def test(self, status=None, checksum=None):
        ignore_status = ['undefined', 'new']

        partnames = self.modelparts.keys()
        partnames.sort(sort_modelnumber)

        for partname in partnames:
            part = self.modelparts[partname]

            if part.properties['model_status'] in ignore_status:
                continue
            if status != None:
                if status != part.properties['model_status']:
                    continue
            if checksum != None:
                if checksum != part.checksum_status:
                    continue

            print "\n" + "*"*75
            print "Testing part: " + part.name + "  model: " + self.modeldir + part.properties["file"]
            part.test()
            part.html_status()
            print "Result: ", part.test_status

    def htmlindex(self):
        rows = []
        partnames = self.modelparts.keys()
        partnames.sort(sort_modelnumber)

        for part in partnames:
            try:
                rows.append(open(os.path.join(self.modelparts[part].testdir, 'status.htm')).read())
            except IOError:
                rows.append(self.modelparts[part].html_status())
        
        lib = {"indexfile": self.indexfilename,
               "testdir": self.testdir,
               "modeldir": self.modeldir,
               "title": self.description,
               "model_rows": '\n'.join(rows),
               "modelfiles_not_found": ', '.join(list(self.modelfiles_not_found)),
               "modelfiles_used_twice": ', '.join([self.model_url(s) for s in self.modelfiles_used_twice]),
               "modelfiles_unused": ', '.join([self.model_url(s) for s in self.modelfiles_unused])}

        if not os.path.isdir(self.testdir):
            os.makedirs(self.testdir)

        html_template = string.Template(open(BASE_DIR + TEMPLATE_FILE).read())
        open(self.testdir + "index.html", "w").write(html_template.safe_substitute(lib))

    def model_url(self, modelname):
        modeldir = self.index.get('GLOBAL','MODELDIR')
        return '<a href="%s">%s</a>' % (os.path.join('../../../', modeldir, modelname), modelname)

    def test_single(self, partname):
        part = self.modelparts.get(partname, None)
        if part == None:
            raise KeyError

        print "\n" + "*"*75
        print "Testing part: " + part.name + "  model: " + self.modeldir + part.properties["file"]
        part.test()
        part.html_status()
        print "Result: ", part.test_status
        

#################### FUNCTIONS

def color(text):
    if COLORS.has_key(text):
        return COLORS[text]
    else:
        return COLORS["default"]


def make_doc_hyperlink(repl, docname=None):
    if docname == None:
      docname = repl['documentation']
    if re.match('http://', repl.get('documentation', '')):
        repl["documentation"] = '<a href="'+ repl["documentation"] +'">' + docname + '</a>'


def sort_modelnumber(a,b):
    aa = string.split(a,"_")[-1]
    bb = string.split(b,"_")[-1]
    return cmp(aa,bb)


def usage():
    print "usage is:"
    print "  -i --index libraryname1 [libraryname2, ..]"
    print "  -t --test libraryname1 [libraryname2, ..]"
    print "  -p --part libraryname partname1 [partname2, ..]"
    print "  -s --status status: check/list only one given status"
    print "  -c --checksum checksum: check/list only one checksum status"


#################### MAIN

if __name__ == "__main__":
    import getopt

    try:
        opts, args = getopt.getopt(sys.argv[1:], "tips:c:",
                                   ["test","index","part","status=","checksum="])
    except getopt.GetoptError:
        # print help information and exit:
        usage()
        sys.exit(2)

    if len(args) < 1:
        usage()
        sys.exit(2)

    mode="undefined"
    status = None
    checksum = None

    for o, a in opts:
        if o in ("-i","--index"):
            mode = "index"
        if o in ("-t","--test"):
            mode = "test"
        if o in ("-p", "--part"):
            mode = "part"
        if o in ("-s", "--status"):
            status = a
        if o in ("-c", "--checksum"):
            checksum = a


    if mode == "undefined":
        usage()
        sys.exit(2)
    elif mode == "index":
        for arg in args:
            library = modellibrary(arg)
            library.htmlindex()
    elif mode == "test":
        for arg in args:
            library = modellibrary(arg)
            library.htmlindex()
            library.test(checksum=checksum, status=status)
            library.htmlindex()
    elif mode == "part":
        if len(args) < 2:
            usage()
            sys.exit(2)
        
        library = modellibrary(args[0])
        for arg in args[1:]:
            library.test_single(arg)
        library.htmlindex()
    
    
    

