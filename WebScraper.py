# -*- coding: utf-8 -*-
"""
Created on Tue Aug  4 13:37:46 2020

@author: karby

The webscraper class will return the data we get from yahoo finance but not
The price. I am handling the price in the DataPipepline file. Here I am getting
The misccellaneous data like balance sheet, income statement, etc. 
"""

import requests
import pandas as pd
import FileManager as fm
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from time import sleep


'''
    This is the function that you will call from main.py or elsewhere in the program
    You must pass it the base url and the web attributes for that url.
    Also you must pass in the stock you want to get and the specific pages.
    If either of these are empty you will get an exception
'''

def get_data(*args, stock=False, pages=False):
    if not pages or not stock:
        raise BaseException('You forgot to pass a stock to this function' if not stock 
                            else 'You forgot to pass pages to this function')
    if len(args) != 2:
        raise BaseException('You passed ' + str(len(args)) + ' arguments when you needed to pass 2')
    # If a new folder wasn't created then just read the csv
    path = fm.create_folder(stock)
    if not path:
        data = {page : fm.read_file(stock, page) for page in pages}
    else:
        data = {name : parse_page(stock, *args, key=page)
                for name, page in pages.items()}
        fm.write_files(path, data)
        
    return data
        
'''
    This function will make the request to the page and return the answer.
    First it will try to use the build-in pandas method to parse the site.
    If that fails then we have to use selenium to expand the entire table.
'''

def parse_page(stock, *args, key=False):
    url, attrs = args
    page = requests.get(url + stock + '/' + key + attrs['stock_key'] + stock)
    # I first try to parse the page using the <table> element
    # If the page doesn't have a table then the function will return
    # A ValueError exception
    try:
        data = parse_by_table(page, singular=True)
    except ValueError:
        driver = webdriver.Chrome(executable_path=ChromeDriverManager().install())
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
        


'''
    This method will parse whatever is specified by kwargs. kw must include 
    cols, rows, and data which will tell our soup object how to find each one
    Then it will get the proper DF and return
'''

def parse_by_attributes(soup, **kw):
    assert ('cols' in kw and 'rows' in kw and 'data' in kw), 'You must pass the 3 essential elements for making a DF'
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
    return fm.create_DF(**data_elements)    
   
    
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
            button.click()
        except:
            pass
        # If a button was found I want to click it
        else:
            # Then I must recursively call this function
            # So I can check if the new row (new_div) created has a button
            new_div = row.find_element_by_xpath('./div[2]')
            click_buttons(new_div)