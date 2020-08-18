# -*- coding: utf-8 -*-
"""
Created on Tue Aug  4 13:18:41 2020

@author: karby
"""

import WebScraper as scraper

'''
    The README explains what is going on in this file
'''

base_url = 'https://finance.yahoo.com/quote/'
web_attrs = {'stock_key' : '?p='}

# This is the different type of data we want to get
# And below are the stocks we want to get
tickers = ['AAPL', 'GOOG', 'FB', 'NFLX', 'AMZN', 'WMT']


pages = { 'Income'     : 'financials',  'Balance' : 'balance-sheet',
         'Cash Flow'   : 'cash-flow', 'Key Stats' : 'key-statistics'}


financial_data = {t : scraper.get_data(t, base_url, web_attrs,
                                       pages=pages,
                                       data_source='yahoo', start='2018-1-1',
                                       frequency=1, interval=1)
                  for t in tickers}


