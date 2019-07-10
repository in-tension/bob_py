from ij import IJ, WindowManager
from ij.measure import ResultsTable
from ij.gui import NonBlockingGenericDialog, Roi, PolygonRoi
from ij.io import DirectoryChooser
from ij.plugin import Duplicator

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

		# self.vl3 = None
		# self.vl4 = None

		self.cells = {}

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
		IJ.log('hemisegment {} does not have raw tif file {}'.format(hemiseg_name, hemiseg_name + RAW_SUF))
		# raise Exception('hemisegment {} does not have raw tif file {}'.format(hemiseg_name, hemiseg_name + RAW_SUF))
	else :
		hseg.raw_imp = IJ.openImage(hs_files[RAW_SUF])
		if IN_DEV :
			hseg.raw_imp.show()
		hseg.cal = hseg.raw_imp.getCalibration()

	## TODO: Hemiseg as dict cells, currently manually doing keys
	## in future, change csv file suf to _<muscle-name>_cell-roi.csv
	if VL3_SUF not in hs_files :
		IJ.log('hemisegment {} does not have vl3 csv file {}'.format(hemiseg_name, hemiseg_name + VL3_SUF))
	else :
		vl3 = Cell(exper, hs_suf, 'vl3')
		vl3.roi = read_vl_file(hs_files[VL3_SUF], hseg.cal)
		hseg.cells['vl3'] = vl3
		# hseg.vl3 = vl3
		exper.cells[(vl3.hs_suf, vl3.name)] = vl3


	if VL4_SUF not in hs_files :
		IJ.log('hemisegment {} does not have vl4 csv file {}'.format(hemiseg_name, hemiseg_name + VL4_SUF))
	else :
		vl4 = Cell(exper, hs_suf, 'vl4')
		vl4.roi = read_vl_file(hs_files[VL4_SUF], hseg.cal)
		hseg.cells['vl4'] = vl4

		#hseg.vl4 = vl4
		exper.cells[(vl4.hs_suf, vl4.name)] = vl4


	## TODO: change to get nuc from raw_imp instead of nuc_bin_imp
	if NUC_BIN_SUF not in hs_files :
		IJ.log('hemisegment {} does not have nuc-bin file {}'.format(hemiseg_name, hemiseg_name + NUC_BIN_SUF))
	else :
		hseg.nuc_bin_imp = IJ.openImage(hs_files[NUC_BIN_SUF])

		if IN_DEV :
			hseg.nuc_bin_imp.show()


		problem_nucs = make_nucs(hseg)
		if len(problem_nucs) > 0 :
			hseg.problem_nucs = problem_nucs

		make_vor(hseg)



	exper.hsegs[hseg.name] = hseg


	if DISP :
		disp_hseg(hseg)


	return exper

def csv_to_col_dict(csv_path, cast_type=str) :
    """
    | reads a csv file and creates a dict of cols
    | assumes first row is col names and that all are unique
    """
    rows = csv_to_rows(csv_path)
    # print(rows)
    # print('\n\n')

    if cast_type is not None :
        temp = [rows[0]]
        temp.extend(arrs_cast_spec(rows[1:], cast_type=cast_type))
        rows = temp

    # print(rows)

    cols = rotate(rows)


    col_dict = {}
    for col in cols :
        col_dict[col[0]] = col[1:]

    return col_dict


def read_vl_file(file_path, cal) :
	roi_csv_headings = ['X', 'Y']
	# coord_col_dict_raw = br.csv_to_col_dict(file_path, cast_type=float)
	#
	# if list(coord_col_dict_raw.keys()) == roi_csv_headings :
	# 	coord_col_dict = coord_col_dict_raw
	# else :
	# 	coord_col_dict = {}
	#
	# 	for (val, col), heading in zip(coord_col_dict_raw.items(), roi_csv_headings) :
	# 		temp = [float(val)]
	# 		temp.extend(col)
	# 		coord_col_dict[heading] = temp
	# 	# print(
	# 	print(coord_col_dict)
	coord_rows = br.csv_to_rows(file_path, cast_type=float)
	if coord_rows[0] == roi_csv_headings :
		coord_col_dict = br.csv_to_col_dict(file_path, cast_type=float)
	else :
		coord_cols = br.rotate(coord_rows)
		coord_col_dict = {'X':coord_cols[0], 'Y':coord_cols[1]}

	cal_func_dict = {'X' : cal.getRawX, 'Y' : cal.getRawY}
	for col_name, cal_func in zip(coord_col_dict.keys(), cal_func_dict.values()) :
		for i in range(len(coord_col_dict[col_name])) :

			coord_col_dict[col_name][i] = cal_func(coord_col_dict[col_name][i])

	vl_roi = PolygonRoi(coord_col_dict['X'], coord_col_dict['Y'],len(coord_col_dict['X']),Roi.POLYGON)

	return vl_roi



def make_nucs(hseg) :
	rm = RoiManager.getRoiManager()
	rm.reset()

	if UPDATE1 :
		IJ.run(hseg.nuc_bin_imp, "Invert", "")

	rt = ResultsTable.getResultsTable()
	rt.reset()
	IJ.run(hseg.nuc_bin_imp, "Analyze Particles...", "add")

	rois = rm.getRoisAsArray()

	problem_nucs = []

	for roi in rois :

		nuc_cent = roi_cent(roi, integer=True)

		found_cell = False
		for cell in hseg.cells.values() :
			if cell.roi.contains(*nuc_cent) :
				cell.add_nuc(roi)
				found_cell = True
				break
		# if hseg.vl3.roi.contains(*nuc_cent) :
		# 	hseg.vl3.add_nuc(roi)
		# elif hseg.vl4.roi.contains(*nuc_cent) :
		# 	hseg.vl4.add_nuc(roi)
		if not found_cell :
			IJ.log('Nuc not in any cell for hemisegment {}'.format(hseg.name))
			problem_nucs.append(roi)

	return problem_nucs



def make_vor(hseg) :
	for cell in hseg.cells.values() :
		IJ.log(cell.name)
		vor_cell(hseg.nuc_bin_imp, cell)
	# vor_cell(hseg.nuc_bin_imp, hseg.vl3)
	# vor_cell(hseg.nuc_bin_imp, hseg.vl4)




def vor_cell(nuc_bin_imp, cell) :
	rm = RoiManager.getRoiManager()
	rm.reset()



	# nuc_bin_cell = dup_and_crop(nuc_bin_imp, cell.roi)


	# nuc_bin_with_cell, offset_cell_roi = ImpWithCrop.setup_imp_and_roi(nuc_bin_imp, cell.roi)
	# nuc_bin_with_cell.crop_imp.setRoi(None)

	d = Duplicator()
	nuc_bin_copy = d.run(nuc_bin_imp)


	IJ.run(nuc_bin_copy, "Make Binary", "")
	# IJ.run(nuc_bin_copy, "Invert", "")
	nuc_bin_copy.show()

	nuc_bin_copy.setRoi(cell.roi)
	IJ.run(nuc_bin_copy, "Clear Outside", "")
	IJ.run(nuc_bin_copy, "Voronoi", "")

	# IJ.run(nuc_bin_with_cell.crop_imp, "Revert", "")
	# # IJ.run(nuc_bin_with_cell.crop_imp, "Invert", "")
	# IJ.run(nuc_bin_with_cell.crop_imp, "Voronoi", "")
	#
	ip = nuc_bin_copy.getProcessor()
	ip.setMinAndMax(0,1)
	IJ.run(nuc_bin_copy, "Apply LUT", "")
	# IJ.run(nuc_bin_with_cell.crop_imp, "Invert", "")


	# offset_cell_roi.set_to_crop()
	nuc_bin_copy.setRoi(cell.roi)
	IJ.run(nuc_bin_copy, "Invert", "")
#

	IJ.run(nuc_bin_copy, "Analyze Particles...", "add")
	vor_rois = rm.getRoisAsArray()





	nuc_inds = [x for x in range(len(cell.nucs))]
	for vor_roi in vor_rois :
		# offset_vor_roi = OffsetRoi(nuc_bin_with_cell, vor_roi_crop, crop_loc=roi_xy(vor_roi_crop))
		# vor_roi = offset_vor_roi.get_main_roi()
		# vor_roi.setLocation(*offset_vor_roi.main_loc)
		#
		#
		temp = None
		for i, nuc_ind in enumerate(nuc_inds) :
			nuc_roi = cell.nucs[nuc_ind].roi

			nuc_cent = roi_cent(nuc_roi, integer=True)
			# nuc_cent = [int(nuc_cent[0]), int(nuc_cent[1])]

			if vor_roi.contains(*nuc_cent) :

				cell.nucs[nuc_ind].vor_roi = vor_roi

				## I don't think I need to do this, I could just use i outside of loop but it feels so insecure or something
				temp = i

				break
			else :
				pass




		else :
			IJ.log('cell: {}, issue with voronoi nuc match up'.format(cell.name))

			# rm.reset()
			#
			# for i, nuc in enumerate(cell.nucs) :
			#
			# 	x = int(nuc.roi.getXBase())
			# 	y = int(nuc.roi.getYBase())
			# 	print('{}. ({},{})'.format(i,x,y))
			# 	add_roi(Roi(x,y,10,10), str(i))
			# print(nuc_inds)
			#
			# add_roi(vor_roi, "vor_roi")




		if temp is not None :
			del nuc_inds[temp]


	force_close(nuc_bin_copy)






## could move to class
def disp_hseg(hseg) :
	if True :
		RoiManager.getRoiManager().reset()

	hseg.raw_imp.show()
	hseg.nuc_bin_imp.show()



	for cell in hseg.cells.values() :

		add_roi(cell.roi, name=cell.name)

		for i, nuc in enumerate(cell.nucs) :
			add_roi(nuc.roi, name='{} nuc {}'.format(cell.name, i))


		for i, nuc in enumerate(cell.nucs) :
			add_roi(nuc.vor_roi, name='{} vor {}'.format(cell.name, i))
		# input()

	add_roi(hseg.cells['vl3'].roi, name='vl3')
	add_roi(hseg.cells['vl4'].roi, name='vl4')

	# for i, nuc in enumerate(hseg.vl3.nucs) :
	# 	add_roi(nuc.roi, name='vl3 nuc{}'.format(i))
	#
	# for i, nuc in enumerate(hseg.vl3.nucs) :
	# 	add_roi(nuc.vor_roi, name='vl3 vor{}'.format(i))
	#
	# for i, nuc in enumerate(hseg.vl4.nucs) :
	# 	if nuc.vor_roi == None :
	# 		print("nuc{}.vor_roi == None".format(i))
	# 	add_roi(nuc.roi, name='vl4 nuc{}'.format(i))
	#
	# for i, nuc in enumerate(hseg.vl4.nucs) :
	# 	if nuc.vor_roi == None :
	# 		print("nuc{}.vor_roi == None".format(i))
	# 	add_roi(nuc.vor_roi, name='vl4 vor{}'.format(i))

	#
	# from java.awt.event import WindowEvent
	# rm.windowActivated(WindowEvent(rm,WindowEvent.WINDOW_ACTIVATED))
