#!/usr/bin/python

import sys, re, string, os
import ConfigParser

#################### SETUP VARS
BASE_DIR= "/home/werner/oss/geda/spicelib/"
TEMPLATE_FILE = BASE_DIR + "model_tests/tests/html_templates/modelindex.html"
#SYMBOL_DIR = BASE_DIR + "symbol_templates/"

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
                         "htmltemplate": "npn_bipolar.html",
                         "files": ["simulate.gnucap"]},
            "pnp.sym": { "dir" : BASE_DIR + "model_tests/tests/pnp_bipolar/",
                         "schematics" : ["dc_current_gain.sch",
                                         "saturation_voltages.sch"],
                         "controller" : "plot_all.py",
                         "htmltemplate": "pnp_bipolar.html",
                         "files": ["simulate.gnucap"]},
            "darlington_npn.sym": { "dir" : BASE_DIR + "model_tests/tests/darlington_npn/",
                                    "schematics" : ["dc_current_gain.sch",
                                                    "saturation_voltages.sch"],
                                    "controller" : "plot_all.py",
                                    "htmltemplate": "darlington_npn.html",
                                    "files": ["simulate.gnucap"]},
            "darlington_pnp.sym": { "dir" : BASE_DIR + "model_tests/tests/darlington_pnp/",
                                    "schematics" : ["dc_current_gain.sch",
                                                    "saturation_voltages.sch"],
                                    "controller" : "plot_all.py",
                                    "htmltemplate": "darlington_pnp.html",
                                    "files": ["simulate.gnucap"]},
            "npn_bin.sym": { "dir" : BASE_DIR + "model_tests/tests/npn_bin/",
                                    "schematics" : ["dc_current.sch"],
                                    "controller" : "plot_all.py",
                                    "htmltemplate": "npn_bin.html",
                                    "files": ["simulate.gnucap"]},
            "pnp_bin.sym": { "dir" : BASE_DIR + "model_tests/tests/pnp_bin/",
                                    "schematics" : ["dc_current.sch"],
                                    "controller" : "plot_all.py",
                                    "htmltemplate": "pnp_bin.html",
                                    "files": ["simulate.gnucap"]},
            "npn_rbase.sym": { "dir" : BASE_DIR + "model_tests/tests/npn_rbase/",
                                    "schematics" : ["dc_current.sch"],
                                    "controller" : "plot_all.py",
                                    "htmltemplate": "npn_rbase.html",
                                    "files": ["simulate.gnucap"]},
            "pnp_rbase.sym": { "dir" : BASE_DIR + "model_tests/tests/pnp_rbase/",
                                    "schematics" : ["dc_current.sch"],
                                    "controller" : "plot_all.py",
                                    "htmltemplate": "pnp_rbase.html",
                                    "files": ["simulate.gnucap"]}
            }

#################### FUNCTIONS

def test_model(param):
    testdir = ind.get("GLOBAL","TESTDIR") + param["partname"] + "/"

    if TESTDEFS.has_key(param["symbol"]):
        test = TESTDEFS[param["symbol"]]
        ## copy all test files and the controller to dest
        os.system("mkdir -p " + testdir)
        for f in (test["files"] + [test["controller"]]):
            os.system("cp " + test["dir"] + f + " " + testdir)
        ## apply the params to all schematic files
        for f in test["schematics"]:
            sch = string.Template(open(test["dir"] + f,"rt").read())
            open(testdir + f, "wt").write(sch.safe_substitute(param))
        ## run the tests
        result = os.system("cd " + testdir + " && ./" + test["controller"])
        ## create the html file
        html = string.Template(open(test["dir"] + test["htmltemplate"], "rt").read())
        open(testdir + "index.html","wt").write(html.safe_substitute(param))
        if result == 0:
            return True
        
    return False
    
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
    repl["checksum_test"] = "NIY"
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
    if RUNTESTS:
        if repl["model_status"] in ["test"]:
            print "\n\n"+ "*"*75
            print "Testing part: " + repl["partname"] + "  model: " +repl["modelpath"]
            print "*"*75
            result = test_model(repl)
            if result == True:
                repl["model_test"] = "succeded"
            else:
                repl["model_test"] = "failed"
            repl["partname"] = '<a href="'+sec+'/index.html">'+sec+'</a>'

    repl["model_url"] = '<a href="../../../'+ modeldir+'/'+repl["file"]+'">'+repl["file"]+'</a>'
    repl["model_status_color"] = color(repl["model_status"])
    repl["model_test_color"] = color(repl["model_test"])
    repl["checksum_test_color"] = color(repl["checksum_test"])
    rows.append(row_template.safe_substitute(repl))

lib = {"indexfile": indexfile,
       "testdir": testdir,
       "modeldir": ind.get("GLOBAL","MODELDIR"),
       "model_rows": string.join(rows,"\n")}

open(testdir + "index.html", "wt").write(html_template.safe_substitute(lib))

