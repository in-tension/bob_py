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



from bob_py.bob_lib import *
from bob_py.fiji_conv import *
from bob_py.bob_lib import *
from bob_py.fiji_conv import *

import brutils as br
imp.reload(br)
imp.reload(br)


__program__ = 'bob.py'





if IN_DEV :
	canceled = False
else :
	canceled = not IJ.showMessageWithCancel(__program__,'To proceed program will close all open images and windows, continue?')


if not canceled :

	setup()


	if IN_DEV :
		exper_path = "/Users/baylieslab/Documents/Amelia/data/patrick/2019-05-20_Dmef2-2xeGFP"
	else :
		dir_chooser = DirectoryChooser(__program__)
		exper_path = dir_chooser.getDirectory()
		if exper_path.endswith('/') :
			exper_path = exper_path[:-1]


	exper_name = os.path.basename(exper_path)


	exper = Exper(exper_path, exper_name)



	hemisegs = []
	fs = os.listdir(exper_path)

	for f in fs :
		if f.startswith(exper_name) :
			hemisegs.append(f)

	exper = run_hemiseg(exper, hemisegs[0])

	hseg = br.one_value(exper.hsegs)
	vl3 = hseg.vl3
	nuc = vl3.nucs[0]
#	for hemiseg in hemisegs :
#		exper = run_hemiseg(exper, hemiseg)
