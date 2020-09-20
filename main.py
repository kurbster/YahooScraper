#!/usr/bin/python3
# -*- coding: utf-8 -*-
'''
Created on Tue Aug  4 13:18:41 2020

@author: karby
'''

import WebScraper as ws
import TechIndicators as ti
import DataPipeline
import Predictors as pred

'''
    The README explains what is going on in this file
'''

base_url = 'https://finance.yahoo.com/quote/'
web_attrs = {'stock_key' : '?p='}

# This is the different type of data we want to get
# And below are the stocks we want to get
tickers = ['AAPL', 'GOOG']



pages = { 'Income'     : 'financials',  'Balance' : 'balance-sheet',
         'Cash Flow'   : 'cash-flow', 'Key Stats' : 'key-statistics'}


financial_data = {t : ws.get_data(base_url, web_attrs, pages=pages,stock=t)
                  for t in tickers}

indicators = {'MACD' : {'slow':26,
                         'fast':12,
                         'signal':9},
                        
              'BB'   : {'period':20,
                         'stdev':2},
              'ATR'  : {'period':20},
              'RSI'  : {'period':20}}


dp = DataPipeline.DataPipeline(financial_data, tickers, ind_args=indicators)
for i in range(3):
    dp.gen_price(base_url, web_attrs, dp.broadcast([dp.update('TI',
                                                    dp.printer())]))