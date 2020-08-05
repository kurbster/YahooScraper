# -*- coding: utf-8 -*-
"""
Created on Tue Aug  4 13:37:46 2020

@author: karby
"""

from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import requests
import re

def get_fin_data(url, attrs, tickers):
    global stocks, base_url, web_attrs
    base_url = url
    web_attrs = attrs
    stocks = tickers
    for stock in stocks:
        income_statement = parse_page('financials', stock)
        #balance_sheet = parse_page('balance-sheet', stock)
        #cash_flow = parse_page('cash-flow',         stock)
        price_page = parse_page(None,               stock)
        print(income_statement)
        
        
def parse_page(key='financials', stock='AAPL'):
    # If the key is None then I want to get the front page of the app
    # Which contains the current price of the stock
    if key is None:
        url = base_url + stock + web_attrs['stock_key'] + stock + web_attrs['price_key']
        # There are no buttons I need to press on this page so no need for selenium
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')
        regex = re.compile('W(100%)*')
        table = soup.find_all('table', class_=regex)
    
    else:
        key = 'financials'
        stock ='AAPL'
        # I get the url associated with what ever is passed in
        url = base_url + stock + '/' + key + web_attrs['stock_key'] + stock
        # Then I get the driver object and the data table
        driver = webdriver.Chrome('C:\\Users\\karby\\Desktop\\Python Files\\ChromeDriver\\chromedriver')
        driver.get(url)
        table = driver.find_element_by_xpath('//*[@id="Col1-1-Financials-Proxy"]/section/div[4]/div[1]/div[1]/div[2]')
        click_buttons(table)
        # Once all of the buttons are pushed I can parse the page
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # This gives me the top of the table so I can find the column names
        tabl_info = soup.find('div', class_='D(tbr)')
        cols = tabl_info.find_all('span')
        
        # This gives me the data table
        tabl = soup.find('div', class_='D(tbrg)')
        data = tabl.find_all('div', {'data-test' : 'fin-col'})
        names = tabl.find_all('span', class_='Va(m)')
        
        temp = {}
        for i,d in enumerate(data):
            row_num = i // (len(cols) - 1)
            if i % (len(cols) - 1) == 0:
                temp[row_num] = [d.text]
            else:
                temp[row_num].append(d.text)
        
        
        driver.close()
        
    

def click_buttons(element):
    # First I get all the children of the web element being passed in
    # These children our the data rows some which contain another button
    rows = element.find_elements_by_xpath('*')
    for row in rows:
        # I must catch the not found exception
        try:
            button = row.find_element_by_xpath('.//button')
        except:
            pass
        # If a button was found I want to click it
        else:
            button.click()
            # Then I must recursively call this function
            # So I can check if the new row (new_div) created has a button
            new_div = row.find_element_by_xpath('./div[2]')
            click_buttons(new_div)
