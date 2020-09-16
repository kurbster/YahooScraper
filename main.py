#!/usr/bin/python3
# -*- coding: utf-8 -*-
'''
Created on Tue Aug  4 13:18:41 2020

@author: karby
'''

import WebScraper as ws
import TechIndicators as ti
import DataPipeline as dp
import Predictors as pred
from pandas_datareader import data as wb
'''
    The README explains what is going on in this file
'''

base_url = 'https://finance.yahoo.com/quote/'
web_attrs = {'stock_key' : '?p='}

# This is the different type of data we want to get
# And below are the stocks we want to get
tickers = ['XOM', 'GOOG', 'AAPL']


pages = { 'Income'     : 'financials',  'Balance' : 'balance-sheet',
         'Cash Flow'   : 'cash-flow', 'Key Stats' : 'key-statistics'}


financial_data = {t : ws.get_data(base_url, web_attrs, pages=pages,stock=t)
                  for t in tickers}

financial_data['Historic'] = {t : wb.DataReader(t, data_source='yahoo', start='01-01-2020')
                             for t in tickers}

indicators = {'MACD' : [{'slow':26,
                         'fast':12,
                         'signal':9},
                        {'slow':26,
                         'fast':12,
                         'signal':9}],
              'BB'   : [{'period':20,
                         'stdev':2}],
              'ATR'  : [{'period':20},{'period':40},{'period':14}],
              'RSI'  : [{'period':20},{'period':40},{'period':14}]}


print(dp.init_pipeline(financial_data, indicators, tickers))
'''
    for ever ticker we will generate the price then use the 
    broadcast function to push that value to our indicators,
    regression, etc.
'''

'''
for t in tickers:
    dp.gen_price(base_url, web_attrs, t, dp.broadcast(
        myIndicators, ti.update()))

'''
