from ij import IJ, WindowManager
from ij.gui import NonBlockingGenericDialog, Roi, PolygonRoi
from ij.io import DirectoryChooser
from ij.plugin.frame import RoiManager

import os
from pprint import pprint
import csv
import datetime

import importlib
import imp



#from bob_py.bob_lib import *
## from bob_py.fiji_conv import *
#from bob_py.bob_lib import *
from bob_py.input import *
# from bob_py.fiji_conv import *
from fiji_utils import *
from fiji_utils import *

import brutils as br
imp.reload(br)
imp.reload(br)


__program__ = 'bob.py'





if IN_DEV :
	canceled = False
else :
	canceled = not IJ.showMessageWithCancel(__program__,'To proceed program will close all open images and windows, continue?')


if not canceled :

	Exper.setup()


	if IN_DEV :
#		exper_path = "/Users/baylieslab/Documents/Amelia/data/patrick/2019-05-20_Dmef2-2xeGFP"


		exper_path = "/Users/baylieslab/Documents/Amelia/data/steffiData/150511_Lim3b-GFP_Hoe-GFP-H4K16ac-Fib-DL-Phal"
	else :
		dir_chooser = DirectoryChooser(__program__)
		exper_path = dir_chooser.getDirectory()
		if exper_path.endswith('/') :
			exper_path = exper_path[:-1]


	exper_dir = os.path.basename(exper_path)
	exper_name = exper_dir.split('_')[:2]
	exper_name = '_'.join(exper_name)


	exper = Exper(exper_path, exper_name)



#	hemisegs = []
#	fs = os.listdir(exper_path)
#
#	for f in fs :
#		if f.startswith(exper_name) :
#			hemisegs.append(f)
#
#	#exper = run_hemiseg(exper, hemisegs[0])
#	exper = Exper(exper
#	IJ.log(exper.name)
#
#
#	for hemiseg in hemisegs :
#		exper = run_hemiseg(exper, hemiseg)
#



	hseg = br.one_value(exper.hsegs)
	vl3 = hseg.cells['vl3']
	nuc = vl3.nucs[0]

#	measure_nuc(hseg.nuc_bin_imp, vl3)
