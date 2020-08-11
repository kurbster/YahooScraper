# -*- coding: utf-8 -*-
"""
Created on Tue Aug  4 13:18:41 2020

@author: karby
"""

import WebScraper as scraper

'''
    base_url doesn't change between calls nor the different attributes
    To help you navigate the website the only one needed is '?p='
    Therefore each page only differs in the stock name
    e.x
    This will get the stock chart for AAPL
        https://finance.yahoo.com/quote/AAPL?p=AAPL
    
    This will get the balance sheet for AAPL
        https://finance.yahoo.com/quote/AAPL/balance-sheet?p=AAPL
    
'''

base_url = 'https://finance.yahoo.com/quote/'
web_attrs = {'stock_key' : '?p='}

# This is the different type of data we want to get
# And below are the stocks we want to get
tickers = ['AAPL', 'GOOG', 'FB', 'WMT', 'TSLA', 'MRNA', 'F', 'BRK-A']

'''
    This dictionary will map a stocks name to another dictionary
    That dictionary maps the name of a dataframe then that DF
    e.x
        financial_data = {'AAPL' : {'income'   : pd.DataFrame,
                                    'balance'  : pd.DataFrame,
                                    'cash'     : pd.DataFrame,
                                    'historic' : pd.DataFrame,
                                    'current'  : pd.DataFrame}}
'''
financial_data = {}

for t in tickers:
    financial_data[t] = scraper.get_fin_data(base_url, web_attrs, t)
    
