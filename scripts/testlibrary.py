#!/usr/bin/python

import sys, re, string, os
import shutil
import popen2
import ConfigParser
import getopt

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
    <td>$description $documentation2</td>
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

#################### FUNCTIONS

def test_model(param):
    testdir = param["testdir"]
    msg = " "
    longmsg = " "


    if TESTDEFS.has_key(param["symbol"]):
        test = TESTDEFS[param["symbol"]]
        ## copy all test files and the controller to dest
        if not os.path.isdir(testdir):
            os.makedirs(testdir)
        for f in (test["files"] + [test["controller"]]):
            shutil.copy(test["dir"] + f, testdir)
        ## apply the params to all schematic files
        for f in test["schematics"]:
            sch = string.Template(open(test["dir"] + f,"rt").read())
            open(testdir + f, "wt").write(sch.safe_substitute(param))
        ## run the tests
        save_cwd = os.getcwd()
        os.chdir(testdir)
        pop = popen2.Popen4("./"+test["controller"])
        longmsg = pop.fromchild.read()
        result = pop.wait()
        os.chdir(save_cwd)
        param["test_result"] = longmsg
        ## create the html file with the test results
        html = string.Template(open(test["dir"] + test["htmltemplate"], "rt").read())
        open(testdir + "index.html","wt").write(html.safe_substitute(param))

        if result == 0:
            return True, "Test succeded", longmsg
        else:
            return False, "Test failed with errorcode %i" %(result), longmsg
    else:
        longmsg = "no test definition available"
        return False, msg, longmsg


def test_single(indexfilename, partname):
    ind = ConfigParser.ConfigParser()
    ind.read(indexfilename)
    testdir = ind.get("GLOBAL","TESTDIR")
    modeldir = ind.get("GLOBAL","MODELDIR")

    repl = dict(ind.items(partname))
    repl["modelpath"] = "../../../../" + modeldir + repl["file"]
    repl["testdir"] = ind.get("GLOBAL","TESTDIR") + partname + "/"
    repl["partname"] = partname
    if repl.has_key("documentation"):
        if (len(repl["documentation"]) > 10) and (repl["documentation"][:4] == "http"):
            repl["documentation"] = '<a href="'+ repl["documentation"]+'">'+repl["documentation"]+'</a>'

    result, shortmsg, longmsg = test_model(repl)
    if result == True:
        print partname, shortmsg, ": ", repl["testdir"] + "index.html"
    else:
        print partname, shortmsg, ": ", repl["testdir"] + "index.html"


def test_library(indexfilename, runtests=False, status_list=["test","good","broken"]):
    ind = ConfigParser.ConfigParser()
    ind.read(indexfilename)
    
    testdir = ind.get("GLOBAL","TESTDIR")
    modeldir = ind.get("GLOBAL","MODELDIR")
    golden_md5 = load_md5sums(BASE_DIR + ind.get("GLOBAL","GOLDEN_CHECKSUMS"))
    current_md5 = load_md5sums(BASE_DIR + ind.get("GLOBAL","CURRENT_CHECKSUMS"))
    
    html_template = string.Template(open(BASE_DIR + TEMPLATE_FILE).read())
    row_template = string.Template(ROW_TEMPLATE)
    
    rows=[]
    secs = ind.sections()
    secs.sort(sort_modelnumber)
    for sec in secs:
        if sec == "GLOBAL":
            continue
        repl = dict(ind.items(sec))
    
        ## Checksum test
        if current_md5.has_key(modeldir + repl["file"]):
            if golden_md5.has_key(modeldir + repl["file"]):
                if current_md5[modeldir + repl["file"]] ==  golden_md5[modeldir + repl["file"]]:
                    repl["checksum_test"] = "good"
                else:
                    repl["checksum_test"] = "failed"
            else:
                repl["checksum_test"] = "missing2"
        else:
            repl["checksum_test"] = "missing1"
    
        
        repl["modelpath"] = "../../../../" + modeldir + repl["file"]
        repl["testdir"] = ind.get("GLOBAL","TESTDIR") + sec + "/"
        repl["partname"] = sec
        repl["model_test"] = "---"
        repl["test_result"] = "---"
        repl["documentation2"] = ""
        if repl.has_key("documentation"):
            if (len(repl["documentation"]) > 10) and (repl["documentation"][:4] == "http"):
                doc = repl["documentation"]
                repl["documentation"] = '<a href="'+ doc +'">'+doc+'</a>'
                repl["documentation2"] = '<a href="'+ doc +'">(d) </a>'
        if runtests:
            if repl["model_status"] in status_list:
                print "\n" + "*"*75
                print "Testing part: " + repl["partname"] + "  model: " +modeldir + repl["file"]
                result, shortmsg, longmsg = test_model(repl)
                if result == True:
                    repl["model_test"] = "succeded"
                    print sec, shortmsg, ": ", repl["testdir"] + "index.html"
                else:
                    repl["model_test"] = "failed"
                    print sec, shortmsg, ": ", repl["testdir"] + "index.html"
                repl["partname"] = '<a href="'+sec+'/index.html">'+sec+'</a>'
    
        repl["model_url"] = '<a href="../../../'+ modeldir+'/'+repl["file"]+'">'+repl["file"]+'</a>'
        repl["model_status_color"] = color(repl["model_status"])
        repl["model_test_color"] = color(repl["model_test"])
        repl["checksum_test_color"] = color(repl["checksum_test"])
        rows.append(row_template.safe_substitute(repl))
    
    
    lib = {"indexfile": indexfilename,
           "testdir": testdir,
           "modeldir": ind.get("GLOBAL","MODELDIR"),
           "title": ind.get("GLOBAL","DESCRIPTION"),
           "model_rows": string.join(rows,"\n")}
    if not os.path.isdir(testdir):
        os.makedirs(testdir)
    open(testdir + "index.html", "wt").write(html_template.safe_substitute(lib))

    
def color(text):
    if COLORS.has_key(text):
        return COLORS[text]
    else:
        return COLORS["default"]

def sort_modelnumber(a,b):
    aa = string.split(a,"_")[-1]
    bb = string.split(b,"_")[-1]
    if aa > bb:
        return 1
    elif aa < bb:
        return -1
    return 0

def load_md5sums(filename):
    lines = open(filename, "rt").readlines()
    md5 = {}
    for l in lines:
        tok = string.split(string.strip(l),"  ")
        md5[tok[1]] = tok[0]
    return md5

def usage():
    print "TBD"

#################### MAIN

try:
    opts, args = getopt.getopt(sys.argv[1:], "tip", ["test","index","part"])
except getopt.GetoptError:
    # print help information and exit:
    usage()
    sys.exit(2)

if len(args) < 1:
    usage()
    sys.exit(2)

for o, a in opts:
    if o in ("-i","--index"):
        for arg in args:
            test_library(arg)
        sys.exit()
    if o in ("-t","--test"):
        for arg in args:
            test_library(arg, runtests=True)
        sys.exit()
    if o in ("-p", "--part"):
        if len(args) < 2:
            usage()
            sys.exit(2)
        for arg in args[1:]:
            test_single(args[0],arg)
        sys.exit()
    
    

