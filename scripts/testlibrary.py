#!/usr/bin/python

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

BASE_DIR = os.path.join(os.getcwd(),
                        os.path.dirname(sys.argv[0]),
                        REL_DIR)

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
          "succeded": "#7FFF7F",
          "NIY": "#CFCFCF",
          "undefined": "#CFCFCF",
          "default": "#FFFFFF"}

TESTDEFS = {"npn.sym": { "dir" : BASE_DIR + "testcircuits/npn_bipolar/",
                         "schematics" : ["dc_current_gain.sch",
                                         "saturation_voltages.sch"],
                         "controller" : "plot_all.py",
                         "htmltemplate": "index.html",
                         "files": ["simulate.gnucap"]},
            "pnp.sym": { "dir" : BASE_DIR + "testcircuits/pnp_bipolar/",
                         "schematics" : ["dc_current_gain.sch",
                                         "saturation_voltages.sch"],
                         "controller" : "plot_all.py",
                         "htmltemplate": "index.html",
                         "files": ["simulate.gnucap"]},
            "npn_darlington.sym": { "dir" : BASE_DIR + "testcircuits/npn_darlington/",
                                    "schematics" : ["dc_current_gain.sch",
                                                    "saturation_voltages.sch"],
                                    "controller" : "plot_all.py",
                                    "htmltemplate": "index.html",
                                    "files": ["simulate.gnucap"]},
            "pnp_darlington.sym": { "dir" : BASE_DIR + "testcircuits/pnp_darlington/",
                                    "schematics" : ["dc_current_gain.sch",
                                                    "saturation_voltages.sch"],
                                    "controller" : "plot_all.py",
                                    "htmltemplate": "index.html",
                                    "files": ["simulate.gnucap"]},
            "npn_bin.sym": { "dir" : BASE_DIR + "testcircuits/npn_bin/",
                                    "schematics" : ["dc_current.sch"],
                                    "controller" : "plot_all.py",
                                    "htmltemplate": "index.html",
                                    "files": ["simulate.gnucap"]},
            "pnp_bin.sym": { "dir" : BASE_DIR + "testcircuits/pnp_bin/",
                                    "schematics" : ["dc_current.sch"],
                                    "controller" : "plot_all.py",
                                    "htmltemplate": "index.html",
                                    "files": ["simulate.gnucap"]},
            "npn_rbase.sym": { "dir" : BASE_DIR + "testcircuits/npn_rbase/",
                                    "schematics" : ["dc_current.sch"],
                                    "controller" : "plot_all.py",
                                    "htmltemplate": "index.html",
                                    "files": ["simulate.gnucap"]},
            "pnp_rbase.sym": { "dir" : BASE_DIR + "testcircuits/pnp_rbase/",
                                    "schematics" : ["dc_current.sch"],
                                    "controller" : "plot_all.py",
                                    "htmltemplate": "index.html",
                                    "files": ["simulate.gnucap"]},
            "diode.sym": { "dir" : BASE_DIR + "testcircuits/diode/",
                                    "schematics" : ["dc_current.sch"],
                                    "controller" : "plot_all.py",
                                    "htmltemplate": "index.html",
                                    "files": ["simulate.ngspice"]},
            "zener_diode.sym": { "dir" : BASE_DIR + "testcircuits/zener_diode/",
                                    "schematics" : ["dc_current.sch"],
                                    "controller" : "plot_all.py",
                                    "htmltemplate": "index.html",
                                    "files": ["simulate.ngspice"]},
            "zener_bidirectional.sym": { "dir" : BASE_DIR + "testcircuits/zener_bidirectional/",
                                    "schematics" : ["dc_current.sch"],
                                    "controller" : "plot_all.py",
                                    "htmltemplate": "index.html",
                                    "files": ["simulate.ngspice"]},
            "opamp.sym": { "dir" : BASE_DIR + "testcircuits/opamp/",
                                    "schematics" : ["dc_amplifier.sch"],
                                    "controller" : "plot_all.py",
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
      'zener_bidirectional': modelZenerBidirectional}.get(section, modelDiode)
    return class_(name, testdir, modeldir, properties)

class modelpartBase(object):
    def __init__(self, name, testdir, modeldir, properties):
        self.name = name
        self.testdir = testdir
        self.modeldir = modeldir
        self.properties = dict(properties)
        self.section = os.path.splitext(self.properties['symbol'])[0]
        if not self.section:
          self.section = 'undefined'

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
                self.test_status = 'succeded'
            else:
                self.test_status = 'failed'

            ## create the html file with the test results
            repl['test_result'] = self.test_message
            make_doc_hyperlink(repl)
            html = string.Template(open(test["dir"] + test["htmltemplate"], "rt").read())
            open(os.path.join(self.testdir, "index.html"),"wt").write(html.safe_substitute(repl))

        else:
            longmsg = "no test definition available"
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
        return row_template.safe_substitute(repl)

class modelDiode(modelpartBase):
  section = 'diode'
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

  def plot_all(self):
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

    command = "ngspice -b ../../../../testcircuits/" + self.section + "/simulate.ngspice"
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
    try:
        ret_plot = self.plot_reverse_voltage()
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



class modellibrary(object):

    def __init__(self, indexfilename):
        self.indexfilename = indexfilename
        self.load_files()


    def load_files(self):
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
            print "Result: ", part.test_status


    def htmlindex(self):

        rows = []
        partnames = self.modelparts.keys()
        partnames.sort(sort_modelnumber)

        for part in partnames:
            rows.append(self.modelparts[part].html_status())
        
        lib = {"indexfile": self.indexfilename,
               "testdir": self.testdir,
               "modeldir": self.modeldir,
               "title": self.description,
               "model_rows": string.join(rows,"\n")}

        if not os.path.isdir(self.testdir):
            os.makedirs(self.testdir)

        html_template = string.Template(open(BASE_DIR + TEMPLATE_FILE).read())
        open(self.testdir + "index.html", "wt").write(html_template.safe_substitute(lib))


    def test_single(self, partname):
        part = self.modelparts.get(partname, None)
        if part == None:
            raise KeyError

        print "\n" + "*"*75
        print "Testing part: " + part.name + "  model: " + self.modeldir + part.properties["file"]
        part.test()
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
    
    
    

