# -*- coding: utf-8 -*-
"""
Created on Tue Aug  4 13:18:41 2020

@author: karby
"""

import WebScraper as scraper

base_url = 'https://finance.yahoo.com/quote/'
# These are the generic attrbutes for calling the proper html
web_attrs = {'stock_key' : '?p='}

# This is the different type of data we want to get
# And below are the stocks we want to get
tickers = ['AAPL', 'GOOG', 'MRNA', 'FB', 'TSLA', 'WMT']

# This is a dictionary mapping the ticker to a dictionary
# Containing the financial data mapped to its name
financial_data = scraper.get_fin_data(base_url, web_attrs, tickers)
stock_data = scraper.get_stock_data(base_url, web_attrs, tickers)
