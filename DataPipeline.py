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

class DataPipeline:
    def __init__(self, data, tickers, ind_args=None):
        self.financial_data = data
        self.tickers = tickers
        self.historic = {t : wb.DataReader(t, data_source='yahoo', start='01-01-2020')
                for t in tickers}
        if ind_args:
            self.indicator_arguments = ind_args
            self.indicators = {t : ti.get_indicators(closes=self.historic[t]['Adj Close'],
                                                     hi=self.historic[t]['High'],
                                                     lo=self.historic[t]['Low'],
                                                     args=ind_args)
                       for t in tickers}
    
    '''
    NOTE: The producer of data does not need coroutines decarator.
    
    1). This method will make the request to the webpage.
    2). Then send the data down the pipline, thus producing our data
    '''


    def gen_price(self, url, attrs, target):
        for stock in self.tickers:
            try:
                page  = requests.get(url + stock + attrs['stock_key'] + stock)
                soup  = BeautifulSoup(page.content, 'html.parser')
                price = ws.parse_by_attributes(soup, cols=[stock],
                                                      tabl={BeautifulSoup.find : ('div', {'id' : 'quote-header-info'})},
                                                      rows={BeautifulSoup.find : {'soup'  : ('div', {'id' : 'quote-market-notice'})}},
                                                      data={BeautifulSoup.find : {'tabl'  : ('span', {'class' : 'Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(ib)'})}})
                target.send(price)
            except GeneratorExit:
                print('Goodbye World')

    '''
        This is the decarator used to start our generators so we don't have to
    '''
    def coroutine(func):
        def start(*a, **k):
            cr = func(*a, **k)
            next(cr)
            return cr
        return start
    
    
    
    @coroutine
    def printer(self):
        try:
            while True:
                series = (yield)
                print(series)
        except GeneratorExit:
            print('Done')
            
    @coroutine
    def broadcast(self, targets):
        while True:
            price = (yield)
            for target in targets:
                target.send(price)
                
    
    @coroutine
    def update(self, method, target):
        while True:
            df = (yield)
            price = float(df.values[0][0].replace(',', ''))
            # Here there is only 1 column in the DF which is the ticker
            # I use some logic on how to add the price
            for col in df.columns:
                new_price = self.historic[col].iloc[-1]
                if price < new_price['Low']:
                    new_price['Low'] = price
                elif price > new_price['High']:
                    new_price['High'] = price
                else:
                    new_price['Adj Close'] = price
                self.historic[col] = self.historic[col].append(new_price)
                if method == 'TI':
                    self.indicators[col]['MACD'] = self.indicators[col]['MACD'].append(ti.get_indicators(update='MACD', closes=self.historic[col]['Adj Close'], args=self.indicator_arguments))
                    self.indicators[col]['RSI']  = self.indicators[col]['RSI'].append(ti.get_indicators(update='RSI', closes=self.historic[col]['Adj Close'], args=self.indicator_arguments))
                    self.indicators[col]['BB']   = self.indicators[col]['BB'].append(ti.get_indicators(update='BB', closes=self.historic[col]['Adj Close'], args=self.indicator_arguments))
                    self.indicators[col]['ATR']  = self.indicators[col]['ATR'].append(ti.get_indicators(update='ATR', closes=self.historic[col]['Adj Close'], hi=self.historic[col]['High'], lo=self.historic[col]['Low'],  args=self.indicator_arguments))
                if method == 'PD':
                    print('Running predictors')
                if method == 'REG':
                    print('Running regressions')
            
            target.send(self.indicators)