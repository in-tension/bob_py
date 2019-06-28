from ij import IJ, WindowManager
from ij.measure import ResultsTable
from ij.gui import NonBlockingGenericDialog, Roi, PolygonRoi
from ij.io import DirectoryChooser
from ij.plugin.frame import RoiManager

import os
# from pprint import pprint
import csv
import datetime

# import importlib
import imp




from .fiji_conv import *


import brutils as br
imp.reload(br)
# imp.reload(br)


class FijiInstUpdated :

	def __init__(self, val, date) :
		self.val = val
		self.date = date


	def __bool__(self) :
		if self.val : return True
		else : return False






UPDATE1 = FijiInstUpdated(True, datetime.date(2019, 6, 26))



IN_DEV = True
DISP = True


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


## Exper/Hemiseg/Cell/Nuc primarily used as structs

class Exper :

	def __init__(self, path, name) :
		self.path = path
		self.name = name

		self.hsegs = {}
		self.cells = {}


	def cells_to_csv(self) :

		for cell in cells :
			cell.roi.getStatistics


	def nucs_to_csv(self) :
		pass



class Hemiseg :
	def __init__(self, exper, name, suf) :
		self.exper = exper
		self.name = name
		self.suf = suf

		self.raw_imp = None
		self.nuc_bin_imp = None

		self.vl3 = None
		self.vl4 = None

		self.problem_nucs = None



class Cell :

	def __init__(self, exper, hs_suf, name) :

		self.exper = exper	## inst of Exper
		self.hs_suf = hs_suf	## just a str of L(larva #) (L|R)(Hemisegment #)
		self.name = name	## str -> vl3 or vl4


		self.nucs = []
		# self.vor = []

		self.roi = None
#		self.




	def add_nuc(self, roi) :
		nuc = Nuc(self, len(self.nucs))
		nuc.roi = roi

		self.nucs.append(nuc)




class Nuc :

	def __init__(self, cell, id_num) :
		self.cell = cell
		self.id_num = id_num

		self.roi = None

		self.vor_roi = None








def setup() :
	# set setting to save column headers
	IJ.run("Input/Output...", "jpeg=85 gif=-1 file=.csv use_file save_column");
	force_close_all()
	rm = RoiManager.getRoiManager()
	rm.reset()
	rm.show()


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
		log_dub('hemisegment {} does not have raw tif file {}'.format(hemiseg_name, hemiseg_name + RAW_SUF))
		raise Exception('hemisegment {} does not have raw tif file {}'.format(hemiseg_name, hemiseg_name + RAW_SUF))
	else :
		hseg.raw_imp = IJ.openImage(hs_files[RAW_SUF])
		if IN_DEV :
			hseg.raw_imp.show()
		hseg.cal = hseg.raw_imp.getCalibration()


	if VL3_SUF not in hs_files :
		log_dub('hemisegment {} does not have vl3 csv file {}'.format(hemiseg_name, hemiseg_name + VL3_SUF))
	else :
		vl3 = Cell(exper, hs_suf, 'vl3')
		vl3.roi = read_vl_file(hs_files[VL3_SUF], hseg.cal)
		hseg.vl3 = vl3
		exper.cells[(vl3.hs_suf, vl3.name)] = vl3
#		hseg.raw_imp.setRoi(vl3.roi)
#		if DISP :
#			rm.addRoi(vl3.roi)#, 0)
#			rm.rename(rm.getCount()-1, 'vl3')



	if VL4_SUF not in hs_files :
		log_dub('hemisegment {} does not have vl4 csv file {}'.format(hemiseg_name, hemiseg_name + VL4_SUF))
	else :
		vl4 = Cell(exper, hs_suf, 'vl4')
		vl4.roi = read_vl_file(hs_files[VL4_SUF], hseg.cal)
		hseg.vl4 = vl4
		exper.cells[(vl4.hs_suf, vl4.name)] = vl4
#		hseg.raw_imp.setRoi(vl4.roi)
#		if DISP :
#			rm.addRoi(vl4.roi)
#			rm.rename(rm.getCount()-1, 'vl4')


	## TODO: change later to get nuc from raw_imp

	if NUC_BIN_SUF not in hs_files :
		log_dub('hemisegment {} does not have nuc-bin file {}'.format(hemiseg_name, hemiseg_name + NUC_BIN_SUF))
	else :
		hseg.nuc_bin_imp = IJ.openImage(hs_files[NUC_BIN_SUF])

		# arr_dict = measure(hseg.nuc_bin_imp, headings = ["%Area"])
		# IJ.run("Colors...", "foreground=black background=white selection=yellow");
		# if arr_dict["%Area"] < 50 :
		# 	IJ.run("Colors...", "foreground=white background=black selection=yellow");


		if IN_DEV :
			hseg.nuc_bin_imp.show()


		problem_nucs = make_nucs(hseg)
		if len(problem_nucs) > 0 :
			hseg.problem_nucs = problem_nucs

		# log_dub("'fore")
		make_vor(hseg)
		# log_dub("aft'")
	## TODO: put vl stuff under relavent if statement



	exper.hsegs[hseg.name] = hseg

#	exper.hsegs.append(hseg)
#	exper.cells.append(vl3)
#	exper.cells.append(vl4)
	if DISP :
		# pass
		disp_hseg(hseg)
#		print('disp')
	return exper


def read_vl_file(file_path, cal) :

	coord_col_dict = br.csv_to_col_dict(file_path, cast_type=float)

	cal_func_dict = {'X' : cal.getRawX, 'Y' : cal.getRawY}
	for col_name, cal_func in zip(coord_col_dict.keys(), cal_func_dict.values()) :
		for i in range(len(coord_col_dict[col_name])) :

			coord_col_dict[col_name][i] = cal_func(coord_col_dict[col_name][i])

	vl_roi = PolygonRoi(coord_col_dict['X'], coord_col_dict['Y'],len(coord_col_dict['X']),Roi.POLYGON)

	return vl_roi



def make_nucs(hseg) : #, vl3, vl4) :
	# log_dub('make_nucs')
	rm = RoiManager.getRoiManager()
	rm.reset()

	if UPDATE1 :
		IJ.run(hseg.nuc_bin_imp, "Invert", "")

	rt = ResultsTable.getResultsTable()
	rt.reset()
	IJ.run(hseg.nuc_bin_imp, "Analyze Particles...", "add")

	rois = rm.getRoisAsArray()

	problem_nucs = []

#	print(rois)
	for roi in rois :
#		x = hseg.cal.getRawX(roi.getXBase())
		x = int(roi.getXBase())
		y = int(roi.getYBase())

		if hseg.vl3.roi.contains(x,y) :
	#		hseg.vl3.nucs.append( /
			hseg.vl3.add_nuc(roi)
		elif hseg.vl4.roi.contains(x,y) :
			hseg.vl4.add_nuc(roi)
		else :
			log_dub('Nuc not in vl3 or vl4 for hemisegment {}'.format(hseg.name))
			problem_nucs.append(roi)

	return problem_nucs



def make_vor(hseg) :
	vor_cell(hseg.nuc_bin_imp, hseg.vl3)
	vor_cell(hseg.nuc_bin_imp, hseg.vl4)




def vor_cell(nuc_bin_imp, cell) :
	rm = RoiManager.getRoiManager()
	rm.reset()


	# nuc_bin_imp.setRoi(cell.roi)
	nuc_bin_with_cell, offset_cell_roi = ImpWithCrop.setup_imp_and_roi(nuc_bin_imp, cell.roi)

	# print("cell.roi = {}".format(cell.roi))
	# print(nuc_bin_with_cell)

	nuc_bin_with_cell.crop_imp.setRoi(None)






	IJ.run(nuc_bin_with_cell.crop_imp, "Revert", "")
	# IJ.run(nuc_bin_with_cell.crop_imp, "Invert", "")

	IJ.run(nuc_bin_with_cell.crop_imp, "Voronoi", "")
	# input()
	# invert()
	ip = nuc_bin_with_cell.crop_imp.getProcessor()
	ip.setMinAndMax(0,1)
	IJ.run(nuc_bin_with_cell.crop_imp, "Apply LUT", "")
	IJ.run(nuc_bin_with_cell.crop_imp, "Invert", "")



	# log_dub('make_vor done')
	# hseg.nuc_bin_imp.setRoi(hseg.vl3.roi)
	# IJ.run(hseg.nuc_bin_imp, "Analyze Particles...", "add")
	# hseg.vl3.vor = rm.getRoisAsArray()



	offset_cell_roi.set_to_crop()


	IJ.run(nuc_bin_with_cell.crop_imp, "Analyze Particles...", "add")

	vor_rois = rm.getRoisAsArray()

	nuc_inds = [x for x in range(len(cell.nucs))]
	tab = '   '

	for vor_roi_crop in vor_rois :

		# print(vor_roi_crop)
		# print(roi_x//y(vor_roi_crop))
		offset_vor_roi = OffsetRoi(nuc_bin_with_cell, vor_roi_crop, crop_loc=roi_xy(vor_roi_crop))
		# print(off/set_vor_roi)
		vor_roi = offset_vor_roi.get_main_roi()
		vor_roi.setLocation(*offset_vor_roi.main_loc)

		# add_roi(vor_roi, "vor_roi")
		# vor_roi.setLocation(*offset_vor_roi.main_loc)

		# print(vor_roi)
		# input()


		temp = None
		for i, nuc_ind in enumerate(nuc_inds) :
			print(len(nuc_inds))


			nuc_roi = cell.nucs[nuc_ind].roi

			x = int(nuc_roi.getXBase())
			y = int(nuc_roi.getYBase())

			if vor_roi.contains(x,y) :

				cell.nucs[nuc_ind].vor_roi = vor_roi

				## I don't think I need to do this, I could just use i outside of loop but I don't like that
				temp = i

				break
			else :
				pass



		else :
			log_dub('cell: {}, issue with voronoi nuc match up'.format(cell.name))
			add_roi(vor_roi)

			# for nuc in cell.nucs :
			# 	add_roi(nuc.roi)


		if temp is not None :
			del nuc_inds[temp]

	# force_close(nuc_bin_with_cell.crop_imp)






## could move to class
def disp_hseg(hseg) :
	if False :
		RoiManager.getRoiManager().reset()

	hseg.raw_imp.show()
	hseg.nuc_bin_imp.show()

	# rm = RoiManager.getRoiManager()
	# rm.reset()
	add_roi(hseg.vl3.roi, name='vl3')
	add_roi(hseg.vl4.roi, name='vl4')

	for i, nuc in enumerate(hseg.vl3.nucs) :
		add_roi(nuc.roi, name='vl3 nuc{}'.format(i))

	for i, nuc in enumerate(hseg.vl3.nucs) :
		add_roi(nuc.vor_roi, name='vl3 vor{}'.format(i))

	for i, nuc in enumerate(hseg.vl4.nucs) :
		if nuc.vor_roi == None :
			print("nuc{}.vor_roi == None".format(i))
		add_roi(nuc.roi, name='vl4 nuc{}'.format(i))

	for i, nuc in enumerate(hseg.vl4.nucs) :
		if nuc.vor_roi == None :
			print("nuc{}.vor_roi == None".format(i))
		add_roi(nuc.vor_roi, name='vl4 vor{}'.format(i))

	#
	# from java.awt.event import WindowEvent
	# rm.windowActivated(WindowEvent(rm,WindowEvent.WINDOW_ACTIVATED))