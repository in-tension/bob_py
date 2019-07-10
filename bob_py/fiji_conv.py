
from ij import IJ, WindowManager
from ij.gui import Toolbar
from ij.measure import ResultsTable
from ij.plugin import Duplicator
from ij.plugin.frame import RoiManager
from ij.plugin.filter import Analyzer


""" int to use to set measurements to all"""
MEAS_ALL = 2092799

## need to add close the other images
def force_close_all() :
	while WindowManager.getImageCount() > 0 :
		imp = IJ.getImage()
		imp.changes = False
		imp.close()

def force_close_all_images() :
	while WindowManager.getImageCount() > 0 :
		imp = IJ.getImage()
		imp.changes = False
		imp.close()


def force_close(imp) :
	imp.changes = False
	imp.close()

def add_roi(roi, name=None) :
	rm = RoiManager.getRoiManager()
	rm.addRoi(roi)
	if name is not None :
		rm.rename(rm.getCount() - 1, name)


## obj should be a collection
def jpprint(obj) :
	"""
		pprints java collections as well as python collections
		obj should be a collection
	"""
	for item in obj :
		print(item)


def getMeasurementInt() :
	a = Analyzer()
	i = a.getMeasurements()
	return i


def setMeasurementInt(i) :
	a = Analyzer()
	a.setMeasurements(i)


def swap_ground_colors() :
	cur_fore = Toolbar.getForegroundColor()
	cur_back = Toolbar.getBackgroundColor()

	Toolbar.setForegroundColor(cur_back)
	Toolbar.setBackgroundColor(cur_fore)

def roi_xy(roi) :
	return (roi.getXBase(), roi.getYBase())

def roi_cent(roi, integer=False) :
	stats = roi.getStatistics()
	if integer :
		return (int(stats.xCentroid), int(stats.yCentroid))
	else :
		return (stats.xCentroid, stats.yCentroid)


def rt_to_arr_dict() :
	rt = ResultsTable.getResultsTable()

	headings = rt.getHeadings()

	arr_dict = {}
	for i in range(len(headings)) :
		temp = rt.getColumn(i)
		if temp is not None :
			arr_dict[rt.getColumnHeading(i)] = list(temp)

	return arr_dict


def measure(imp, roi=None, headings=None) :
	setMeasurementInt(MEAS_ALL)

	## possibly don't include roi
	if roi is not None :
		imp.setRoi(roi)

	IJ.run(imp, "Measure", "");

	arr_dict = rt_to_arr_dict()

	if headings is not None :
		return arr_dict
	else :
		out_arr_dict = {}
		for heading in heading :
			## LBYL
			try :
				out_arr_dict[heading] = arr_dict[heading]
			except KeyError :
				IJ.log('fiji_conv.measure() : no heading {}'.format(heading))
		return out_arr_dict



#
# class ImpWithCrop :
#
# 	@staticmethod
# 	def setup_imp_and_roi(imp, roi_to_crop) :
# 		imp_with_crop = ImpWithCrop(imp, roi_to_crop)
# 		offset_roi = OffsetRoi(imp_with_crop, roi_to_crop, main_loc=roi_xy(roi_to_crop))
# 		return imp_with_crop, offset_roi
#
# 	def __init__(self, imp, roi_to_crop) :
# 		self.main_imp = imp
#
# 		self.main_imp.setRoi(roi_to_crop)
#
# 		self.crop_offset = roi_xy(roi_to_crop)
#
# 		d = Duplicator()
# 		self.crop_imp = d.crop(self.main_imp)
# 		self.crop_imp.show()
#
#
#
#
# 	def main_to_crop_loc(self, coords) :
# 		""" convience function for `convert_loc`  so you don't need to know direc -1/1"""
# 		return self.convert_loc(coords, -1)
#
# 	def crop_to_main_loc(self, coords) :
# 		""" convience function for `convert_loc` so you don't need to know direc -1/1"""
#
# 		return self.convert_loc(coords, 1)
#
# 	def convert_loc(self, orig_coords, direc) :
# 		"""
# 			direc = -1 for main_to_crop
# 			direc = 1 for crop_to_main
# 		"""
#
# 		if not (direc == 1 or direc == -1) :
# 			raise ValueError('direc must be 1 or -1')
# 		if len(orig_coords) != 2 :
# 			raise ValueError('orig coords must tuple (or list) of length 2')
#
# 		new_coords = (orig_coords[0] + direc * self.crop_offset[0], orig_coords[1] + direc * self.crop_offset[1])
# 		return new_coords
#
# 	def __str__(self) :
# 		return "fiji_conv.ImpWithCrop: [main_imp={}, crop_imp'{}, crop_offset={}]".format(self.main_imp.getTitle(), self.crop_imp.getTitle(), self.crop_offset)
#
# class OffsetRoi :
#
# 	def __init__(self, imp_with_crop, roi, main_loc=None, crop_loc=None) :
# 		self.roi = roi.clone()
# 		self.imp_with_crop = imp_with_crop
#
#
# 		if main_loc is None and crop_loc is None :
# 			raise ValueError('must pass a value for at least one of main_loc or crop_loc')
#
# 		elif main_loc != None :
# 			self.main_loc = main_loc
# 			self.crop_loc = imp_with_crop.main_to_crop_loc(self.main_loc)
# 		else :
# 			self.crop_loc = crop_loc
# 			self.main_loc = imp_with_crop.crop_to_main_loc(self.crop_loc)
#
#
# 	def set_to_crop(self) :
# 		self.imp_with_crop.crop_imp.setRoi(self.roi)
# 		self.roi.setLocation(*self.crop_loc)
#
# 	def set_to_main(self) :
# 		self.imp_with_crop.main_imp.setRoi(self.roi)
# 		self.roi.setLocation(*self.main_loc)
#
# 	def get_main_roi(self) :
# 		self.set_to_crop()
# 		return self.roi.clone()
#
# 	def get_crop_roi(self) :
# 		self.set_to_main()
# 		return self.roi.clone()
#
# 	def __str__(self) :
# 		return "fiji_conv.OffsetRoi [roi={}, main_loc={}, crop_loc={}".format(self.roi, self.main_loc, self.crop_loc)
