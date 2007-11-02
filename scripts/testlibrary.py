#!/usr/bin/python

import sys, re, string, os
import ConfigParser

#################### SETUP VARS
BASE_DIR= "/home/werner/oss/geda/spicelib/"
TEMPLATE_FILE = BASE_DIR + "model_tests/tests/html_templates/modelindex.html"
#SYMBOL_DIR = BASE_DIR + "symbol_templates/"

ROW_TEMPLATE = """
<tr><td>$partname</td>
    <td>$symbol</td>
    <td>$file</td>
    <td>$value</td>
    <td>$modelname</td>
    <td>$footprint</td>
    <td>$model_status</td>
    <td>$checksum_test</td>
</tr> """


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
                         "files": ["simulate.gnucap"]}}

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
        return True
        
    return False
    
def log(x):
    open("gedaparts.log","at").write(str(x) + "\n")

#################### MAIN


if len(sys.argv) != 2:
    print "usage: " + sys.argv[0] + "indexfile" 
    sys.exit()

indexfile = sys.argv[1]
ind = ConfigParser.ConfigParser()
ind.read(indexfile)

testdir = ind.get("GLOBAL","TESTDIR")
modeldir = ind.get("GLOBAL","MODELDIR")

html_template = string.Template(open(TEMPLATE_FILE).read())
row_template = string.Template(ROW_TEMPLATE)

rows=[]
secs = ind.sections()
secs.sort()
for sec in secs:
    if sec == "GLOBAL":
        continue
    repl = dict(ind.items(sec))
    repl["checksum_test"] = "NIY"
    repl["modelpath"] = BASE_DIR + modeldir + repl["file"]
    repl["partname"] = sec
    if repl["model_status"] in ["test","good"]:
        result = test_model(repl)
        if result == True:
            repl["partname"] = '<a href="'+sec+'/index.html">'+sec+'</a>'
            
    rows.append(row_template.safe_substitute(repl))

lib = {"indexfile": indexfile,
       "testdir": testdir,
       "modeldir": ind.get("GLOBAL","MODELDIR"),
       "model_rows": string.join(rows,"\n")}

open(testdir + "index.html", "wt").write(html_template.safe_substitute(lib))

