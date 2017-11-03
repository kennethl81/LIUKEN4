import unittest
import requests
import urllib
import urllib3.request
import re

# used for loading CSV into Pandas
import pandas
import logging
import sys
import time

from bs4 import BeautifulSoup

# for bokeh
from bokeh.plotting import figure, show
from bokeh.models import HoverTool
from bokeh.layouts import column
from bokeh.transform import jitter
from bokeh.models import ColumnDataSource
from io import StringIO
from datetime import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) #urllib3 keeps warning about not using a certificate


class TestMethods(unittest.TestCase):
    # test ability to get a completed url request
    def test_response(self):
        url = 'https://finance.yahoo.com'
        response = requests.get(url, stream=True)
        testResponse = 0
        if response.status_code is not None:
            testResponse = response.status_code

        self.assertEqual(testResponse, 200)

    # if __name__ == '__main__':
    # unittest.main()


# url = 'https://uk.finance.yahoo.com/quote/AAPL/history'  # url for a ticker symbol, with a download link
# r = requests.get(url)  # download page

# txt = r.text  # extract html

# cookie = r.cookies['B']  # the cooke we're looking for is named 'B'
# print('Cookie: ', cookie)

# Now we need to extract the token from html.
# the string we need looks like this: "CrumbStore":{"crumb":"lQHxbbYOBCq"}
# regular expressions will do the trick!

# pattern = re.compile('.*"CrumbStore":\{"crumb":"(?P<crumb>[^"]+)"\}')

# for line in txt.splitlines():
#    m = pattern.match(line)
#    if m is not None:
#        crumb = m.groupdict()['crumb']

# print('Crumb=', crumb)

# main function for execution
# prevents the warnings from flooding the console from pdfminer from improperly formatted PDFs

def main(argsv):

    exec = run_code()

    count = 1
    while exec is False:
        print("Retrying...(try #:" + str(count) + ")")
        exec = run_code()

        time.sleep(3)
        count += 1

def run_code():
    # these are the download links for the different files
    historical_data_url = "https://query1.finance.yahoo.com/v7/finance/download/EXPE?period1=1478116367&period2=1509652367&interval=1d&events=history&crumb={0}&cookie={1}"
    dividend_data_url = "https://query1.finance.yahoo.com/v7/finance/download/EXPE?period1=1478116367&period2=1509652367&interval=1d&events=div&crumb={0}&cookie={1}"
    options_url = "https://finance.yahoo.com/quote/EXPE/options?p=EXPE"
    crumb_value = "584ln80SGN5"  # this is the crumb value that must be used for valid http requests.

    # get the CSV files
    if historical_data_url is not None and dividend_data_url is not None:
        print("Extracting data from finance.yahoo")

        cookie_value = get_finance_yahoo_cookie()

        if cookie_value is not None:  # if we can't get the cookie appended to URLs, then Yahoo will send back an unauthorized request
            crumb = crumb_value

            historical_data_url = format_crumb_and_cookie_url(historical_data_url, crumb, cookie_value)
            dividend_data_url = format_crumb_and_cookie_url(dividend_data_url, crumb, cookie_value)

            #print("Historical Data:" + historical_data_url)
            # print("Dividend Data: " + dividend_data_url)

            historical_data = get_finance_yahoo(historical_data_url)
            dividend_data = get_finance_yahoo(dividend_data_url)

            # create Pandas data frames
            if historical_data is not None and dividend_data is not None:
                print("Creating data frames for historical and dividend data...")
                historical_data_frame = create_pandas_dataframe_from_csv(historical_data)
                dividend__data_frame = create_pandas_dataframe_from_csv(dividend_data)
                options = get_finance_yahoo_options(options_url)

                # combine data frames
                if historical_data_frame is not None and dividend__data_frame is not None:
                    print("Combining data frames...")
                    combined_data_frames = combine_pandas_dataframes(historical_data_frame, dividend__data_frame) #combine historical and dividends
                    combined_data_frames = combine_pandas_dataframes(combined_data_frames, options[0][0]) #combine call options
                    combined_data_frames = combine_pandas_dataframes(combined_data_frames, options[1][0])  # combine put options
                    if combined_data_frames is not None:
                        print("Data frames combined")
                        generate_bokeh_chart(combined_data_frames)
                        return True
                else:
                    print("Unable to create a combined data frame. There might be a problem with one or both CSV inputs.")
        else:
            print("There was a problem downloading the data from finance.yahoo. The script will try again. This issue "
                  "is usually caused by a network issue between the client and server.")
            return False


def get_finance_yahoo(url):
    # make a request and get a file
    file = requests.post(url)
    # decode_file = file.content.decode('utf-8')
    # read_file = csv.reader(decode_file)

    # for dat in read_file:
    # print(dat)

    return file.content

def get_finance_yahoo_options(url):

    page = urllib.request.urlopen(url)
    soup = BeautifulSoup(page, 'html.parser')

    calls = ""
    puts = ""

    #get calls table and convert it to a dataframe
    calls_table = soup.findAll('table', attrs={'class': 'calls table-bordered W(100%) Pos(r) Bd(0) Pt(0) list-options'})
    calls_table = str.replace(str(calls_table), 'Last Trade Date', 'Date')
    calls_table = str.replace(calls_table, 'Strike', 'Calls Strike')
    calls = pandas.read_html(str(calls_table))

    #get puts table and convert it to a dataframe
    puts_table = soup.findAll('table', attrs={'class': 'puts table-bordered W(100%) Pos(r) list-options'})
    puts_table = str.replace(str(puts_table), 'Last Trade Date', 'Date')
    puts_table = str.replace(puts_table, 'Strike', 'Puts Strike')
    puts = pandas.read_html(str(puts_table))

    return (calls, puts)

def generate_bokeh_chart(pandas_data_frame):

    numlines = len(pandas_data_frame.columns)

    pandas_data_frame['Date'] = pandas.to_datetime(pandas_data_frame['Date'])
    dates = [str(datetime.strptime(str(i), "%Y-%m-%d %H:%M:%S").date()) for i in pandas_data_frame['Date']]

    open_price_source = ColumnDataSource(data={
            'Date': pandas_data_frame['Date'],
            'Open': pandas_data_frame['Open'],
            'DateFormatted': dates,
    })

    close_price_source = ColumnDataSource(data={
            'Date': pandas_data_frame['Date'],
            'Close': pandas_data_frame['Close'],
            'DateFormatted': dates
    })

    calls_price_source = ColumnDataSource(data={
            'Date': pandas_data_frame['Date'],
            'Calls Strike': pandas_data_frame['Calls Strike'],
            'DateFormatted': dates
    })

    puts_price_source = ColumnDataSource(data={
            'Date': pandas_data_frame['Date'],
            'Puts Strike': pandas_data_frame['Puts Strike'],
            'DateFormatted': dates
    })

    hover = HoverTool(tooltips=[
        ("price", "$y"),
        ("date","@DateFormatted")
        ]
    )

    p = figure(width=800, height=800,  x_axis_type="datetime", title="Expedia Stock", tools=["pan,wheel_zoom,box_zoom,reset", hover], toolbar_location="above")

    p.xaxis.axis_label = 'Date'
    p.yaxis.axis_label = 'Price'

    p.line('Date', 'Open', source=open_price_source, color="green", line_width=2, legend="Open Price")
    p.line('Date', 'Close', source=close_price_source, color="blue", line_width=2, legend="Close Price")

    #draw calls strike
    #p.circle(pandas_data_frame["Date"].tolist(), pandas_data_frame["Calls Strike"].tolist(), size=5, color="navy", alpha=0.5, legend="Calls Strike")
    #p.circle(pandas_data_frame["Date"].tolist(), pandas_data_frame["Puts Strike"].tolist(), size=5, color="red", alpha=0.5, legend="Puts Strike")
    p.circle('Date','Calls Strike', source=calls_price_source, size=5, color="navy",
             alpha=0.5, legend="Calls Strike Price")
    p.circle('Date','Puts Strike', source=puts_price_source, size=5, color="red",
             alpha=0.5, legend="Puts Strike Price")
    show(p)

def format_crumb_and_cookie_url(url, crumb, cookie):
    return url.format(crumb, cookie)


def get_finance_yahoo_cookie():
    # use urllib to get set-cookie value
    # use the finance.yahoo.com web page to scrape
    http = urllib3.PoolManager()

    url = "https://finance.yahoo.com"

    make_request = http.request("GET", "https://finance.yahoo.com")
    # cookie_regex = r"set-cookie': 'B=((.*)(&b))"
    cookie_regex = r"set-cookie': 'B=((.*)\; (expires))"
    cookie_match = re.findall(cookie_regex,
                              str(make_request.headers))  # this will return the string of the set-cookie header

    if len(cookie_match) > 0:
        get_result_from_cookie_match = cookie_match[0]  # get cookie value from tuple
        cookie_value = get_result_from_cookie_match[1]  # the cookie value

        return cookie_value


def create_pandas_dataframe_from_csv(data):
    if data is not None:
        return pandas.read_csv(StringIO(data.decode('utf-8')))


def combine_pandas_dataframes(df1, df2):
    # how is the type of join (like in SQL)
    # on is what the primary key to use (like in SQL)
    # Date looks like the primary key between the two data frames
    return pandas.merge(df1, df2, how="outer", on="Date")


if __name__ == "__main__":
    main(sys.argv)