#! /usr/bin/python

PLOTTER='matplotlib'
#PLOTTER='gnuplot'

#The format of simulators is a dict.  The keys are the simulator's name, which
#tells spicelib how to invoke it and the spice file syntax
#The values are full paths to the executable
#If value is '', then the simulator will be assumed to be in PATH
#value can contain spaces to facilitate the use of wrapper scripts
#e.g. '/usr/local/bin/spice-wrapper gnucap'
SIMULATORS = {
    'ngspice': '',
    'gnucap': '',
    'gnucap': '/opt/gnucap/bin/gnucap',
    #'qucs', ''
    }
