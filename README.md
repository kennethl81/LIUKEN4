# LIUKEN4
Coding challenge #4

Installation
===================================================
This script was built using python v3.6.3

Thos script relies on the following additional modules installed via pip3:
    requests
    urllib
    urllib3
    pandas
    bs4(BeautifulSoup)
    bokeh
    
How to Use
===================================================
This script was designed to be run in Jupyter Notebook or a python compatible IDE

Load LIUKEN4.ipynb to execute the script
-or-
use this command:

        import LIUKEN4
        #firstParam= number of days from today's date, secondParam= stock symbol
        LIUKEN4.main(60, "EXPE")


About the Script
===================================================
This script works by making requests to finance.yahoo for a given stock symbol.
The requests are made using a crumb and cookie value that is scraped (this is the only way to allow us to call the file download web service and get past authorization issues) for historical data. On finance.yahoo.com, there is no provided service to download options data besides an API. My script scrapes the options data by making a page request and scraping the data using BeautifulSoup.

When the data is collected (CSVs and HTML strings), they are converted to pandas data frames using the .from_csv and .from_html functions in pandas. After converting data to data frames, the data frames are combined using the merge functionality within pandas. This combined data frame is sent as an argument to the bokeh chart generation function

The execution steps in this script is to generate the bokeh chart. I have chosen the bokeh chart to display the open/close historical prices as lines and call/put options as a scattered plot on the graph. The primary index in common between all historical data and options data is the 'Date' value. I was able to use 'Date' as the x-axis in the bokeh chart and price as the y-axis. 

In drawing the chart, I noticed there were some problems with bokeh converting datetime  correctly to display in the mouse-over tooltip tool. I addressed this issue by parsing through each 'Date' value in the dataframe and converting the value to a simpler date value without the timestamp. I utilized the ColumnDataSource module to define an extra 'DateFormatted' column to use for the dates in the tool tip.

For drawing the lines and scatter plot on the bokeh chart, I read bokeh documentation that stated it was possible to combine a mix of glyphs. I investigated using the multiline glyph for the open/close historical price but it was not as flexible as using two individual line glyphs (due to inability to use more than one source=source parameter). After drawing the lines for the open/close historical price, I used the circle glyph to draw the call/puts strike values. Lastly the chart is displayed using the show(<figure>)</figure>) function call.  