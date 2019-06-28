/*
   BobForPatrick.ijm
   16.1.17

   based on:
	*** Bob_10.ijm ***
	(Created   16.1.17)

	
	Fiji Version 2.0.0-rc-49/1.51e ??

	Image quantification (Drosophila larva, VL3 & VL4)

	"_Fib" image type was changed to "_EU" to process EU pictures instead
*/

var x_glob = newArray(); 
var y_glob = newArray();
var error = false;
var hemisegs_txt = "";
var headings = "";

// flags to capture heading the first time
// associated data is processed

var results_flag = false;

var Cell_flag = false;
var Nuc_flag = false;
var Nnd_flag = false;
var Voronoi_flag = false;

var Hoe_flag = false;
var Fib_flag = false;
var Fib_bin_flag = false;
var H3K9ac_flag = false;
var H4K16ac_flag = false;
var HP1_flag = false;
var HP1_bin_flag = false;

// capture headings separately so they can be written
// out in the desired order

var Cell_heading = "";
var Nuc_heading = "";
var Nnd_heading = "";
var Voronoi_heading = "";

var Hoe_heading = "";
var Fib_heading = "";
var Fib_bin_heading = "";
var H3K9ac_heading = "";
var H4K16ac_heading = "";
var HP1_heading = "";
var HP1_bin_heading = "";

var VL_labels = newArray ("_VL3", "_VL4");
var VL_names = newArray ("VL3", "VL4");
var XY_labels = newArray ("_XY-VL3.csv", "_XY-VL4.csv");

// per-Cell data, duplicated over Nuclei
var Cell_label = "";
var Cell_data = "";

// number of rows equals number of Nuclei in Cell
var Nuc_data = newArray();
var Nnd_data = newArray();
var Voronoi_data = newArray();

// we need to save per-image image data (potentially blank-Cell data)
// as we go along because we won't know until the end what image types
// we have seen

var Hoe = "_Hoe";
var Fib = "_EU";
var Fib_bin = "_Fib-bin";
var H3K9ac = "_H3K9ac";
var H4K16ac = "_H4K16ac";
var HP1 = "_HP1";
var HP1_bin = "_HP1-bin";

var possible_images = newArray (Hoe, Fib, Fib_bin, H3K9ac, H4K16ac, HP1, HP1_bin);
var n_image_types = possible_images.length;
var b_image_type = newArray (n_image_types);

for (i = 0; i < n_image_types; i++)  b_image_type[i] = false;

// can't have 2-d arrays
var     Hoe_data = newArray();
var     Fib_data = newArray();
var Fib_bin_data = newArray();
var  H3K9ac_data = newArray();
var H4K16ac_data = newArray();
var     HP1_data = newArray();
var HP1_bin_data = newArray();

// for blank-Cell image data
var n_image_fields = 18;
var blank_Cell_image_row = "";
for (i = 0; i < n_image_fields - 1; i++)  blank_Cell_image_row += ",";

// used to build image_data
var per_image_data = newArray();

// each row is constructed by concatinating per-image rows together
var image_data = newArray();

// first collect rows Cell, Nuc, etc. data,
// then add columns for all Cells for those image types seen
var results_data = newArray();


macro "Bob" {
        waitForUser ("Bob says …", "Hi, friend!");
	// *** <Set Up> ***
		list = getList("window.titles"); 
		for (n = 0; n < list.length; n++) { 
		    winame = list[n]; 
		    selectWindow(winame); 
			run("Close"); 
		} 
		while (nImages>0) { 
			selectImage(nImages); 
			close(); 
		} 
	// *** </Set Up> ***

	
	// *** <Variables> ***
		all = "area mean standard modal min centroid center perimeter bounding fit shape feret's integrated median skewness kurtosis area_fraction stack display redirect=None decimal=5";
		rois ="area  centroid  perimeter bounding fit shape stack redirect=None decimal=5";
		over_image ="mean standard modal min center feret's integrated median skewness kurtosis area_fraction redirect=None decimal=5";
		
		Nuc_bin = "_Nuc-bin.tif";
		Nuc_save = "_Nuc.csv";
		XY_VL3 = "_XY-VL3.csv";
		XY_VL4 = "_XY-VL4.csv";
		VL3 = "_VL3";
		VL4 = "_VL4";
		
		required_files = newArray(Nuc_bin, XY_VL3, XY_VL4);

		sl = File.separator; 	// "\" or "/" based on os
		Cell_csv = "_Cell.csv";
		hs_txt = "hemisegs.txt";
		heading_csv = "headings.csv";
		Nnd_save = "_Nnd.csv";
		Voronoi_save = "_Voronoi.csv";
		tif = ".tif";
		csv = ".csv";
		results_csv = "big_bob.csv";
		results_csv_new = "bob_results_new.csv";
	
		spreadsheets_no_sl = "Spreadsheets";
		spreadsheets = spreadsheets_no_sl + sl;
				
		h_dir = getDirectory("Select Head Folder");
                toks = split (h_dir, sl);
                h_dir_name = toks[toks.length - 1];
                results_csv_new = h_dir_name + "_" + results_csv_new;
		s_dir = make_s_dir();
		delete_results_csv();  // delete old combined-results spreadsheet
		delete_results_csv_new();  // delete old combined-results spreadsheet (new)
		save_results_headings();  // just Cell / Nucleus headings for now
		hs_list = get_hs_list();
	// *** </Variables> ***


	// *** <Actually Does Shits> ***
		for (a = 0; a < hs_list.length; a++)  collect_hs_data (hs_list[a]);
		File.saveString(headings, s_dir + heading_csv)
                // add image data for image types seen
                for (i = 0; i < n_image_types; i++) {
                  if (!b_image_type[i])  continue;
                  // (more readable than just switching on i)
                  if (possible_images[i] ==     Hoe)  concat_rows (results_data,     Hoe_data, ",,");
                  if (possible_images[i] ==     Fib)  concat_rows (results_data,     Fib_data, ",,");
                  if (possible_images[i] == Fib_bin)  concat_rows (results_data, Fib_bin_data, ",,");
                  if (possible_images[i] ==  H3K9ac)  concat_rows (results_data,  H3K9ac_data, ",,");
                  if (possible_images[i] == H4K16ac)  concat_rows (results_data, H4K16ac_data, ",,");
                  if (possible_images[i] ==     HP1)  concat_rows (results_data,     HP1_data, ",,");
                  if (possible_images[i] == HP1_bin)  concat_rows (results_data, HP1_bin_data, ",,");
                }
                save_results_headings_new();
                save_results_new();
                
	// *** </Actually Does Shits> ***

		
	File.saveString(hemisegs_txt, s_dir + hs_txt)
	selectWindow("Results");
	run("Close");
	selectWindow("ROI Manager");
	run("Close");
}


function collect_hs_data (hemiseg) {
        // save "Results" column labels first time through
	if (!results_flag)  run("Input/Output...", "jpeg=85 gif=-1 file=.csv use_file save_column");
	hs_dir = h_dir + hemiseg + sl;
	has_v_coords = newArray (false, false);
	hs_images = check_files(hs_dir, hemiseg, has_v_coords);
	if (!error) {
		for (n = 0; n < hs_images.length; n++) {
			open (hs_dir + hemiseg + hs_images[n] + tif);
		}
		open(hs_dir + hemiseg + Nuc_bin);

		// loop over VL3 and VL4 Cells
                for (i_v = 0; i_v < 2; i_v++) {
                        if (!has_v_coords[i_v])  continue;
                	roiManager("reset");

                        Cell_label_old = hemiseg + VL_labels[i_v];
                        parsed_label = parse_sample_name (hemiseg);
                        Cell_label = "";
                        for (i = 0; i < parsed_label.length; i++) {
                            if (i != 0)  Cell_label += ",";
                            Cell_label += parsed_label[i];
                        }
                        Cell_label += "," + VL_names[i_v];
			open_coords(hs_dir, hemiseg + XY_labels[i_v], VL_labels[i_v]);

			roiManager("select", 0);
			run("Set Measurements...", all);
			roiManager("measure");

                        // Cell_data will be repeated for each Nucleus in the Cell
                        data = get_data(1);
                        Cell_data = "";
                        if (data.length != 1)  print ("Big problemo!");
                        else  Cell_data = data[0];
			saveAs("Results", s_dir + hemiseg + VL_labels[i_v] + Cell_csv);
			get_headings_new ("Cell");
			get_headings("Cell");
			run("Clear Results");  

			create_Nuc(hemiseg, VL_labels[i_v]);
                        n_Nuclei = Nuc_data.length;   // for blank-Cell image data
								
			get_centroids();
			x_centroids = Array.copy(x_glob);
			y_centroids = Array.copy(y_glob);

                        // process image if it exists for this sample,
                        // otherwise accumulate blank-Cell data.
                        // logic assumes that hs_images is a (properly ordered)
                        // subsequence of possible_images.
                        ni = 0;
			for (n = 0; n < n_image_types; n++) {
                            has_image = ni < hs_images.length;  // no short-circuit &&
                            if (has_image)  has_image = has_image && possible_images[n] == hs_images[ni];
                            if (has_image) {
				Nuc_over_image (hemiseg, hs_images[ni], VL_labels[i_v]);
                                image_data = concat_rows (image_data, per_image_data, ",");
                                b_image_type[n] = true;
                                ni++;
                             }
                             else {  // we don't have this image type for this sample
                                  // load blank-Cell data
                                  per_image_data = newArray(n_Nuclei);
                                  for (i = 0; i < n_Nuclei; i++)  per_image_data[i] = blank_Cell_image_row;
                             }
                             // add data to correct image_type data array
                             // (more readable than just switching on n)
                             if (possible_images[n] == Hoe) {
                               if (Hoe_data.length != 0)  Hoe_data = Array.concat (Hoe_data, newArray (""));
                               Hoe_data = Array.concat (Hoe_data, per_image_data);
                             }
                             if (possible_images[n] ==     Fib) {
                               if (Fib_data.length     != 0)  Fib_data     = Array.concat (Fib_data,     newArray (""));
                               Fib_data     = Array.concat (Fib_data,     per_image_data);
                             }
                             if (possible_images[n] == Fib_bin) {
                               if (Fib_bin_data.length != 0)  Fib_bin_data = Array.concat (Fib_bin_data, newArray (""));
                               Fib_bin_data = Array.concat (Fib_bin_data, per_image_data);
                             }
                             if (possible_images[n] ==  H3K9ac) {
                               if (H3K9ac_data.length  != 0)  H3K9ac_data  = Array.concat (H3K9ac_data,  newArray (""));
                               H3K9ac_data  = Array.concat (H3K9ac_data,  per_image_data);
                             }
                             if (possible_images[n] == H4K16ac) {
                               if (H4K16ac_data.length != 0)  H4K16ac_data = Array.concat (H4K16ac_data, newArray (""));
                               H4K16ac_data = Array.concat (H4K16ac_data, per_image_data);
                             }
                             if (possible_images[n] ==     HP1) {
                               if (HP1_data.length     != 0)  HP1_data     = Array.concat (HP1_data,     newArray (""));
                               HP1_data     = Array.concat (HP1_data,     per_image_data);
                             }
                             if (possible_images[n] == HP1_bin) {
                               if (HP1_bin_data.length != 0)  HP1_bin_data = Array.concat (HP1_bin_data, newArray (""));
                               HP1_bin_data = Array.concat (HP1_bin_data, per_image_data);
                             }
                        }

			delete_Nuc();

			
			Voronoi (hemiseg + VL_labels[i_v] + Voronoi_save, x_centroids, y_centroids);

                        // write data to combined spreadsheet and clear arrays
                        save_Cell_results();
                        // accumulate data in results_data
                        append_Cell_results();
                        clear_data_arrays();
                }

		close (hemiseg + Nuc_bin);
		for (n = 0; n < hs_images.length; n++) {
			close (hemiseg + hs_images[n] + tif);
		}

	}
        // don't save "Results" column labels on subsequent iterations
	if (!results_flag) {
          run("Input/Output...", "jpeg=85 gif=-1 file=.csv use_file");
          results_flag = true;
        }
}


function make_s_dir () {
	if (!(File.exists(h_dir + spreadsheets))) {
		File.makeDirectory(h_dir + spreadsheets)
	}
	s_dir = h_dir + spreadsheets;
	return s_dir;
}

// delete the old combined-results spreadsheet if it exists
function delete_results_csv() {
	if (File.exists(s_dir + results_csv))  File.delete (s_dir + results_csv);
}

// delete the old new-version combined-results spreadsheet if it exists
function delete_results_csv_new() {
	if (File.exists(h_dir + results_csv_new))  File.delete (h_dir + results_csv_new);
}

function get_hs_list() {
	txt = "";
	h_dir_contents = getFileList(h_dir);
	hemisegs = newArray();
	for (n = 0; n < h_dir_contents.length; n++) {
		if (endsWith(h_dir_contents[n], "/")) {
			if (!startsWith(h_dir_contents[n], spreadsheets_no_sl)) {
				k = lengthOf(h_dir_contents[n]) - 1; 
				temp = substring(h_dir_contents[n], 0, k);
				hemisegs = Array.concat(hemisegs, temp);
			}
		}
	}
	return hemisegs;
}


function check_files (hs_dir, hemiseg, has_v_coords) {
        error = false;
        has_Nuc_bin = false;
        has_v_coords[0] = false;
        has_v_coords[1] = false;
	hs_files = newArray();
	for (n = 0; n < required_files.length; n++) {
		if (File.exists(hs_dir + hemiseg + required_files[n])) {
			if (n == 0)  has_Nuc_bin = true;
			else         has_v_coords[n - 1] = true;
		}
		else	print ("missing file in " + sl + hemiseg + ": " + hemiseg + required_files[n]);
	}
	if (!has_Nuc_bin)  error = true;
	if (!has_v_coords[0]  &&  !has_v_coords[1]) {
	   error = true;
	   print ("missing both XY coordinate files in " + sl + hemiseg + ": " + required_files[1] + ", " + required_files[2]);
	}

	hemisegs_txt = hemisegs_txt + hemiseg + "{\n";
	for (m = 0; m < possible_images.length; m++) {
		if (File.exists(hs_dir + hemiseg + possible_images[m] + tif)) {
			hs_files = Array.concat(hs_files, possible_images[m]);
			hemisegs_txt = hemisegs_txt + possible_images[m] + "\n";
		}
	}
	hemisegs_txt = hemisegs_txt + "}\n";
	if (error) {
		print("\tCan't compute " + hemiseg + " due to missing files");
	}
	return hs_files;
}


function open_coords (hs_dir, file, name) {
	//print("got this far");
	x = newArray(); 
	y = newArray();
	coords = File.openAsString(hs_dir + file);
	lines = split(coords,"\n"); 	// lines = array of strings
	
	for (n = 1; n < lines.length; n++) {
		XY = split(lines[n], ","); // XY = array of two strings
		x = Array.concat(x, XY[0]);
		y = Array.concat(y, XY[1]);
	}
	toUnscaled(x,y);	

	makeSelection("freehand", x, y); 

	roiManager("Add");
	roiManager("Select", 0);
	roiManager("rename", name);
}


function create_Nuc (hemiseg, VL) {
	roiManager("Select", 0);
	run("Set Measurements...", rois);
	run("Analyze Particles...", "display add");

	Nnd(hemiseg + VL + Nnd_save);
        Nuc_data = get_data(0);
	saveAs("Results", s_dir + hemiseg + VL + Nuc_save);

	get_headings_new ("Nuc");
	get_headings("Nuc");
	run("Clear Results"); 
	run("Set Measurements...", over_image);
}


function get_centroids () {	
	x_list = newArray();
	y_list = newArray();
	for (n = 0; n < nResults; n++) {
		x = getResult("X", n);
		y = getResult("Y", n);
		toUnscaled(x,y);
		
		x_list = Array.concat(x_list, x);
		y_list = Array.concat(y_list, y);
	}
	x_glob = Array.copy(x_list);
	y_glob = Array.copy(y_list);	
}


function Nuc_over_image (hemiseg, image, VL) {
		selectWindow(hemiseg + image +  tif);		
		select_Nuc();

		roiManager ("measure");
                per_image_data = get_data(0);
		saveAs("Results", s_dir + hemiseg + VL + image + csv);

		get_headings_new (image);
		get_headings(image);
		run("Clear Results"); 
}


function select_Nuc () {
	a = Array.getSequence(roiManager("count"));
	b = Array.slice(a, 1, a.length);
	roiManager("Select", b);
}


function delete_Nuc () {
	a = Array.getSequence(roiManager("count"));
	b = Array.slice(a, 1, a.length);
	roiManager("Select", b);
	roiManager("delete");
}


function Nnd (file) {
	//IJ.log("nnd");
	selectWindow(hemiseg + Nuc_bin);		
	select_Nuc();
	run("Nnd ");

	selectWindow("Nearest Neighbor Distances");
        Nnd_data = get_Nnd_data();
	saveAs("Results", s_dir + file);
	get_headings_new ("Nnd");
	get_headings("Nnd");
	run("Close");
}


function Voronoi (file, x, y) {	
	//IJ.log("vor");
	run("Set Measurements...", all);
	selectWindow(hemiseg + Nuc_bin);		

	// *** <Create Voronoi> ***
		roiManager("Select", 0);
                run ("Make Inverse");
		setForegroundColor(255, 255, 255);
		run("Fill", "slice");

		run("Voronoi");
	
		run("Select None");
		setMinAndMax(0,1);
		run("Apply LUT");
		run("Invert");

		roiManager("Select", 0);
		run("Analyze Particles...", "add");
	// *** </Create Voronoi> ***


	// *** <Re-order and Save> ***
		v_order(x, y);
	
		a = Array.getSequence(roiManager("count") - 1);
		roiManager("Select", a);
		run("Revert");
		roiManager("measure");
                Voronoi_data = get_data(1);
		saveAs("Results", s_dir + file);
		get_headings_new ("Voronoi");
		get_headings("Voronoi");

	// *** <Clean-up> ***
		run("Clear Results"); 
	
		a = Array.getSequence(roiManager("count"));
		b = Array.slice(a, 0, a.length - 1);
		roiManager("Select", b);
		roiManager("delete");
	// *** <Clean-up> ***	
}


function v_order (x, y) {
	for (n = 1; n < roiManager("count"); n++) {
		roiManager("select", n);
		for (m = 0; m < x.length; m++) {
			if (Roi.contains(x[m], y[m])) {
				x = arr_del(x, m);
				y = arr_del(y, m);
				roiManager("rename", m);
				m = x.length;
			}
		}	
	}	
	roiManager("sort");
}


function arr_del (arr, m) {
	a = Array.slice(arr, 0, m);
	b = Array.slice(arr, m + 1, arr.length - m - 1);
	c = Array.concat(a, b);
	return c;
}

// new version to capture section headings into separate strings
// implements any section-specific logic
// (flags will be set by subsequent call to get_headings)
function get_headings_new (section_name) {
        // test if we already have this section's heading
        if (section_name == "Cell") {
           if (Cell_flag)  return;
           Cell_heading = get_headings_string (section_name, 1);
           // Cell_flag = true;
        }
        if (section_name == "Nuc") {
           if (Nuc_flag)  return;
           Nuc_heading = get_headings_string (section_name, 0);
           // Nuc_flag = true;
        }
        if (section_name == "Nnd") {
           if (Nnd_flag)  return;
           Nnd_heading = "NND";
           // Nnd_flag = true;
        }
        if (section_name == "Voronoi") {
           if (Voronoi_flag)  return;
           Voronoi_heading = get_headings_string (section_name, 1);
           // Voronoi_flag = true;
        }
        if (section_name == Hoe) {
           if (Hoe_flag)  return;
           s_name = substring (section_name, 1);
           Hoe_heading = get_headings_string (s_name, 0);
           // Hoe_flag = true;
        }
        if (section_name == Fib) {
           if (Fib_flag)  return;
           s_name = substring (section_name, 1);
           Fib_heading = get_headings_string (s_name, 0);
           // Fib_flag = true;
        }
        if (section_name == Fib_bin) {
           if (Fib_bin_flag)  return;
           s_name = substring (section_name, 1);
           Fib_bin_heading = get_headings_string (s_name, 0);
           // Fib_bin_flag = true;
        }
        if (section_name == H3K9ac) {
           if (H3K9ac_flag)  return;
           s_name = substring (section_name, 1);
           H3K9ac_heading = get_headings_string (s_name, 0);
           // H3K9ac_flag = true;
        }
        if (section_name == H4K16ac) {
           if (H4K16ac_flag)  return;
           s_name = substring (section_name, 1);
           H4K16ac_heading = get_headings_string (s_name, 0);
           // H4K16ac_flag = true;
        }
        if (section_name == HP1) {
           if (HP1_flag)  return;
           s_name = substring (section_name, 1);
           HP1_heading = get_headings_string (s_name, 0);
           // HP1_flag = true;
        }
        if (section_name == HP1_bin) {
           if (HP1_bin_flag)  return;
           s_name = substring (section_name, 1);
           HP1_bin_heading = get_headings_string (s_name, 0);
           // HP1_bin_flag = true;
        }

}

// healper function for get_headings_new
// skip first n_skip columns
function get_headings_string (section_name, n_skip) {
	toks = split (String.getResultsHeadings);
        h_string = "";
	for (n = n_skip; n < toks.length; n++) {
                if (n > n_skip)  h_string += ",";
		h_string = h_string + toks[n] + "-" + section_name;
	}
        return h_string;
}

function get_headings (section_name) {
        // test if we already have this section's heading
        if (section_name == "Cell") {
           if (Cell_flag)  return;
           Cell_flag = true;
        }
        if (section_name == "Nuc") {
           if (Nuc_flag)  return;
           Nuc_flag = true;
        }
        if (section_name == "Nnd") {
           if (Nnd_flag)  return;
           Nnd_flag = true;
        }
        if (section_name == "Voronoi") {
           if (Voronoi_flag)  return;
           Voronoi_flag = true;
        }
        if (section_name == Hoe) {
           if (Hoe_flag)  return;
           Hoe_flag = true;
        }
        if (section_name == Fib) {
           if (Fib_flag)  return;
           Fib_flag = true;
        }
        if (section_name == Fib_bin) {
           if (Fib_bin_flag)  return;
           Fib_bin_flag = true;
        }
        if (section_name == H3K9ac) {
           if (H3K9ac_flag)  return;
           H3K9ac_flag = true;
        }
        if (section_name == H4K16ac) {
           if (H4K16ac_flag)  return;
           H4K16ac_flag = true;
        }
        if (section_name == HP1) {
           if (HP1_flag)  return;
           HP1_flag = true;
        }
        if (section_name == HP1_bin) {
           if (HP1_bin_flag)  return;
           HP1_bin_flag = true;
        }


	temp = split(String.getResultsHeadings);
	for (n = 0; n < temp.length; n++) {
		headings = headings + temp[n] + "-" + section_name + ",";
	}
	headings = headings + ",";
}

// return data from results table as an array of rows, each
// row a comma-separated list (string) of column values
// skip the first n_skip columns
function get_data(n_skip) {
        data = newArray();
        if (nResults == 0)  return data;
        columns = split (String.getResultsHeadings);
        for (r = 0; r < nResults; r++) {
            row = "";
            // skip n_skip column
            for (j = n_skip; j < columns.length; j++) {
                res = getResult (columns[j], r);
                // print out integers without trailing zeros
                if (floor (res) == res)  ndec = 0;
                else                     ndec = 5;
                if (j > n_skip)  row += ",";
                row += d2s (res, ndec);
            }
            data = Array.concat (data, row);
        }
        return data;
}

// special function to get data from the "Nearest Neighbor Distances"
// data window.  assumes that this window has been selected
function get_Nnd_data() {
        data = newArray();
        rows = split (getInfo("window.contents"), "\n");
        for (i = 1; i < rows.length; i++) {          // skip header row
            fields = split (rows[i]);
            data = Array.concat (data, fields[1]);   // skip label column
        }
        return data;
}

// append partial csv rows to growing rows
// (to build image_data from per_image_data)
function concat_rows (whole_rows, partial_rows, sep) {
         if (whole_rows.length == 0)  whole_rows = Array.copy (partial_rows);
         else {
              if (whole_rows.length != partial_rows.length)  print ("Big Problemo!");
              else {
                   for (i = 0; i < whole_rows.length; i++) {
                       // whole_rows[i] += sep + partial_rows[i];
                       // "+=" fails sometimes
                       if (lengthOf (whole_rows[i]) == 0  &&  lengthOf (partial_rows[i]) == 0) {
                            appended_row = "";
                       }
                       else {
                            appended_row = whole_rows[i] + sep + partial_rows[i];
                       }
                       whole_rows[i] = appended_row;
                   }
              }
         }
         return whole_rows;
}

// write out experiment info and column headings -- temporary version
function save_results_headings() {
	File.append ("sample,larva,side,segment,Cell,,Nucleus", s_dir + results_csv);
}

// append result rows for one Cell to combined spreadsheet
function save_Cell_results() {
         for (i = 0; i < Nuc_data.length; i++) {
             // i + 1 is the "Nucleus number" within the Cell
             row  =          "\n";   // separate Cell sections with a blank row
             row +=          Cell_label;
             row += ",,"  +  (i + 1);
             row += ",,"  +  Cell_data;
             row += ",,"  +  Nuc_data[i];
             row +=  ","  +  Nnd_data[i];
             //IJ.log(Voronoi_data.length);
             //row += ",,"  +  Voronoi_data[i];
             File.append (row, s_dir + results_csv);  // File.append adds new line
         }
}

function append_Cell_results() {
  // Cells separated by empty rows
  if (results_data.length != 0)  results_data = Array.concat (results_data, newArray (""));
  data = newArray (Nuc_data.length);
  for (i = 0; i < Nuc_data.length; i++) {
    // i + 1 is the "Nucleus number" within the Cell
    row  =          "";
    row +=          Cell_label;
    row += ",,"  +  (i + 1);
    row += ",,"  +  Cell_data;
    row += ",,"  +  Nuc_data[i];
    row +=  ","  +  Nnd_data[i];
    //row += ",,"  +  Voronoi_data[i];
    data[i] = row;
   }
  results_data = Array.concat (results_data, data);
}

// write out experiment info and column headings -- new (temporary) version
function save_results_headings_new() {
        sample_heading = "sample,larva,side,segment,Cell,,Nucleus";
        heading = sample_heading;
        heading += ",," + Cell_heading;
        heading += ",," + Nuc_heading;
        heading +=  "," + Nnd_heading;
        //heading += ",," + Voronoi_heading;
        for (i = 0; i < n_image_types; i++) {
            if (!b_image_type[i])  continue;
            // (more readable than just switching on i)
            if (possible_images[i] ==     Hoe)  heading += ",," +     Hoe_heading;
            if (possible_images[i] ==     Fib)  heading += ",," +     Fib_heading;
            if (possible_images[i] == Fib_bin)  heading += ",," + Fib_bin_heading;
            if (possible_images[i] ==  H3K9ac)  heading += ",," +  H3K9ac_heading;
            if (possible_images[i] == H4K16ac)  heading += ",," + H4K16ac_heading;
            if (possible_images[i] ==     HP1)  heading += ",," +     HP1_heading;
            if (possible_images[i] == HP1_bin)  heading += ",," + HP1_bin_heading;
        }
	File.append (heading + "\n", h_dir + results_csv_new);
}

// save combined-data array to new-version combined spreadsheet
function save_results_new() {
         for (i = 0; i < results_data.length; i++) {
             File.append (results_data[i], h_dir + results_csv_new);  // File.append adds new line
         }
}


// clear global combined-spreadsheet data arrays
function clear_data_arrays() {
         Cell_data = "";
         Nuc_data = newArray();
         Nnd_data = newArray();
         Voronoi_data = newArray();
         per_image_data = newArray();
         image_data = newArray();
}

// parse the name of the sample directory into
// sample, larva number, side, segment
// assumes format <sample>_L<larva number>-<side><segment>
function parse_sample_name (dir_name) {
         // defaults for failed parse
         sample = dir_name;
         larva = "?";
         side = "?";
         segment = "?";
         def = newArray (sample, larva, side, segment);

         toks = split (dir_name, "_");
         if (toks.length < 2)  return def;

         lseg = toks[toks.length - 1];
         sample = substring (dir_name, 0, lengthOf (dir_name) - (lengthOf (lseg) + 1));

         toks = split (lseg, "-");
         if (toks.length != 2)  return def;

         if (toks.length < 2  ||  !startsWith (toks[0], "L"))  return def;
         larva = substring (toks[0], 1);
         if (isNaN (parseInt (larva)))  return def;

         if (lengthOf (toks[1]) != 2)  return def;
         side = substring (toks[1], 0, 1);
         if (side != "L"  &&  side != "R")  return def;
         segment = substring (toks[1], 1);
         if (isNaN (parseInt (segment)))  return def;


         return newArray (sample, larva, side, segment);
}

function pause_i (message, i) {
	do_pause = getBoolean(message + ", " + i);
	if (do_pause) {
		waitForUser(message + ", " + i);
	}
}


function pause (message) {
	do_pause = getBoolean(message);
	if (do_pause) {
		waitForUser(message);
	}
}
