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
from bs4 import BeautifulSoup, Tag
from time import sleep


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

    
def get_data(*args, stock=False, pages=False):
    if not pages or not stock:
        raise BaseException('You forgot to pass a variable to this function')
    # If a new folder wasn't created then just read the csv
    path = create_folder(stock)
    if not path:
        data = {page : read_file(stock, page) for page in pages}
    else:
        data = {name : parse_page(stock, *args, key=page)
                for name, page in pages.items()}
        write_files(path, data)
    return data
        


def parse_page(stock, *args, key=False):  
    url, attrs = args
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
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        data = parse_by_attributes(soup, 
                                      tabl_info={BeautifulSoup.find : ('div', {'class' : 'D(tbr)'})},
                                           tabl={BeautifulSoup.find : ('div', {'class' : 'D(tbrg)'})},
                                           cols={BeautifulSoup.find_all : {'tabl_info' : ('div' , {'class' : 'Ta(c)'})}},
                                           rows={BeautifulSoup.find_all : {'tabl'      : ('span', {'class' : 'Va(m)'})}},
                                           data={BeautifulSoup.find_all : {'tabl'      : ('div' , {'data-test' : 'fin-col'})}})
                                      
        driver.close()
            
    return data
        



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
    
    # When I am getting the stock price I pass in the name of the stock
    # Rather then a dictionary telling me how to get there
    # Therefore the above for loop won't add it to our data_elements therefore I do
    for attr in attrs:
        if attr not in data_elements:
            data_elements[attr] = kw.get(attr)
    return create_DF(**data_elements)    
   
    
'''
    create_DF is a funtion that takes in a dictionary that must have the keys
            rows, cols, and data.
    This function takes that dictionary and returns the associating DataFrame
'''
def create_DF(**kw):
    rows = to_list(kw.get('rows'))
    cols = to_list(kw.get('cols'))
    data = to_list(kw.get('data'))
    return pd.DataFrame(np.reshape(data, (len(rows), len(cols))), index=rows, columns=cols)


'''
    to_list is a funtion that takes in a list of objects and returns a single
    Dimension list of type str. This function has 2 parts:
        1). Recursively call this method until myList is a 1D list
        2). Then check what type of data the list holds and perform the right action
'''
def to_list(myList):
    # If the next dimension is also a list then recursively call this method
    # Until we don't have anymore lists to go through
    if isinstance(myList[0], list):
        return to_list(myList[0])
    else:
        # If myList contains BeautifulSoup tags then we need to return
        # The string attribute of each tag
        if isinstance(myList[0], Tag):
            return [e.string for e in myList]
        else:
            return myList
    
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
            '''
            WIERD BUG IF YOU DON'T SLEEP BEFORE YOU CLICK
            SOMETIMES IT WILL NOT CLICK THE FIRST BUTTON 
            BUT WILL CLICK EVERYTHING ELSE
            
            UPDATE:
                This is because firefox is slower than chrome
                And sometimes isnt loading the data fast enough
                
                Can someone eventually help with this? We only use this 
                Code everytime we get a new stock so I don't think it
                Really matters because we should only be invested in a few 
                Stock and will already have that data saved
            '''
            sleep(.75)
            button.click()
        except:
            pass
        # If a button was found I want to click it
        else:
            # Then I must recursively call this function
            # So I can check if the new row (new_div) created has a button
            new_div = row.find_element_by_xpath('./div[2]')
            click_buttons(new_div)