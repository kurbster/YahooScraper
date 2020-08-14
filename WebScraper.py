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
    get_data is a function that will always return the price of a stock
        NOTE: As of Version 1.2 that means just using yahoo's summary page
    Therefore get_data
'''

def get_data(*args, **kw):
    data = {}
    data['Price'] = parse_page(*args)
    pages = kw['pages']
    # If the pages kw was set we need to return the financial pages
    if pages is not None:
        del kw['pages']
        # If a new folder wasn't created then just read the csv
        path = create_folder(args[-1])
        if not path:
            for page in pages:
                data[page] = read_file(args[-1], page)
        else:
            fin_data = {name : parse_page(*args, key=page)
                        for name, page in pages.items()}
            write_files(path, fin_data)
            data.update(fin_data)
    if kw:
        data['Historic'] = parse_page(*args, hist=kw)
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
    Then it will either take 2 extra arguments (url, attrs)
                         OR  3 extra arguments (url, attrs, key)
                         OR  only keyword arguments
    3 arguments means that I am taking the summary data
    4 arguments means that I am taking specific financial data
    
    Only keword arguments that can tells the method that we want to find
    The historical price data for a stock. Therefore I can us pandas_datareader
    And there is no need to pass in a url or any web attributes
    
            The specific keywords that can be passed in are:
                start=''
                end=''
                data_source='yahoo'
            These are the kwargs passed into wb.DataReader
'''

def parse_page(*args, **kw):
    url, attrs, stock = args
    key = kw.get('key')
    hist = kw.get('hist')
    # kw is empty that means we only want to parse the summary page
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
    # This dictionary maps the row names to the data in that row using
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
