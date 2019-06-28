from ij import IJ, WindowManager
from ij.gui import NonBlockingGenericDialog, Roi, PolygonRoi
from ij.io import DirectoryChooser 
from ij.plugin.frame import RoiManager

import os
from pprint import pprint
import csv

import importlib
import imp





import brutils as br
imp.reload(br)
imp.reload(br)



__program__ = 'testing bob'


IN_DEV = True 
DISP = True


#FILE_SUFS = ['.tif', '_Hoe.tif', '_Nuc-bin.tif', '_XY-VL3.csv', '_XY-VL4.csv']
POT_FILE_SUFS = {	
	'raw_img' : '.tif', 
	'hoecsht' : '_Hoe.tif', 
	'nuc_bin' : '_Nuc-bin.tif', 
	'vl3' : '_XY-VL3.csv', 
	'vl4' : '_XY-VL4.csv'
}

RAW_SUF = '.tif'
HOE_SUF = '_Hoe.tif'
NUC_BIN_SUF = '_Nuc-bin.tif'
VL3_SUF = '_XY-VL3.csv'
VL4_SUF = '_XY-VL4.csv'





 
## basically custom structs

class Exper :

	def __init__(self, path, name) :
		self.path = path
		self.name = name
		
		self.hsegs = {}
		self.cells = {}

class Hemiseg :
	def __init__(self, exper, name, suf) :
		self.exper = exper
		self.name = name
		self.suf = suf

		self.raw_imp = None
		self.nuc_bin_imp = None

		self.vl3 = None
		self.vl4 = None

		

class Cell :
	
	def __init__(self, exper, hs_suf, name) :

		self.exper = exper	## inst of Exper
		self.hs_suf = hs_suf	## just a str of L(larva #) (L|R)(Hemisegment #)
		self.name = name	## str -> vl3 or vl4


		self.roi = None
#		self.

class Nuc :

	def __init__(self, cell, id_num) :
		self.cell = cell
		self.id_num = id_num


	
## not sure why this I have this instead of pprint
def pprint2(collection) :
	for item in collection :
		print(item)




def force_close_all() :
	img_titles = WindowManager.getImageTitles()
	for img_title in img_titles :
		WindowManager.getImage(img_title).close()
	
	wins = WindowManager.getAllNonImageWindows()
	for win in wins :
		win.dispose()




def setup() :
	# set setting to save column headers
	IJ.run("Input/Output...", "jpeg=85 gif=-1 file=.csv use_file save_column");
	force_close_all()
	rm = RoiManager.getRoiManager()
	rm.reset()
	rm.show()
	






def read_vl_file(file_path, cal) :

	coord_col_dict = br.csv_to_col_dict(file_path, cast_type=float)
	
	cal_func_dict = {'X' : cal.getRawX, 'Y' : cal.getRawY}
	for col_name, cal_func in zip(coord_col_dict.keys(), cal_func_dict.values()) :
		for i in range(len(coord_col_dict[col_name])) :

			coord_col_dict[col_name][i] = cal_func(coord_col_dict[col_name][i])

	vl_roi = PolygonRoi(coord_col_dict['X'], coord_col_dict['Y'],len(coord_col_dict['X']),Roi.POLYGON)
	
	return vl_roi




def run_hemiseg(exper, hemiseg_name) :
	hemiseg_path = os.path.join(exper.path, hemiseg_name)
	hs_suf = hemiseg_name.replace(exper.name+'_', '')

	hseg = Hemiseg(exper, hemiseg_name, hemiseg_path)

	hs_files = {}	## {'suf' : 'path'}
	fs = os.listdir(hemiseg_path)
	for f in fs :
		if f.startswith(hemiseg_name) :
			suf = f.replace(hemiseg_name, '', 1)
			path = os.path.join(hemiseg_path,f)
			hs_files[suf] = path


	rm = RoiManager.getRoiManager()

	
	if RAW_SUF not in hs_files :
		IJ.log('hemisegment {} does not have raw tif file {}'.format(hemiseg_name, hemiseg_name + RAW_SUF))
		raise Exception('hemisegment {} does not have raw tif file {}'.format(hemiseg_name, hemiseg_name + RAW_SUF))
	else :
		hseg.raw_imp = IJ.openImage(hs_files[RAW_SUF])
		if DISP :
			hseg.raw_imp.show()
		hseg.cal = hseg.raw_imp.getCalibration()


	if VL3_SUF not in hs_files :
		IJ.log('hemisegment {} does not have vl3 csv file {}'.format(hemiseg_name, hemiseg_name + VL3_SUF))
	else :
		vl3 = Cell(exper, hs_suf, 'vl3')
		vl3.roi = read_vl_file(hs_files[VL3_SUF], hseg.cal)
#		hseg.raw_imp.setRoi(vl3.roi)
		if DISP :
			rm.addRoi(vl3.roi)#, 0)
			rm.rename(rm.getCount()-1, 'vl3')
			

	
	if VL4_SUF not in hs_files :
		IJ.log('hemisegment {} does not have vl4 csv file {}'.format(hemiseg_name, hemiseg_name + VL4_SUF))
	else :
		vl4 = Cell(exper, hs_suf, 'vl4')
		vl4.roi = read_vl_file(hs_files[VL4_SUF], hseg.cal)
#		hseg.raw_imp.setRoi(vl4.roi)
		if DISP :
			rm.addRoi(vl4.roi)
			rm.rename(rm.getCount()-1, 'vl4')


	## TODO: change later to get nuc from raw

	if NUC_BIN_SUF not in hs_files :
		IJ.log('hemisegment {} does not have nuc-bin file {}'.format(hemiseg_name, hemiseg_name + NUC_BIN_SUF))
	else :
		hseg.nuc_bin_imp = IJ.openImage(hs_files[NUC_BIN_SUF])
		if DISP :
			hseg.nuc_bin_imp.show()



	hseg.vl3 = vl3
	hseg.vl4 = vl4

	exper.hsegs[hseg.name] = hseg
	exper.cells[(vl3.hs_suf, vl3.name)] = vl3
	exper.cells[(vl4.hs_suf, vl4.name)] = vl4
#	exper.hsegs.append(hseg)
#	exper.cells.append(vl3)
#	exper.cells.append(vl4)

	return exper

	
	

## main program


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

	run_hemiseg(exper, hemisegs[0])

#	for hemiseg in hemisegs :
#		exper = run_hemiseg(exper, hemiseg)








