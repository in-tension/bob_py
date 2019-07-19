""" """

import os
import csv
import datetime
import imp
import json


from ij import IJ, WindowManager
from ij.measure import ResultsTable
from ij.gui import NonBlockingGenericDialog, Roi, PolygonRoi
from ij.io import DirectoryChooser
from ij.plugin import Duplicator
from ij.plugin.frame import RoiManager


from fiji_utils import *
import brutils as br
imp.reload(br)

# class FijiInstUpdated :
#
# 	def __init__(self, val, date) :
# 		self.val = val
# 		self.date = date
#
#
# 	def __bool__(self) :
# 		if self.val : return True
# 		else : return False
#
# UPDATE1 = FijiInstUpdated(True, datetime.date(2019, 6, 26))


IN_DEV = True
DISP = False
# DISP = True

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

JSON_SUF = '.json'
JSON_SPLIT_CHAR = 'json:'


class InputExper :
	def __init__(self, path, name) :
		self.path = path
		self.name = name


		self.read_json_file()

		self.hsegs = {}
		self.cells = {}
		self.make_hsegs()


	def read_json_file(self) :
		json_file_path = os.path.join(self.path, self.name + JSON_SUF)
		# print(json_file_path)

		if not os.path.exists(json_file_path) :
			IJ.log('no experiment json file for experiment {}\npath:{}'.format(self.name,json_file_path))

		else :
			with open(json_file_path, 'r') as f :
				raw_text = f.read()

			ignore, json_text = raw_text.split(JSON_SPLIT_CHAR)
			self.json = json.loads(json_text)

	@staticmethod
	def setup() :
		"""setup"""
		## set setting to save column headers
		IJ.run("Input/Output...", "jpeg=85 gif=-1 file=.csv use_file save_column");

		## set setting to copy column headers - not actually necessary
		IJ.run("Input/Output...", "jpeg=85 gif=-1 file=.csv copy_column save_column");

		force_close_all_images()
		rm = RoiManager.getRoiManager()
		rm.reset()
		rm.show()


	def make_hsegs(self) :
		"""creates self.hsegs and self.cells"""
		fs = os.listdir(self.path)
		for f in fs :
			if f.startswith(self.name) and os.path.isdir(os.path.join(self.path, f)):
				self.hsegs[f.replace(self.name + '_','')] = InputHseg(self, f)


	def get_id(self) :
		return self.name



class InputHseg :
	def __init__(self, exper, name) :
		self.exper = exper
		self.path = os.path.join(exper.path, name)
		self.name = name.replace(exper.name+'_', '')


		self.raw_imp = None
		self.nuc_bin_imp = None
		self.cells = {}
		self.problem_nucs = None
		self.init_all()


	def init_all(self) :
		"""creates self.raw_imp, self.nuc_bin_imp and self.cells
		make everything for one hemisegment"""

		hs_files = {}
		fs = os.listdir(self.path)
		for f in fs :
			if f.startswith(self.get_id()) :
				suf = f.replace(self.get_id(), '', 1)
				path = os.path.join(self.path,f)
				hs_files[suf] = path


		rm = RoiManager.getRoiManager()
		if RAW_SUF not in hs_files :
			IJ.log('hemisegment {} does not have raw tif file {}'.format(self.name, self.name + RAW_SUF))
			## raise Exception('hemisegment {} does not have raw tif file {}'.format(self.name, self.name + RAW_SUF))
		else :
			self.raw_imp = IJ.openImage(hs_files[RAW_SUF])
			if DISP :
				self.raw_imp.show()
			self.cal = self.raw_imp.getCalibration()


		## todo: Hemiseg as dict cells, currently manually doing keys
		## in future, change csv file suf to _<muscle-name>_cell-roi.csv
		if VL3_SUF not in hs_files :
			IJ.log('hemisegment {} does not have vl3 csv file {}'.format(self.name, self.name + VL3_SUF))
		else :
			vl3 = InputCell(self.exper, self, 'vl3')
			vl3.roi = InputHseg.read_vl_file(hs_files[VL3_SUF], self.cal)
			self.cells['vl3'] = vl3
			# print(self.cells)
			self.exper.cells[vl3.get_id()] = vl3


		if VL4_SUF not in hs_files :
			IJ.log('hemisegment {} does not have vl4 csv file {}'.format(self.name, self.name + VL4_SUF))
		else :
			vl4 = InputCell(self.exper, self, 'vl4')
			vl4.roi = InputHseg.read_vl_file(hs_files[VL4_SUF], self.cal)
			self.cells['vl4'] = vl4
			self.exper.cells[vl4.get_id()] = vl4


		## todo: change to get nuc from raw_imp instead of nuc_bin_imp
		if NUC_BIN_SUF not in hs_files :
			IJ.log('hemisegment {} does not have nuc-bin file {}'.format(self.name, self.name + NUC_BIN_SUF))
		else :
			self.nuc_bin_imp = IJ.openImage(hs_files[NUC_BIN_SUF])
			if DISP :
				self.nuc_bin_imp.show()

			problem_nucs = self.make_nucs()
			if len(problem_nucs) > 0 :
				self.problem_nucs = problem_nucs

			self.make_vor()



		# self.measure_all()
		self.exper.hsegs[self.name] = self

		if DISP :
			self.disp_self()


	@staticmethod
	def read_vl_file(file_path, cal) :
		"""open and xy csv file, uncalibrates the values and creates and returns a polygon roi"""
		roi_csv_headings = ['X', 'Y']

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


	def make_nucs(self) :
		""" """
		rm = RoiManager.getRoiManager()
		rm.reset()

		# if UPDATE1 :
		IJ.run(self.nuc_bin_imp, "Invert", "")

		rt = ResultsTable.getResultsTable()
		rt.reset()
		IJ.run(self.nuc_bin_imp, "Analyze Particles...", "add")

		rois = rm.getRoisAsArray()
		problem_nucs = []
		for roi in rois :
			nuc_cent = roi_cent(roi, integer=True)

			found_cell = False
			for cell in self.cells.values() :
				if cell.roi.contains(*nuc_cent) :
					cell.add_nuc(roi)
					found_cell = True
					break

			if not found_cell :
				IJ.log('Nuc not in any cell for hemisegment {}'.format(self.name))
				problem_nucs.append(roi)

		# print(self.cells['vl3'].nucs)
		return problem_nucs

	#
	# def measure_all(self) :
	# 	cell_rois = [cell.roi for cell in self.cells.values()]
	# 	self.cell_geo = measure_roi_set(cell_rois, self.raw_imp, set_measure=MEAS_GEO)
	#
	# 	for cell in self.cells.values() :
	# 		cell.meas_nuc_and_vor(self.nuc_bin_imp)
	#

	def make_vor(self) :
		"""given hseg, assumed to have cells and nucs"""
		for cell in self.cells.values() :
			cell.make_vor(self.nuc_bin_imp)


	def disp(self) :
		"""display images of self and adds rois of self to RoiManager"""
		if True :
			RoiManager.getRoiManager().reset()

		self.raw_imp.show()
		self.nuc_bin_imp.show()

		for cell in self.cells.values() :
			add_roi(cell.roi, name=cell.name)

			for i, nuc in enumerate(cell.nucs) :
				add_roi(nuc.roi, name='{} nuc {}'.format(cell.name, i))

			for i, nuc in enumerate(cell.nucs) :
				add_roi(nuc.vor_roi, name='{} vor {}'.format(cell.name, i))

		for name, cell in self.cells.items() :
			add_roi(cell.roi, name=name)


	def get_id(self) :
		return '_'.join([self.exper.get_id(), self.name])



class InputCell :

	def __init__(self, exper, hseg, name) :

		self.exper = exper
		self.hseg = hseg
		self.name = name	## str -> vl3 or vl4


		self.nucs = []

		self.roi = None

		self.geo = None

		self.nuc_geo = None
		self.vor_geo = None

		self.nuc_intens = None


	def add_nuc(self, roi) :
		nuc = InputNuc(self, len(self.nucs))
		nuc.roi = roi

		self.nucs.append(nuc)


	def make_vor(self, nuc_bin_imp) :
		"""creates the voronoi for one self, self is assumed to have nucs"""

		vor_rois = self.make_vor_roi(nuc_bin_imp)
		self.match_vor_nuc(vor_rois)


	def make_vor_roi(self, nuc_bin_imp) :

		rm = RoiManager.getRoiManager()
		rm.reset()
		d = Duplicator()
		nuc_bin_copy = d.run(nuc_bin_imp)

		IJ.run(nuc_bin_copy, "Make Binary", "")
		nuc_bin_copy.setRoi(self.roi)
		IJ.run(nuc_bin_copy, "Clear Outside", "")

		IJ.run(nuc_bin_copy, "Voronoi", "")

		nuc_bin_copy.setRoi(None)
		ip = nuc_bin_copy.getProcessor()
		ip.setMinAndMax(0,1)
		IJ.run(nuc_bin_copy, "Apply LUT", "")
		IJ.run(nuc_bin_copy, "Invert", "")

		nuc_bin_copy.setRoi(self.roi)
		IJ.run(nuc_bin_copy, "Analyze Particles...", "add")
		vor_rois = rm.getRoisAsArray()

		force_close(nuc_bin_copy)
		return vor_rois


	def match_vor_nuc(self, vor_rois) :
		rm = RoiManager.getRoiManager()
		nuc_inds = [x for x in range(len(self.nucs))]
		for vor_roi in vor_rois :

			temp = None
			for i, nuc_ind in enumerate(nuc_inds) :
				nuc_roi = self.nucs[nuc_ind].roi

				nuc_cent = roi_cent(nuc_roi, integer=True)

				if vor_roi.contains(*nuc_cent) :
					self.nucs[nuc_ind].vor_roi = vor_roi
					## I don't think I need to do this, I could just use i outside of loop but it feels so insecure or something
					temp = i
					break

			else :
				IJ.log('self: {}, issue with voronoi nuc match up'.format(self.name))
				rm.reset()
				for i, nuc in enumerate(self.nucs) :

					x = int(nuc.roi.getXBase())
					y = int(nuc.roi.getYBase())
					IJ.log('{}. ({},{})'.format(i,x,y))
					add_roi(Roi(x,y,10,10), str(i))
				IJ.log(str(nuc_inds))
				add_roi(vor_roi, "vor_roi")

				## raise RuntimeError('self: {}, issue with voronoi nuc match up'.format(self.name))

			if temp is not None :
				del nuc_inds[temp]

	#
	# def meas_nuc_and_vor(self, imp) :
	# 	nuc_roi_set = []
	# 	vor_roi_set = []
	#
	# 	for nuc in self.nucs :
	# 		nuc_roi_set.append(nuc.roi)
	# 		vor_roi_set.append(nuc.vor_roi)
	#
	# 	self.nuc_geo = measure_roi_set(nuc_roi_set, imp, set_measure=MEAS_GEO)
	# 	self.vor_geo = measure_roi_set(vor_roi_set, imp, set_measure=MEAS_GEO)


	def get_id(self) :
		return '_'.join([self.hseg.get_id(), self.name])



class InputNuc :

	def __init__(self, cell, id_num) :
		self.cell = cell
		self.id_num = id_num
		self.name = 'nuc-' + str(self.id_num)

		self.roi = None

		self.vor_roi = None


	def get_id(self) :
		return '_'.join([self.cell.get_id(), self.name])
