# -*- coding: utf-8 -*-
"""
Created on Tue Aug  4 13:37:46 2020

@author: karby
"""

import os
import requests
import pandas as pd
import numpy as np
from selenium import webdriver
from bs4 import BeautifulSoup
from pandas_datareader import data as wb

'''
    get_data is a function that will return data specified by args and kwargs 
        The only possible args this function can take are:
                base_url  = url
                web_attrs = attrs
        These args must be specified if we are going to get data from yahoo
    
    IF there are no args specified
        Then you want to get the historic data because this uses a built-in
        pandas_datareader method so we don't need the internet
        
        E.X of this call
            get_data('AAPL', data_source='yahoo', start='2018-1-1')
                    These kwargs are required for the pandas method
                    
    IF args has any values then we will get the current price of that stock
                    
    IF the pages kwarg is set then I loop through the pages I want get the DF
        If pages was set then I remove it from kwargs because I don't want
        To pass that to pandas_datareader
        
    Therefore is any more kwargs are set we want to get the historical data
'''

def get_data(stock, *args, **kw):
    data = {}
    if args:
        data['Price'] = parse_page(stock, *args)
    pages = kw.get('pages')
    # If the pages kw was set we need to return the financial pages
    if pages is not None:
        del kw['pages']
        # If a new folder wasn't created then just read the csv
        path = create_folder(stock)
        if not path:
            for page in pages:
                data[page] = read_file(stock, page)
        else:
            fin_data = {name : parse_page(stock, *args, key=page)
                        for name, page in pages.items()}
            write_files(path, fin_data)
            data.update(fin_data)
    if kw:
        data['Historic'] = parse_page(stock, hist=kw)
    return data

# Making the parent directory point to our financial data folder
parent = os.getcwd()
FIN_DIR = os.path.join(parent, 'Financial Data')

def create_folder(stock):
    path = os.path.join(FIN_DIR, stock)
    # I try to make the folder to store the stock data in
    try:
        os.mkdir(path)
        return path
    # If my exception is the file exists then I return false b/c I did not
    # Create a new file. Therefore the funciton that called this will know
    # To read a csv file instead of creating one
    except FileExistsError:
        return False
    # If I get a file not found error then the Financial Data directory
    # Isn't set up on this computer. Therefore I have to make the directory
    # Then recall the method so I can create the stock folder
    except FileNotFoundError:
        os.mkdir(FIN_DIR)
        # I must return the value of path to the parent 
        return create_folder(stock)

def read_file(stock, name, ext='.csv'):
    name += ext
    path = os.path.join(FIN_DIR, stock)
    return pd.read_csv(os.path.join(path, name))

def write_files(path, files, ext='.csv'):
    for name, data in files.items():
        data.to_csv(os.path.join(path, name + ext))
    
'''
    parse_page will always take 1 argument and that is the stock name
    Then it will take 2 extra arguments (url, attrs)
                  OR  0 extra arguments
            IF there are 0 args then we are just using pandas_datareader
            Therefore I don't set the url or attrs
   
    IF there are no kwargs set then we need to return the current price 
    
    IF the kwarg, key, was set then we need to get the page with that key
    
    IF the hist kwarg was set then we need to get the historical data
'''

def parse_page(stock, *args, **kw):
    # If args is empty then we are getting the hist data. Otherwise we need
    # To get the url and web attributes
    if args != ():
        url, attrs = args
    key = kw.get('key')
    hist = kw.get('hist')
    # If kw is empty that means we only want to parse the summary page
    if not kw:
        # There are no buttons I need to press on this page so no need for selenium
        page = requests.get(url + stock + attrs['stock_key'] + stock)
        return parse_by_table(page)
     
    # If key is not None then we need to parse a specific financial page
    if key:
        page = requests.get(url + stock + '/' + key + attrs['stock_key'] + stock)
        # I first try to parse the page using the <table> element
        # If the page doesn't have a table then the function will return
        # A ValueError exception
        try:
            data = parse_by_table(page, singular=True)
        except ValueError:
            driver = webdriver.Chrome('C:\\Users\\karby\\Desktop\\Python Files\\ChromeDriver\\chromedriver')
            driver.get(url + stock + '/' + key + attrs['stock_key'] + stock)
            table = driver.find_element_by_xpath('//*[@id="Col1-1-Financials-Proxy"]/section/div[4]/div[1]/div[1]/div[2]')
            click_buttons(table)
            data = parse_by_attributes(driver.page_source)
            driver.close()
        
        return data
        
    if hist:
        return wb.DataReader(stock, **hist)  


'''
    parse_by_table is used when the page were parsing uses the <table> element
    Therefore we don't need any selenium objects because the data is right 
    There in the table and we can use the built in pandas method to read it
'''
def parse_by_table(page, singular=False):
    soup = BeautifulSoup(page.content, 'html.parser')
    table = soup.find_all('table') 
    df = pd.read_html(str(table))[0] if singular else pd.read_html(str(table))
    return df

'''
    parse_by_attributes will parse our yahoo pages that store their data in
    A div element. Therefore there had to be some finessing to get the data 
'''

def parse_by_attributes(page):
    # Once all of the buttons are pushed I can parse the page
    soup = BeautifulSoup(page, 'html.parser')
    
    # This gives me the top of the table so I can find the column names
    tabl_info = soup.find('div', class_='D(tbr)')
    columns = tabl_info.find_all('span')
        
    # This gives me the data table
    tabl = soup.find('div', class_='D(tbrg)')
    data = tabl.find_all('div', {'data-test' : 'fin-col'})
    names = tabl.find_all('span', class_='Va(m)')
       
    # These are the lists and dictionary I will use to create my pd DataFrame
    rows = [n.text for n in names]      # Names of the data we're taking
    cols = [c.text for c in columns]    # Names of the columns
    # I pop the first value from this list because it is just a placeholder and I dont need it
    cols.pop(0)
    # This is a list of all the data that I reshape so I can create my DF
    temp = np.reshape([d.text for d in data], (len(rows), len(cols)))
    # The orient (or rows) of my data is stored in the key (or index)
    # Of my dictionary, therefore I just used those values
    df = pd.DataFrame(temp, index=rows, columns=cols)
    return df


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
