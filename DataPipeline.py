# -*- coding: utf-8 -*-
"""
Created on Sat Sep 12 20:38:42 2020

@author: karby
"""

import requests
from bs4 import BeautifulSoup
from pandas_datareader import data as wb
import WebScraper as ws
import TechIndicators as ti
'''
    This is the decarator used to start our generators so we don't have to
'''
def coroutine(func):
    def start(*a, **k):
        cr = func(*a, **k)
        next(cr)
        return cr
    return start

'''
    NOTE: The producer of data does not need coroutines decarator.
    
    1). This method will make the request to the webpage.
    2). Then send the data down the pipline, thus producing our data
'''


def gen_price(url, attrs, stock, target):
    page  = requests.get(url + stock + attrs['stock_key'] + stock)
    soup  = BeautifulSoup(page.content, 'html.parser')
    price = ws.parse_by_attributes(soup, cols=[stock],
                                              tabl={BeautifulSoup.find : ('div', {'id' : 'quote-header-info'})},
                                              rows={BeautifulSoup.find : {'soup'  : ('div', {'id' : 'quote-market-notice'})}},
                                              data={BeautifulSoup.find : {'tabl'  : ('span', {'class' : 'Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(ib)'})}})
    target.send(price)


@coroutine
def printer():
    try:
        while True:
            series = (yield)
            print(series)
    except GeneratorExit:
        print('Done')
        
@coroutine
def broadcaster(targets):
    while True:
        price = (yield)
        for target in targets:
            target.send(price)

def init_pipeline(data, indicators, tickers):
    historic = {t : wb.DataReader(t, data_source='yahoo', start='01-01-2020')
                for t in tickers}
    indicators_init = {t : ti.get_indicators(stock=t, closes=historic[t]['Adj Close'], hi=historic[t]['High'], lo=historic[t]['Low'], indicators=indicators)
                       for t in tickers}
    return indicators_init
