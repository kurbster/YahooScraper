# -*- coding: utf-8 -*-
"""
Created on Tue Aug  4 13:18:41 2020

@author: karby
"""

from WebScraper import get_data
from TechIndicators import get_financial_indicators

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


<<<<<<< Updated upstream
financial_data = {t : get_data(t, base_url, web_attrs,
                                       pages=pages,
<<<<<<< Updated upstream
                                       frequency=1, interval=1)
=======
financial_data = {t : scraper.get_data(t, base_url, web_attrs,
                                        pages=pages,
                                        data_source='yahoo', start='2018-1-1',
                                        frequency=1, interval=1)
>>>>>>> Stashed changes
                  for t in tickers}

# Currencies or anything that doesn't have the extra pages of data 
# Need to be called in a different loop that doesn't set pages
currencies = ['BTC-USD', 'GC=F']
currency_data = {c : scraper.get_data(c, base_url, web_attrs,
                                      data_source='yahoo', start='2018-1-1',
                                      frequency=1, interval=1)
                  for c in currencies}

<<<<<<< Updated upstream

=======
                                       data_source='yahoo', start='2018-1-1')
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

indicator_data = {t : get_financial_indicators(financial_data[t]['Historic'], **indicators)
                  for t in tickers}
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
