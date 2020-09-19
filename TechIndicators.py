# -*- coding: utf-8 -*-
"""
Created on Thu Sep 10 18:38:00 2020

@author: karby
"""

import numpy as np
import pandas as pd

def dictionary_to_function(func):
        def wrap(*a, **kw):
            kwargs = {k : int(v) for k, v in kw.items()}
            return func(*a, **kwargs).dropna()
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
    return results['RSI']
    
# ATR takes certain ranges and finds the true (max) and average range
# Which is an indicator based on volatility
@dictionary_to_function
def ATR(closes, hi, lo, period):
    assert (period > 0), 'ATR requires 1 positive parameters, period'
    results = pd.DataFrame()
    results['TR']  = TrueRange(closes, hi, lo)
    results['ATR'] = results['TR'].rolling(period).mean()
    return results['ATR']
    
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
    return results['signal']



def get_indicators(update=False, closes=False, hi=False, lo=False, args=False):
    if update:
        kwargs = args[update]
        if update == 'MACD':
            return MACD(closes, **kwargs)
        elif update == 'RSI':
            return RSI(closes, **kwargs)
        elif update == 'BB':
            return BB(closes, **kwargs)
        elif update == 'ATR':
            return ATR(closes, hi, lo, **kwargs)
        else:
            raise BaseException('We havent added that feature yet') 
    else:
        indicator_data = {}
        for func, kwargs in args.items():
            if func == 'MACD':
                indicator_data[func] = MACD(closes, **kwargs)
            elif func == 'RSI':
                indicator_data[func] = RSI(closes, **kwargs)
            elif func == 'BB':
                indicator_data[func] = BB(closes, **kwargs)
            elif func == 'ATR':
                indicator_data[func] = ATR(closes, hi, lo, **kwargs)
            else:
                raise BaseException('We havent added that feature yet')

        return indicator_data
