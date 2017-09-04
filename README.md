# KOI_DR25_Bokeh
Bokeh Interactive Exploration of Kepler Planet Candidates
Explore the final Kepler Planet Candidate catalog using the python Bokeh package for interactive web graphics.
Run with
python koi_bokehinteract.py
This will generate the html file
koiDR25_BokehInteract.html and usually automatically opens the html page in your browser.
If you are impatient or don't want to run python, then just save to your computer the 
file koiDR25_BokehInteract.html and open it in the browser of your choice.  javascript must be enabled for the table to work.
The webpage consists of the KOI planet candidates from the Data Release 25.
Brief documentation of the data table is here

https://exoplanetarchive.ipac.caltech.edu/docs/PurposeOfKOITable.html#q1-q17_dr25  Soon to be refereed paper by Thompson et al. (in prep)

Also see previous DR24 catalog by Coughlin et al. (2016)
http://adsabs.harvard.edu/abs/2016ApJS..224...12C

The web page consists of a table for the KOIs (planet candidates only).  Using boxes along the top it is possible to filter the table using data columns There is also a figure below the table showing the 'filtered' data from the table.  The default figure is Log(Period) vs. Log(Rplanet), however one can change which columns are plotted.  Hovering over a point will show the points KOI number and selecting a point will open in your browser the DV summary page.  The interaction between the 'Bokeh widgets' is written all in CustomJS so all the data and calculations are done on the client side (i.e. your browser).

