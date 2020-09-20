# -*- coding: utf-8 -*-
"""
Created on Sat Sep 12 23:25:13 2020

@author: karby
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

class Predictors:
    def __init__(self, portfolio, plot=False):
        prices = portfolio['Adj Close']
        returns = np.log(1 + prices.pct_change())
        self.u = returns.mean()
        self.var = returns.var()
        self.dev = returns.std()
        
    def Monte_Carlo(self, t, prices, days, iterations):
        drift = self.u - (.5 * self.var)
        dailyReturns = np.exp(drift + self.dev
                              * norm.ppf(
                                  np.random.rand(days, iterations)))
    
        priceList = np.zeros_like(dailyReturns)
        def recursivePrice(index):
            if index == 0:
                priceList[0] = prices.iloc[-1]
                return priceList[0]
            else:
               priceList[index] = recursivePrice(index - 1) * dailyReturns[index]
               return priceList[index]
        
        recursivePrice(days - 1)
        
        if self.plot:
            plt.figure(figsize=(10,6))
            plt.title(t)
            plt.plot(priceList)