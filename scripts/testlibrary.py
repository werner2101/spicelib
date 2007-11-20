#!/usr/bin/python

import sys, re, string, os
import shutil
import popen2
import ConfigParser

#################### SETUP VARS
BASE_DIR= "/home/werner/oss/geda/spicelib/"
TEMPLATE_FILE = BASE_DIR + "model_tests/tests/html_templates/modelindex.html"


ROW_TEMPLATE = """
<tr><td>$partname</td>
    <td>$value</td>
    <td>$model_url</td>
    <td>$symbol</td>
    <td bgcolor="$checksum_test_color">$checksum_test</td>
    <td bgcolor="$model_status_color">$model_status</td>
    <td bgcolor="$model_test_color">$model_test</td>
    <td>$description</td>
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

TESTDEFS = {"npn.sym": { "dir" : BASE_DIR + "model_tests/tests/npn_bipolar/",
                         "schematics" : ["dc_current_gain.sch",
                                         "saturation_voltages.sch"],
                         "controller" : "plot_all.py",
                         "htmltemplate": "index.html",
                         "files": ["simulate.gnucap"]},
            "pnp.sym": { "dir" : BASE_DIR + "model_tests/tests/pnp_bipolar/",
                         "schematics" : ["dc_current_gain.sch",
                                         "saturation_voltages.sch"],
                         "controller" : "plot_all.py",
                         "htmltemplate": "index.html",
                         "files": ["simulate.gnucap"]},
            "npn_darlington.sym": { "dir" : BASE_DIR + "model_tests/tests/npn_darlington/",
                                    "schematics" : ["dc_current_gain.sch",
                                                    "saturation_voltages.sch"],
                                    "controller" : "plot_all.py",
                                    "htmltemplate": "index.html",
                                    "files": ["simulate.gnucap"]},
            "pnp_darlington.sym": { "dir" : BASE_DIR + "model_tests/tests/pnp_darlington/",
                                    "schematics" : ["dc_current_gain.sch",
                                                    "saturation_voltages.sch"],
                                    "controller" : "plot_all.py",
                                    "htmltemplate": "index.html",
                                    "files": ["simulate.gnucap"]},
            "npn_bin.sym": { "dir" : BASE_DIR + "model_tests/tests/npn_bin/",
                                    "schematics" : ["dc_current.sch"],
                                    "controller" : "plot_all.py",
                                    "htmltemplate": "index.html",
                                    "files": ["simulate.gnucap"]},
            "pnp_bin.sym": { "dir" : BASE_DIR + "model_tests/tests/pnp_bin/",
                                    "schematics" : ["dc_current.sch"],
                                    "controller" : "plot_all.py",
                                    "htmltemplate": "index.html",
                                    "files": ["simulate.gnucap"]},
            "npn_rbase.sym": { "dir" : BASE_DIR + "model_tests/tests/npn_rbase/",
                                    "schematics" : ["dc_current.sch"],
                                    "controller" : "plot_all.py",
                                    "htmltemplate": "index.html",
                                    "files": ["simulate.gnucap"]},
            "pnp_rbase.sym": { "dir" : BASE_DIR + "model_tests/tests/pnp_rbase/",
                                    "schematics" : ["dc_current.sch"],
                                    "controller" : "plot_all.py",
                                    "htmltemplate": "index.html",
                                    "files": ["simulate.gnucap"]},
            "diode.sym": { "dir" : BASE_DIR + "model_tests/tests/diode/",
                                    "schematics" : ["dc_current.sch"],
                                    "controller" : "plot_all.py",
                                    "htmltemplate": "index.html",
                                    "files": ["simulate.ngspice"]},
            "zener_diode.sym": { "dir" : BASE_DIR + "model_tests/tests/zener_diode/",
                                    "schematics" : ["dc_current.sch"],
                                    "controller" : "plot_all.py",
                                    "htmltemplate": "index.html",
                                    "files": ["simulate.ngspice"]},
            "zener_bidirectional.sym": { "dir" : BASE_DIR + "model_tests/tests/zener_bidirectional/",
                                    "schematics" : ["dc_current.sch"],
                                    "controller" : "plot_all.py",
                                    "htmltemplate": "index.html",
                                    "files": ["simulate.ngspice"]}
            }

#################### FUNCTIONS

def test_model(param):
    testdir = ind.get("GLOBAL","TESTDIR") + param["partname"] + "/"
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

def log(x):
    open("gedaparts.log","at").write(str(x) + "\n")

def load_md5sums(filename):
    lines = open(filename, "rt").readlines()
    md5 = {}
    for l in lines:
        tok = string.split(string.strip(l),"  ")
        md5[tok[1]] = tok[0]
    return md5

#################### MAIN


if len(sys.argv) < 2:
    print "usage: " + sys.argv[0] + "options indexfile" 
    sys.exit()

if sys.argv[1] == "--notests":
    RUNTESTS = False
    indexfile = sys.argv[2]
else:
    RUNTESTS = True
    indexfile = sys.argv[1]
    
ind = ConfigParser.ConfigParser()
ind.read(indexfile)

testdir = ind.get("GLOBAL","TESTDIR")
modeldir = ind.get("GLOBAL","MODELDIR")
golden_md5 = load_md5sums(BASE_DIR + ind.get("GLOBAL","GOLDEN_SIGNATURES"))
current_md5 = load_md5sums(BASE_DIR + ind.get("GLOBAL","CURRENT_SIGNATURES"))

html_template = string.Template(open(TEMPLATE_FILE).read())
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

    
    repl["modelpath"] = BASE_DIR + modeldir + repl["file"]
    repl["partname"] = sec
    repl["model_test"] = "---"
    repl["test_result"] = "---"
    if repl.has_key("documentation"):
        if (len(repl["documentation"]) > 10) and (repl["documentation"][:4] == "http"):
            repl["documentation"] = '<a href="'+ repl["documentation"]+'">'+repl["documentation"]+'</a>'
    if RUNTESTS:
        if repl["model_status"] not in ["undefined"]:
            print "\n" + "*"*75
            print "Testing part: " + repl["partname"] + "  model: " +repl["modelpath"]
            result, shortmsg, longmsg = test_model(repl)
            if result == True:
                repl["model_test"] = "succeded"
                print "Model test succeded:", shortmsg
            else:
                repl["model_test"] = "failed"
                print "Model test failed:", shortmsg
            repl["partname"] = '<a href="'+sec+'/index.html">'+sec+'</a>'

    repl["model_url"] = '<a href="../../../'+ modeldir+'/'+repl["file"]+'">'+repl["file"]+'</a>'
    repl["model_status_color"] = color(repl["model_status"])
    repl["model_test_color"] = color(repl["model_test"])
    repl["checksum_test_color"] = color(repl["checksum_test"])
    rows.append(row_template.safe_substitute(repl))


lib = {"indexfile": indexfile,
       "testdir": testdir,
       "modeldir": ind.get("GLOBAL","MODELDIR"),
       "title": ind.get("GLOBAL","DESCRIPTION"),
       "model_rows": string.join(rows,"\n")}
open(testdir + "index.html", "wt").write(html_template.safe_substitute(lib))
