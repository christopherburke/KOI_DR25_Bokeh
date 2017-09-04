# -*- coding: utf-8 -*-
"""
Created on Tue Aug 29 11:39:06 2017

@author: Christopher J Burke
Example from Dennis Obrien was very helpful for filtering table with CustomJS
https://gist.github.com/dennisobrien/450d7da20daaba6d39d0
Switch data on figure was aided by
https://stackoverflow.com/questions/38038432/bokeh-interactively-changing-the-columns-being-plotted
Things Wanting
-Z dimension as color shading
-multiselect for columns to display
-Save current table to file

"""

from bokeh.models import ColumnDataSource, CustomJS, HoverTool, TapTool, OpenURL
from bokeh.models.widgets import DataTable, TableColumn, NumberFormatter, CheckboxGroup, TextInput, Select
from bokeh.io import output_file, show
from bokeh.layouts import layout, Column
from bokeh.plotting import figure
from bokeh.models.tools import BoxZoomTool, PanTool, ResetTool, SaveTool, ZoomInTool, ZoomOutTool
import numpy as np
import urllib
import urllib2

def get_DR25_KOI_Data():
    # query NEXSCI for the DR25 planet candidate catalog and then filter members
    #  to a target list that is read in
    whereString = "koi_pdisposition like 'CANDIDATE'"
    url = 'https://exoplanetarchive.ipac.caltech.edu/cgi-bin/nstedAPI/nph-nstedAPI?'
    data = {'table':'q1_q17_dr25_koi', \
            'select':'kepid,kepoi_name,koi_score,koi_period,koi_time0bk,koi_duration,koi_prad,koi_depth,koi_teq,koi_insol,koi_dor,koi_steff,koi_slogg,koi_srad,koi_kepmag,koi_tce_plnt_num', \
            'format':'csv', \
            'where':whereString}
    url_values = urllib.urlencode(data)
    #print url_values
    queryData = urllib2.urlopen(url + url_values)
    returnPage = queryData.read()
    dtypeseq = ['i4','S20']
    dtypeseq.extend(['f8'] * 14)
    curBlock = np.genfromtxt(returnPage.splitlines(), delimiter=',', skip_header=1, \
                        dtype=dtypeseq)
    kepid = curBlock['f0']
    koiname = curBlock['f1']
    koi_score = curBlock['f2']
    koi_period = curBlock['f3']
    koi_time0bk = curBlock['f4']
    koi_duration = curBlock['f5']
    koi_prad = curBlock['f6']
    koi_depth = curBlock['f7']
    koi_teq = curBlock['f8']
    koi_insol = curBlock['f9']
    koi_dor = curBlock['f10']
    koi_steff = curBlock['f11']
    koi_slogg = curBlock['f12']
    koi_srad = curBlock['f13']
    koi_kepmag = curBlock['f14']
    koi_pn = np.int8(curBlock['f15'])
    # Trim off leading K in koi string and convert to float 
    koi_number = np.array([float(xstr[1:]) for xstr in koiname])
    
    print "Tot # PCs: {0:d}".format(len(kepid))
    # Convert all the data columns into a python dictionary
    koi_dict = {}
    koi_dict['kepid'] = kepid.tolist()
    koi_dict['koi_number'] = koi_number.tolist()
    koi_dict['koi_score'] = koi_score.tolist()
    koi_dict['koi_period'] = koi_period.tolist()
    koi_dict['koi_time0bk'] = koi_time0bk.tolist()
    koi_dict['koi_duration'] = koi_duration.tolist()
    koi_dict['koi_prad'] = koi_prad.tolist()
    koi_dict['koi_depth'] = koi_depth.tolist()
    koi_dict['koi_teq'] = koi_teq.tolist()
    koi_dict['koi_insol'] = koi_insol.tolist()
    koi_dict['koi_dor'] = koi_dor.tolist()
    koi_dict['koi_steff'] = koi_steff.tolist()
    koi_dict['koi_slogg'] = koi_slogg.tolist()
    koi_dict['koi_srad'] = koi_srad.tolist()
    koi_dict['koi_kepmag'] = koi_kepmag.tolist()


    # Add columns for figure only that are log versions of some
    logColumns = ["koi_period", "koi_depth", "koi_prad", "koi_teq", "koi_insol", \
                "koi_srad", "koi_dor"]
    # Add Log columns to dataset
    for colwant in logColumns:
        currentColumn = np.array(koi_dict[colwant])
        idx = np.where(np.logical_not(np.isfinite(currentColumn)))[0]
        medianValue = np.nanmedian(currentColumn)
        currentColumn[idx] = medianValue
        
        # Correct negative values to median
        idx = np.where(currentColumn <= 0.0)[0]
        currentColumn[idx] = medianValue
        currentColumn = np.log10(currentColumn)
        koi_dict["Log" + colwant] = currentColumn.tolist()

    # Build the URL for the DV summary hosted at the exoplanet archive
    #https://exoplanetarchive.ipac.caltech.edu/data/KeplerData/011/011656/011656840/dv/kplr011656840-001-20160209194854_dvs.pdf
    urlPrefix = "https://exoplanetarchive.ipac.caltech.edu/data/KeplerData/"
    urlPart1 = "/dv/kplr"
    urlPart2 = "-20160209194854_dvs.pdf"
    urlList = []
    kicList = koi_dict['kepid']
    for i,kic in enumerate(kicList):
        kicstr = "{0:09d}".format(kic)
        kicp1 = kicstr[0:3] + '/'
        kicp2 = kicstr[0:6] + '/'
        kicp3 = kicstr + '-'
        kicp4 = "{0:03d}".format(koi_pn[i])
        urlList.append(urlPrefix + kicp1 + kicp2 + kicstr + urlPart1 + kicp3 + kicp4 + urlPart2)
        
    koi_dict['koi_url'] = urlList

    return koi_dict

if  __name__ == "__main__":

    outputFile = 'koiDR25_BokehInteract.html'    
    # Build dictionary of DR25 KOI PC catalog information
    koi_dict = get_DR25_KOI_Data()
    # Designate columns available for figure and their labels
    figure_data_dict = {'koi_period':['Period [day]'], 'Logkoi_period':['Log Period [day]'], \
            'koi_depth':['Depth [ppm]'], 'Logkoi_depth':['Log Depth [ppm]'], \
            'koi_prad':['Planet Radius [Rearth]'], 'Logkoi_prad':['Log Planet Radius [Rearth]'], \
            'koi_teq':['Planet Teq [K]'], 'Logkoi_teq':['Log Planet Teq [K]'], \
            'koi_kepmag':['KpMag'], \
            'koi_srad':['Stellar Radius [Rsun]'], 'Logkoi_srad':['Log Stellar Radius [Rsun]'], \
            'koi_steff':['Stellar Teff [K]'], 'koi_slogg':['Stellar Logg [cgs]'], \
            'koi_score':['Disp. Score'], \
            'koi_insol':['Insol Flux'], 'Logkoi_insol':['Log Insol Flux'], \
            'koi_dor':['a/rstar'], 'Logkoi_dor':['Log a/rstar']}
    
    # source data for table consists of the full orinal table and the filtered table        
    source = ColumnDataSource(koi_dict)
    original_source = ColumnDataSource(koi_dict)
    
    # This is a helper datatable that will help convert from dictionary key names (e.g. koi_period)
    #    to the displayed name (e.g. Period [day]) for figure menu and axis labels
    axis_label_source = ColumnDataSource(figure_data_dict)
    
    # Here are the data columns that will show up in the table
    columns = [
        TableColumn(field="koi_number", title="KOI Num", formatter=NumberFormatter(format="0.00")),
        TableColumn(field="kepid", title="KIC Num", formatter=NumberFormatter(format="0")),
        TableColumn(field="koi_period", title="Period [day]", formatter=NumberFormatter(format="0.00000")),
        TableColumn(field="koi_time0bk", title="Epoch [BKJD]", formatter=NumberFormatter(format="0.0000")),
        TableColumn(field="koi_duration", title="Duration [hr]", formatter=NumberFormatter(format="0.00")),
        TableColumn(field="koi_depth", title="Depth [ppm]", formatter=NumberFormatter(format="0.00")),
        TableColumn(field="koi_prad", title="Planet Radius [Re]", formatter=NumberFormatter(format="0.00")),
        TableColumn(field="koi_teq", title="Planet Teq [K]", formatter=NumberFormatter(format="0.00")),
        TableColumn(field="koi_insol", title="Insol Flux", formatter=NumberFormatter(format="0.00")),
        TableColumn(field="koi_kepmag", title="KpMag", formatter=NumberFormatter(format="0.00")),
        TableColumn(field="koi_srad", title="Stellar Rad [Rs]", formatter=NumberFormatter(format="0.00")),
        TableColumn(field="koi_steff", title="Stellar Teff [K]", formatter=NumberFormatter(format="0")),
        TableColumn(field="koi_slogg", title="Stellar Logg [cgs]", formatter=NumberFormatter(format="0.00")),
        TableColumn(field="koi_dor", title="a/rstar", formatter=NumberFormatter(format="0.00")),
        TableColumn(field="koi_score", title="Disp Score", formatter=NumberFormatter(format="0.00"))
    ]
    # Make the bokeh data table 
    data_table = DataTable(source=source, columns=columns, height=300, width=1000)
    
    # Do the Figure initially it is log period vs log planet radius
    # Include hovertool
    hover = HoverTool(tooltips=[("KOI", "@koi_number{0.00}")])

    data_figure = figure(height=600, width=1000,x_axis_label='Log Period [Day]', \
                    y_axis_label='Log Rp [Rearth]', tools=[hover, TapTool(), BoxZoomTool(), PanTool(), ZoomOutTool(), ZoomInTool(), ResetTool(), SaveTool()])
    data_figure.axis.axis_line_width=3
    circle_handle = data_figure.circle(x='Logkoi_period', y='Logkoi_prad', source=source, size=10)
    data_figure.axis.axis_label_text_font_size = "20pt"
    data_figure.axis.major_label_text_font_size = "15pt"
    data_figure.axis.major_tick_line_width = 3
    xAxisHandle = data_figure.axis[0]
    yAxisHandle = data_figure.axis[1]
    # Include tap tool to open url with click on point
    taptool = data_figure.select(type=TapTool)
    taptool.callback = OpenURL(url="@koi_url")
    
    # START JAVASCRIPT literal code for handling figure data axis change
    figure_data_callback_code = """
    var data = source.data;
    var labeldata = labels.data;
    var xaxis_data = xaxis_data_obj.value;
    var yaxis_data = yaxis_data_obj.value;
    //These lines change data shown on axis
    circ.glyph.x.field = xaxis_data;
    circ.glyph.y.field = yaxis_data;
    //These lines update the figure axis label
    xaxis.attributes.axis_label = labeldata[xaxis_data][0]
    yaxis.attributes.axis_label = labeldata[yaxis_data][0]

    // Update the source and target
    source.change.emit();
    target_figure_obj.change.emit();
    """
    # END JAVASCRIPT literal code for figure handling
    
    # Figure control widgets that allow user to change data displayed on each axis
    allOptions = [(_key,figure_data_dict[_key][0]) for _key in figure_data_dict]
    xaxis_data_select = Select(title='X-axis Data', value='Logkoi_period', options=allOptions, width=100)
    yaxis_data_select = Select(title='Y-axis Data', value='Logkoi_prad', options=allOptions, width=100)
    
    # define filter widgets without callbacks
    # Define the columns that you want to be able to filter on
    filters_wanted = ["koi_period", "koi_prad", "koi_teq", "koi_insol", \
            "koi_depth", "koi_srad", "koi_steff", "koi_slogg", "koi_score", "koi_kepmag"]
    # Provide the filter names to display
    filters_name = ["Period", "PlanetRadius", "PlanetTeq", "Insol Flux", \
            "Depth","StellarRad","StellarTeff","StellarLogg","Score","KpMag"]
    # Provide the initial min max values to use
    filters_min = [0.0, 0.1, 100.0, 0.1, \
            0.0, 0.05, 1000.0, 2.0, 0.0, 2.0]
    filters_max = [1000.0, 1.0e4, 1.0e4, 1.0e4, \
            1.0e5, 1000.0, 1.0e4, 6.5, 1.0, 30.0]
    # Make the helper bokeh datatable to help convert filter keys with labels for display
    filter_column_dict = {str(j):[x] for j,x in enumerate(filters_wanted)}
    filter_label_source = ColumnDataSource(filter_column_dict)
    
    # Now set up the bokeh widget boxes for filters
    filter_boxs = []
    min_boxs = []
    max_boxs = []
    for i in range(len(filters_wanted)):
        filter_boxs.append(CheckboxGroup(labels=[filters_name[i]], active=[1], width=100))
        min_boxs.append(TextInput(value="{0:6.3f}".format(filters_min[i]), title="Min", width=100, tags=['min_{0:d}'.format(i)]))
        max_boxs.append(TextInput(value="{0:9.3f}".format(filters_max[i]), title="Max", width=100, tags=['max_{0:d}'.format(i)]))

    # Bokeh CustomJS for handling figure data select change
    figure_data_callback = CustomJS(
        args=dict(source=source,
                  circ=circle_handle,
                  xaxis_data_obj=xaxis_data_select,
                  yaxis_data_obj=yaxis_data_select,
                  target_figure_obj=data_figure,
                  labels=axis_label_source,
                  xaxis = xAxisHandle,
                  yaxis = yAxisHandle),
        code=figure_data_callback_code
    )
    # Now attach the callback to the figure control widgets
    xaxis_data_select.callback=figure_data_callback
    yaxis_data_select.callback=figure_data_callback

    # START JAVASCRIPT literal 
    # Callback code used by all filter widgets
    ccc = """
var data = source.data;
var original_data = original_source.data;
var filter_label = filter_label_source.data;
var f_active = [];
var f_on = [];
var mn = [];
var mx = [];

// check if the callback object was the checkbox or minmax value
if (typeof cb_obj.value !== 'undefined') {
  // minmax value changed
  // Find which filter it was from the tags
  var temp = cb_obj.tags[0].split("_")
  var filtid = parseInt(temp[1])
  // modify filter checkbox for this filtid
  evaluate_str = "f" + filtid + ".active[0]=0;"
  eval(evaluate_str)
  evaluate_str = "f" + filtid + ".change.emit();"
  eval(evaluate_str)
}
    """
    ccc = ccc + "var NFILT = {0:d};\n".format(len(filter_boxs))
    # Generate the js code for all filter box handling
    for i in range(len(filter_boxs)):
        ln1 = "mn.push(parseFloat(mn{0:d}.value));\n".format(i)
        ln2 = "mx.push(parseFloat(mx{0:d}.value));\n".format(i)
        ln3 = "f_active.push(f{0:d}.active[0]);\n".format(i)
        ccc = ccc + ln1 + ln2 + ln3
    ccc = ccc + """
for (var i = 0; i < NFILT; ++i) {
    if (f_active[i] == 0) {
        f_on.push(true);    
    } else {
        f_on.push(false);    
    }
}

var element_use = [];
for (var i = 0; i < original_data['koi_number'].length; ++i) {
    var useit = true;
    var k = 0;
    for (var key in filter_label) {
        var currentValue = original_data[filter_label[key][0]][i];
        if (f_on[k] && (currentValue < mn[k] || currentValue > mx[k])) {
            useit = false;
        }
        k++;
    }
    element_use.push(useit);
}            
for ( var key in original_data) {
    data[key] = [];
    for (var i = 0; i < original_data['koi_number'].length; ++i) {
        if (element_use[i]) {
            data[key].push(original_data[key][i]);
        }        
    }
}
source.change.emit();
target_table_obj.change.emit();
target_figure_obj.change.emit();
    """
    # END JAVASCRIPT literal code    
    
    # This is the original code to see how it works for a single filter box
    """
    var period_min = parseFloat(period_min_obj.value);
    var period_max = parseFloat(period_max_obj.value);
    var period_filt_active = period_filt_obj.active[0];
    let period_filt_on;
    
    if (period_filt_active == 0) {
        period_filt_on = true;    
    } else {
        period_filt_on = false;    
    }
    //console.log("Pmin: " + period_min + "Pmax: " + period_max + " " + period_filt_on)
    for (var key in original_data) {
        data[key] = [];
        for (var i = 0; i < original_data['toiNumber'].length; ++i) {
            if ((!period_filt_on) || (period_filt_on && original_data['period'][i] > period_min && 
                    original_data['period'][i] < period_max)) {
                data[key].push(original_data[key][i]);            
            }        
        }        
    }    
    source.change.emit();
    target_table_obj.change.emit();
    target_figure_obj.change.emit();
    """

    

    # now define the callback objects now that the filter widgets exist
    # Build the dictionary list for the filter callbacks
    # Add filter check boxes
    f_dict = { "f{0:d}".format(i):filter_boxs[i] for i in range(len(filter_boxs))}
    mn_dict = { "mn{0:d}".format(i):min_boxs[i] for i in range(len(min_boxs))}
    mx_dict = { "mx{0:d}".format(i):max_boxs[i] for i in range(len(max_boxs))}
    tmp_dict = {}
    tmp_dict['source'] = source
    tmp_dict['original_source'] = original_source
    tmp_dict['target_table_obj'] = data_table
    tmp_dict['target_figure_obj'] = data_figure
    tmp_dict['filter_label_source'] = filter_label_source
    arg_dict = {}
    arg_dict.update(tmp_dict)
    arg_dict.update(f_dict)
    arg_dict.update(mn_dict)
    arg_dict.update(mx_dict)
    filter_callback = CustomJS(
        args=arg_dict,
        code=ccc
    )

    # finally connect the callbacks to the filter widgets
    for i in range(len(filter_boxs)):
        filter_boxs[i].callback = filter_callback
    for i in range(len(min_boxs)):
        min_boxs[i].callback = filter_callback
    for i in range(len(max_boxs)):
        max_boxs[i].callback = filter_callback


    # Set the layout of the table widgets and figure
    # Group filter boxs together   
    fig_widgetbox = Column(xaxis_data_select, yaxis_data_select)
    filter_widget_list = []
    for i in range(len(filter_boxs)):
        filter_widget_list.append(Column(filter_boxs[i], min_boxs[i], max_boxs[i]))
    doc = layout([filter_widget_list, [data_table], [fig_widgetbox,data_figure]])
    #output_file(args.outputFile, mode='inline', root_dir=None)
    output_file(outputFile)
    show(doc)
    