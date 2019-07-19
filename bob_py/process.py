""" """

import os
import csv
import datetime
import imp


from ij import IJ, WindowManager
from ij.measure import ResultsTable
from ij.gui import NonBlockingGenericDialog, Roi, PolygonRoi
from ij.io import DirectoryChooser
from ij.plugin import Duplicator
from ij.plugin.frame import RoiManager


from fiji_utils import *
import brutils as br
imp.reload(br)



IN_DEV = True
DISP = False
# DISP = True



class ProcessExper :
	def __init__(self, input_exper) :
		# self.path = path
		self.name = input_exper.name
		self.input_exper = input_exper

		self.hsegs = {}
		for name, input_hseg in input_exper.hsegs.items() :
			self.hsegs[name] = ProcessHseg(self, input_hseg)


	def get_id(self) :
		return self.name



class ProcessHseg :
	def __init__(self, exper, input_hseg) :
		self.exper = exper
		self.name = input_hseg.name


		self.cells = {}
		for name, input_cell in input_exper.cells.items() :
			self.cells[name] = ProcessCell(self, input_cell)


	def measure_all(self) :
		cell_rois = [cell.roi for cell in self.input_hseg.cells.values()]
		self.cell_geo = measure_roi_set(cell_rois, self.input_hseg.raw_imp, set_measure=MEAS_GEO)

		for cell in self.cells.values() :
			cell.meas_nuc_and_vor(self.input_hseg.nuc_bin_imp)



	def get_id(self) :
		return '_'.join([self.exper.get_id(), self.name])



class ProcessCell :

	def __init__(self, hseg, input_cell) :
		self.hseg = hseg
		self.name = input_cell.name	## str -> vl3 or vl4
		self.input_cell = input_cell

		self.nucs = {}
		for name, input_nuc in input_exper.nucs.items() :
			self.nucs[name] = ProcessNuc(self, input_nuc)


	def meas_nuc_and_vor(self, imp) :
		nuc_roi_set = []
		vor_roi_set = []

		for nuc in self.input_cell.nucs :
			nuc_roi_set.append(nuc.roi)
			vor_roi_set.append(nuc.vor_roi)

		self.nuc_geo = measure_roi_set(nuc_roi_set, imp, set_measure=MEAS_GEO)
		self.vor_geo = measure_roi_set(vor_roi_set, imp, set_measure=MEAS_GEO)



	def get_id(self) :
		return '_'.join([self.hseg.get_id(), self.name])



class ProcessNuc :

	def __init__(self, cell, input_nuc) :
		self.cell = cell
		self.name = input_nuc.name
		self.input_nuc = input_nuc

	def get_id(self) :
		return '_'.join([self.cell.get_id(), self.name])
