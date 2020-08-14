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
tickers = ['BRK-A', 'GOOG', 'TSLA']

'''
    This dictionary will map a stocks name to another dictionary
    That dictionary maps the name of a dataframe then that DF
    e.x
        financial_data = {'AAPL' : {'Income'   : pd.DataFrame,
                                    'Balance'  : pd.DataFrame,
                                    'Cash'     : pd.DataFrame,
                                    'Historic' : pd.DataFrame,
                                    'Key Stats': pd.DataFrame,
                                    'Price     :[pd.DataFrame]'}}
'''

'''
    pages is a dictionary that maps the user level name to the actual name of
    The page containing that data. When you pass this into get_data it will
    Iterate through each page and get the data for that based on the base_url
    And web attributes
'''

pages = {'Income'      : 'financials',  'Balance' : 'balance-sheet',
         'Cash Flow'   : 'cash-flow', 'Key Stats' : 'key-statistics'}

financial_data = {t : scraper.get_data(base_url, web_attrs, t,
                                       pages=pages,
                                       data_source='yahoo', start='2018-1-1') 
                  for t in tickers}

