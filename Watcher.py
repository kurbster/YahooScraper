# -*- coding: utf-8 -*-
"""
Created on Fri Aug  7 17:23:04 2020

@author: karby
"""

from time import sleep

class Watcher:
    def __init__(self, tickers):
        self.stocks = tickers
        
    def add_stock(self, stock):
        self.stocks.append(stock)
        
    def del_stock(self, stock):
        self.stocks.remove(stock)
        
    def watch(self, start, end, interval):
        for s in self.stocks:
            print(s)
        
