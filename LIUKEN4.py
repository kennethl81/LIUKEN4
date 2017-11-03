import sys
import unittest
import requests
import urllib.request
import urllib.error
import urllib3.request
import io

import re
#used for loading CSV into Pandas
import csv as csv
import pandas
import numpy
import time

from bs4 import BeautifulSoup
from io import StringIO

class TestMethods(unittest.TestCase):

    # test ability to get a completed url request
    def test_response(self):
        url = 'https://finance.yahoo.com'
        response = requests.get(url, stream=True)
        testResponse = 0
        if response.status_code is not None:
            testResponse = response.status_code

        self.assertEqual(testResponse, 200)

#if __name__ == '__main__':
   # unittest.main()


#url = 'https://uk.finance.yahoo.com/quote/AAPL/history'  # url for a ticker symbol, with a download link
#r = requests.get(url)  # download page

#txt = r.text  # extract html

#cookie = r.cookies['B']  # the cooke we're looking for is named 'B'
#print('Cookie: ', cookie)

# Now we need to extract the token from html.
# the string we need looks like this: "CrumbStore":{"crumb":"lQHxbbYOBCq"}
# regular expressions will do the trick!

#pattern = re.compile('.*"CrumbStore":\{"crumb":"(?P<crumb>[^"]+)"\}')

#for line in txt.splitlines():
#    m = pattern.match(line)
#    if m is not None:
#        crumb = m.groupdict()['crumb']

#print('Crumb=', crumb)

#main function for execution
def main(argsv):

    #these are the download links for the different files
    historical_data_url = "https://query1.finance.yahoo.com/v7/finance/download/EXPE?period1=1478116367&period2=1509652367&interval=1d&events=history&crumb={0}&cookie={1}"
    dividend_data_url = "https://query1.finance.yahoo.com/v7/finance/download/EXPE?period1=1478116367&period2=1509652367&interval=1d&events=div&crumb={0}&cookie={1}"
    crumb_value = "584ln80SGN5" #this is the crumb value that must be used for valid http requests.

    #get the CSV files
    if historical_data_url is not None and dividend_data_url is not None:
        print("Extracting data from finance.yahoo using the following URLs:")

        cookie_value = get_finance_yahoo_cookie()

        if cookie_value is not None: #if we can't get the cookie appended to URLs, then Yahoo will send back an unauthorized request
            crumb = crumb_value

            historical_data_url = format_crumb_and_cookie_url(historical_data_url, crumb, cookie_value)
            dividend_data_url = format_crumb_and_cookie_url(dividend_data_url, crumb, cookie_value)

            print("Historical Data:" + historical_data_url)
            print("Dividend Data: " + dividend_data_url)

            historical_data = get_finance_yahoo(historical_data_url)
            dividend_data = get_finance_yahoo(dividend_data_url)

            #create Pandas data frames
            if historical_data is not None and dividend_data is not None:
                print("Creating data frames for historical and dividend data...")
                historical_data_frame = create_pandas_dataframe_from_csv(historical_data)
                dividend__data_frame = create_pandas_dataframe_from_csv(dividend_data)

            #combine data frames
                if historical_data_frame is not None and dividend__data_frame is not None:
                    print("Combining data frames...")
                    combined_data_frames = combine_pandas_dataframes(historical_data_frame, dividend__data_frame)
                else:
                    print("Unable to create a combined data frame. There might be a problem with one or both CSV inputs.")
        else:
            print("There was a problem downloading the data from finance.yahoo")

def get_finance_yahoo(url):

    #make a request and get a file
    file = requests.post(url)
    #decode_file = file.content.decode('utf-8')
    #read_file = csv.reader(decode_file)

    #for dat in read_file:
        #print(dat)

    return file.content

def format_crumb_and_cookie_url(url, crumb, cookie):

    return url.format(crumb, cookie)

def get_finance_yahoo_cookie():
    #use urllib to get set-cookie value
    #use the finance.yahoo.com web page to scrape
    http = urllib3.PoolManager()

    url = "https://finance.yahoo.com"

    make_request = http.request("GET", "https://finance.yahoo.com")
    #cookie_regex = r"set-cookie': 'B=((.*)(&b))"
    cookie_regex = r"set-cookie': 'B=((.*)\; (expires))"
    cookie_match = re.findall(cookie_regex, str(make_request.headers)) #this will return the string of the set-cookie header

    if len(cookie_match) > 0:
        get_result_from_cookie_match = cookie_match[0] #get cookie value from tuple
        cookie_value = get_result_from_cookie_match[1] #the cookie value

        return cookie_value


def create_pandas_dataframe_from_csv(data):

    if data is not None:
        return pandas.read_csv(StringIO(data.decode('utf-8')))

def combine_pandas_dataframes(df1, df2):

    #how is the type of join (like in SQL)
    #on is what the primary key to use (like in SQL)
    #Date looks like the primary key between the two data frames
    return pandas.merge(df1, df2, how="outer", on="Date")

if __name__=="__main__":
    main(sys.argv)