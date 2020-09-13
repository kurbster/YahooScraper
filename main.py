# -*- coding: utf-8 -*-
"""
Created on Tue Aug  4 13:18:41 2020

@author: karby
"""

import WebScraper as ws
import TechIndicators as ti
import DataPipeline as dp
import Predictors

'''
    The README explains what is going on in this file
'''

base_url = 'https://finance.yahoo.com/quote/'
web_attrs = {'stock_key' : '?p='}

# This is the different type of data we want to get
# And below are the stocks we want to get
tickers = ['MSFT', 'GOOG', 'DIS', 'M']


pages = { 'Income'     : 'financials',  'Balance' : 'balance-sheet',
         'Cash Flow'   : 'cash-flow', 'Key Stats' : 'key-statistics'}


financial_data = {t : ws.get_data(base_url, web_attrs, pages=pages,stock=t)
                  for t in tickers}

indicators = {'MACD' : [{'slow':26,
                         'fast':12,
                         'signal':9},
                        {'slow':40,
                         'fast':25,
                         'signal':13}],
              'BB'   : [{'mean period':20,
                         'deviation period':2},
                        {'mean period':40,
                         'deviation period':4},
                        {'mean period':10,
                         'deviation period':1}],
              'ATR'  : [{'period':20},
                        {'period':40},
                        {'period':10}],
              'RSI'  : [{'period':14},
                        {'period':10},
                        {'period':20}]
             }

#indicator_data = {t : ti.get_financial_indicators(financial_data[t]['Historic'], **indicators)
 #                 for t in tickers}



#for t in tickers:
 #   dp.gen_price(base_url, web_attrs, t, dp.printer())
#for t in tickers:

