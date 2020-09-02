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
from webdriver_manager.firefox import GeckoDriverManager
from bs4 import BeautifulSoup
from pandas_datareader import data as wb
from time import sleep

'''
    get_kwargs is a decarator for our get_data function which basically 
    Gets the specific input values from **kw and passes them into the function
'''


def get_kwargs(func):
    def wrapper(stock, *args, **kw):
        X = lambda keys, kws: {k : v for k, v in kws.items() if k in keys}
        hist = X(['data_source', 'start', 'end'], kw)
        price = X(['frequency', 'interval'], kw)
        pages = kw.get('pages')
        return func(stock, hist, price, pages, *args)
    return wrapper


'''
    get_data is a function that will return the data of a specific stock
    To do this I make a dictionary then add the desired data based on the parameters.
    Example of different parameters:
        *args will always represent the url and web attributes. 
        Therefore if args is set then we will call parse_page with no kwargs
        Which will just parse the summary page.
            'https://finance.yahoo.com/quote/AAPL?p=AAPL'
        
        
        If the pages parameter is set then we must loop through that
        Dictionary and either read the already existing .csv file or 
        Read the data from the website using parse_page with key=page
        
        If the parameters hist or price are set then we call parse_page
        With the specific **kwargs. Historic data does need *args because 
        I use a built in pandas method and not requests/BeautifulSoup
        
'''

@get_kwargs
def get_data(stock, hist, price, pages, *args):
    data = {}
    if args:
        data['Summary'] = parse_page(stock, *args)
    # If the pages kw was set we need to return the financial pages
    if pages:
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
    
    # These are all of the possible kw args I will pass into the parse page
    # Function, which in this case will ultimately call the DataReader method
    if hist:
        data['Historic'] = parse_page(stock, **hist)

    if price:
        data['Price'] = parse_page(stock, *args, **price)
    return data

# Making the parent directory point to our financial data folder
parent  = os.getcwd()
FIN_DIR = os.path.join(parent, 'Data')
CHROME  = os.path.join(parent, 'ChromeDriver')

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
   
    IF there are no kwargs set then we need to return the summary page
    
    IF the kwarg, key, was set then we need to get the page with that key
    
    IF args was set and we haven't returned yet that means we called this function
    Trying to return the current price over a certain interval every frequency seconds
'''

def parse_page(stock, *args, **kw):
    # If args is not set then I am returning the historical data using the builin method
    if not args:
        return wb.DataReader(stock, **kw)
   
    # Otherwise I am parsing a page from the internet
    else:
        url, attrs = args
        key = kw.get('key')
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
                '''
                    THERE IS STILL A PROBLEM HERE WITH THE SELENIUM OBJECT. IDK
                '''
                driver = webdriver.Firefox(executable_path=GeckoDriverManager().install())
                driver.get(url + stock + '/' + key + attrs['stock_key'] + stock)
                table = driver.find_element_by_xpath('//*[@id="Col1-1-Financials-Proxy"]/section/div[4]/div[1]/div[1]/div[2]')
                click_buttons(table)
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                data = parse_by_attributes(soup, 
                                      tabl_info={BeautifulSoup.find : ('div', {'class' : 'D(tbr)'})},
                                           tabl={BeautifulSoup.find : ('div', {'class' : 'D(tbrg)'})},
                                           cols={BeautifulSoup.find_all : {'tabl_info' : ('div' , {'class' : 'Ta(c)'})}},
                                           rows={BeautifulSoup.find_all : {'tabl'      : ('span', {'class' : 'Va(m)'})}},
                                           data={BeautifulSoup.find_all : {'tabl'      : ('div' , {'data-test' : 'fin-col'})}})
                                      
                driver.close()
            
            return data
        
        # If nothing else has returned this function then we are getting the current price
        # This will run interval amount of times, sleeping frequency seconds each time
        else:
            data = pd.DataFrame()
            for i in range(kw.get('interval')):
                page = requests.get(url + stock + attrs['stock_key'] + stock)
                soup = BeautifulSoup(page.content, 'html.parser')
                # You have to pass stock here as a 3D list
                data = data.append(parse_by_attributes(soup,
                                       cols=[[[stock]]], 
                                       rows={BeautifulSoup.find : {'soup' : ('span', {'data-reactid' : '53'})}},
                                       data={BeautifulSoup.find : {'soup' : ('span', {'data-reactid' : '50'})}}))
                sleep(kw.get('frequency'))
            return data


'''
    parse_by_attributes is a function that will parse a page using BeautifulSoup
    based on the kwargs that are passed in. 
    NOTE: FOR THIS FUNCTION TO WORK YOU MUST PASS IN COLS, ROWS, AND DATA
    This is because these elements are used to create the pd.DataFrame
    
    The function works in 2 parts
        1). First evaluate the elements that will not be used for pandas
            and are there to help you find the elements that will. Therefore
            I need to save the soup elements in a dictionary
        
        2). Second I evaluate the elements that will be used for pandas
            Which I use the soup_element dictionary to help me use the right
            soup object to call the soup function
            
'''    
def parse_by_attributes(soup, **kw):
    attrs = ['cols', 'rows', 'data']
    soup_elements = {name : [func(soup, name=args[0], attrs=args[1])
                    for func, args in path.items()]
                    for name, path in kw.items() if name not in attrs}
    soup_elements['soup'] = [soup]
    
    data_elements = {name : [[func(soup_elements[obj][0], name=attrs)  
                                      if type(attrs) is str
                                      else func(soup_elements[obj][0], name=attrs[0], attrs=attrs[1])
                              for obj, attrs in args.items()]
                              for func, args in path.items()]
                              for name, path in kw.items() if name in attrs
                              if type(path) is dict}
    
    # If the user declared one of the data elements in stead of resolving it
    # Through soup elements then the above loop wouldn't resolve it so I do it here
    # NOTE: If you want to declare the data element then you must pass in a 3D list
    # Because of the create_df method
    for attr in attrs:
        if attr not in data_elements:
            data_elements[attr] = kw.get(attr)
    return create_DF(**data_elements)    
   
    
    
def create_DF(**kw):
    # If the values are soup elements then I need to call r.text
    try:
        row_vals = [[[r.text for r in rows]
                         for rows in entry]
                         for entry in kw.get('rows')]
        
    # If I get this exception then the values are strings so I don't call .text
    except AttributeError:
        row_vals = [[[r  for r in rows]
                         for rows in entry]
                         for entry in kw.get('rows')]
        col_vals = [[[c  for c in columns]
                         for columns in entry]
                         for entry in kw.get('cols')]
        data_vals = [[[d for d in data]
                         for data in entry]
                         for entry in kw.get('data')]
    else:
        col_vals = [[[c.text for c in columns]
                         for columns in entry]
                         for entry in kw.get('cols')]
        data_vals = [[[d.text for d in data]
                         for data in entry]
                         for entry in kw.get('data')]
    
    rows, cols, temp = row_vals[0][0], col_vals[0][0], data_vals[0][0]
    data = np.reshape(temp, (len(rows), len(cols)))
    return pd.DataFrame(data, index=rows, columns=cols)

    
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
