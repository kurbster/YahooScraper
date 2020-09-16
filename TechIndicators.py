# -*- coding: utf-8 -*-
"""
Created on Thu Sep 10 18:38:00 2020

@author: karby
"""

import numpy as np
import pandas as pd
from pandas_datareader import data as wb

def dictionary_to_function(func):
        def wrap(*a, **kw):
            kwargs = {k : int(v) for k, v in kw.items()}
            return func(*a, **kwargs)
        return wrap
    
# If RSI is > 70 then the asset is over bought
# If RSI is < 30 then the asset is under bought
@dictionary_to_function
def RSI(closes, period):
    assert period > 0, 'RSI requires 1 positive parameter'
    results = pd.DataFrame()
    results['delta'] = closes - closes.shift(1)
    results['gain']  = np.where(results['delta'] >= 0, results['delta'], 0)
    results['loss']  = np.where(results['delta'] <  0, abs(results['delta']), 0)
    avg_loss = []
    avg_gain = []
    gain = results['gain'].tolist()
    loss = results['loss'].tolist()
    for i in range(len(closes)):
        if i < period :
            avg_gain.append(np.NaN)
            avg_loss.append(np.NaN)
        elif i == period:
            avg_gain.append(results['gain'].rolling(period).mean().tolist()[period])
            avg_loss.append(results['loss'].rolling(period).mean().tolist()[period])
        else:
            avg_gain.append(((period - 1)*avg_gain[i-1] + gain[i])/period)
            avg_loss.append(((period - 1)*avg_loss[i-1] + loss[i])/period)
        
    results['avg gain'] = np.array(avg_gain)
    results['avg loss'] = np.array(avg_loss)
    results['RS'] = results['avg gain'] / results['avg loss']
    results['RSI'] = 100 - (100 / (1 + results['RS']))
    return results
    
# ATR takes certain ranges and finds the true (max) and average range
# Which is an indicator based on volatility
@dictionary_to_function
def ATR(closes, hi, lo, period):
    assert (period > 0), 'ATR requires 1 positive parameters, period'
    results = pd.DataFrame()
    results['TR']  = TrueRange(closes, hi, lo)
    results['ATR'] = results['TR'].rolling(period).mean()
    return results
    
@dictionary_to_function
def ADX(closes, hi, lo, period):
    assert (period > 0), 'ADX requires 1 positive parameters, period'
    results = pd.DataFrame()
    results['TR']  = TrueRange(closes, hi, lo)
    results['DM+'] = np.where((results['High'] - results['High'].shift(1)) > 
                                   (results['Low'].shift(1) - results['Low']), 0)
    results['DM+'] = np.where(results['DM+'] < 0, 0, results['DM+'])
    results['DM-'] = np.where((results['High'] - results['High'].shift(1)) < 
                                   (results['Low'].shift(1) - results['Low']), 0)
    results['DM-'] = np.where(results['DM-'] < 0, 0, results['DM-'])
    print(results)
    return results
        
    
def TrueRange(closes, hi, lo):
    temp = pd.DataFrame()
    temp['H-L']  = abs(hi - lo)
    # You have to use the previous close so you must use shift
    temp['H-PC'] = abs(hi - closes.shift(1))
    temp['L-PC'] = abs(lo - closes.shift(1))
    return temp[['H-L', 'H-PC', 'L-PC']].max(axis=1, skipna=False)
    
# The Bollinger Band will sketch a region above and below the mean
# Again more focused on volatility
@dictionary_to_function
def BB(closes, period, stdev):
    assert (period > 0 and stdev), 'Bollinger Bands requires 2 parameters, period > 0 and stdev'
    results = pd.DataFrame()
    results['MA']   = closes.rolling(period).mean()
    results['UP']   = results['MA'] + stdev * results['MA'].rolling(period).std()
    results['DOWN'] = results['MA'] - stdev * results['MA'].rolling(period).std()
    results.dropna(inplace=True)
    return results
    
# MACD only uses the 'Adj Close for that stock
@dictionary_to_function
def MACD(closes, slow, fast, signal):
    assert (slow > 0 and fast > 0 and signal > 0), 'MACD requires 3 positive parameters, slow, fast'
    results = pd.DataFrame()
    results['MA_fast'] = closes.ewm(span=fast, min_periods=fast).mean()
    results['MA_slow'] = closes.ewm(span=slow, min_periods=slow).mean()
    results['MACD']    = results['MA_fast'] - results['MA_slow']
    results['signal']  = results['MACD'].ewm(span=signal, min_periods=signal).mean()
    results = results.dropna()
    return results

class Indicators:
    def __init__(self, sym, commands, start='01-01-2019'):    
        self.stock = sym
        self.historical = wb.DataReader(sym, data_source='yahoo', start=start)
        
        # Here I am remapping this indicators object to the indicator the user wanted
        for func, kwarg in commands.items():
            if func == 'MACD':
                self.macd = kwarg
            elif func == 'RSI':
                self.rsi_data  = kwarg
            elif func == 'BB':
                self.bb = kwarg
            elif func == 'ATR':
                self.atr = kwarg
    
    '''
        TODO: Add setter methods so we can change what are analysis is.
        Right now when you call the function it will use that indicator objects
        Data.
        
        TODO: Finish pluging in the update generator so I can update the 
        Indicators accordingly.
    '''
    def MACD(self, c):     return MACD(c  , **self.macd)
    def RSI(self , c):     return RSI( c  , **self.rsi )
    def BB(self  , c):     return BB(  c  , **self.bb  )
    def ATR(self , c,h,l): return ATR(c,h,l **self.atr )
    
    def get(self):
        return self.historical
    
    def update(self):
        while True:
            price = (yield)
            '''
            do stuff here
            '''
            
    