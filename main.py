# -*- coding: utf-8 -*-
"""
Created on Tue Aug  4 13:18:41 2020

@author: karby
"""


from selenium import webdriver
from bs4 import BeautifulSoup
from WebScraper import get_fin_data
import  pandas as pd
import numpy as np


base_url = 'https://finance.yahoo.com/quote/'
# These are the generic attrbutes for calling the proper html
web_attrs = {'stock_key' : '?p=', 'price_key' : '&.tsrc=fin-srch'}

# This is the different type of data we want to get
# And below are the stocks we want to get
tickers = ['AAPL']

get_fin_data(base_url, web_attrs, tickers)