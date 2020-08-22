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
tickers = ['AAPL', 'GOOG', 'CAT']


pages = { 'Income'     : 'financials',  'Balance' : 'balance-sheet',
         'Cash Flow'   : 'cash-flow', 'Key Stats' : 'key-statistics'}


financial_data = {t : scraper.get_data(t, base_url, web_attrs,
                                       pages=pages,
                                       frequency=1, interval=1)
                  for t in tickers}

# Currencies or anything that doesn't have the extra pages of data 
# Need to be called in a different loop that doesn't set pages
currencies = ['BTC-USD', 'GC=F']
currency_data = {c : scraper.get_data(c, base_url, web_attrs,
                                       frequency=1, interval=1)
                  for c in currencies}


