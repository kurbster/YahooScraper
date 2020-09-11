# -*- coding: utf-8 -*-
"""
Created on Thu Sep 10 18:38:00 2020

@author: karby
"""

import numpy as np
import pandas as pd

# This is a decarator which will ensure the data passed into
# Our technical indicator methods will be ints and not dict_values()
    
# AS OF RIGHT NOW THE ONLY FUNCTION THAT NEED THIS IS ATR WHICH ONLY 
# TAKES IN 1 PARAMETER 
def converter(func):
    def wrapper(**kw):
        ints = [int(v) for v in kw.get('data').values()]
        return func(ints[0], DF=kw.get('DF'))
    return wrapper

# If RSI is > 70 then the asset is over bought
# If RSI is < 30 then the asset is under bought
@converter
def RSI(period, **kw):
    stock = kw.get('DF')
    results = pd.DataFrame()
    results['delta'] = stock['Adj Close'] - stock['Adj Close'].shift(1)
    results['gain']  = np.where(results['delta'] >= 0, results['delta'], 0)
    results['loss']  = np.where(results['delta'] <  0, abs(results['delta']), 0)
    avg_loss = []
    avg_gain = []
    gain = results['gain'].tolist()
    loss = results['loss'].tolist()
    for i in range(len(stock)):
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
@converter
def ATR(period, **kw):
    stock = kw.get('DF')
    results = pd.DataFrame()
    results['H-L']  = stock['High'] - stock['Low']
    # You have to use the previous close so you must use shift
    results['H-PC'] = stock['High'] - stock['Adj Close'].shift(1)
    results['L-PC'] = stock['Low'] - stock['Adj Close'].shift(1)
    results['TR']   = results[['H-L', 'H-PC', 'L-PC']].max(axis=1, skipna=False)
    results['ATR']  = results['TR'].rolling(period).mean()
    return results.drop(['H-L', 'H-PC', 'L-PC'], axis=1)


# The Bollinger Band will sketch a region above and below the mean
# Again more focused on volatility
def BollBand(**kw):
    period, std = kw.get('data').values()
    stock = kw.get('DF')
    results = pd.DataFrame()
    results['MA']   = stock['Adj Close'].rolling(period).mean()
    results['UP']   = results['MA'] + std * results['MA'].rolling(period).std()
    results['DOWN'] = results['MA'] - std * results['MA'].rolling(period).std()
    results.dropna(inplace=True)
    return results

# MACD only uses the 'Adj Close for that stock
def MACD(**kw):
    slow, fast, signal = kw.get('data').values()
    stock = kw.get('DF')
    results = pd.DataFrame()
    results['MA_fast'] = stock['Adj Close'].ewm(span=fast, min_periods=fast).mean()
    results['MA_slow'] = stock['Adj Close'].ewm(span=slow, min_periods=slow).mean()
    results['MACD']    = results['MA_fast'] - results['MA_slow']
    results['signal']  = results['MACD'].ewm(span=signal, min_periods=signal).mean()
    results = results.dropna()
    return results

# This dict maps a name to that function
func_dict = {'MACD' : MACD, 'ATR' : ATR, 'BB': BollBand,
             'RSI'  : RSI}   

# This function takes in kwargs which is a dictionary mapping the different
# Indicators to different parameters for that indicator
def get_financial_indicators(stock, **kw):
    data = {key : {i : func_dict[key](data=arg, DF=stock)
                    for i, arg in enumerate(value)}
                    for key, value in kw.items()}
    return data
