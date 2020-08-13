# -*- coding: utf-8 -*-
"""
Created on Tue Aug  4 13:37:46 2020

@author: karby
"""

import pandas as pd
import os
import requests
from selenium import webdriver
from bs4 import BeautifulSoup
from pandas_datareader import data as wb

'''
    get_data is a function that will take in either 0, 3, or 4 arguments
        If it is passed 0 then kwargs must be set and we are only getting 
            historical data
        If it is passed 3 then we are getting the current price summary of
            that particular stock
        If it is passed 4 then we are getting data from financial pages
            which is the extra argument passed in
    E.X
        get_data(url, web_attrs, AAPL) -> get current stock price of AAPL
        get_data(url, web_attrs, pages, AAPL) -> get financial data for 
                every page in the pages variable
        get_data(data_source='yahoo', 'start'='2008-1-1') -> get the historical
                data for this stock with these kwargs
                
    NOTE
        The method will return the price summary every time unless you set
            get_price=False
        It will also return the historical if kw is set no matter what *args is
'''

def get_data(*args, **kw):
    data = {}
    data['summary'] = parse_page(*args)
    pages = kw.get('pages')
    # If the pages kw was set we need to return the financial pages
    if pages is not None:
        # If a new folder wasn't created then just read the csv
        path = create_folder(args[-1])
        if not path:
            fin_data = {name : read_csv(args[-1], name)
                        for name in pages}
            data.update(fin_data)
        else:
            fin_data = {name : parse_page(*args, key=page)
                        for name, page in pages.items()}
            write_files(path, fin_data)
            data.update(fin_data)

    return data

# Making the parent directory point to our financial data folder
parent = os.getcwd()
parent = os.path.join(parent, 'Financial Data')

def create_folder(stock):
    path = os.path.join(parent, stock)
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
        os.mkdir(parent)
        # I must return the value of path to the parent 
        return create_folder(stock)

# Returns a pandas DataFrame from the csv file
def read_csv(stock, file_name):
    path = os.path.join(parent, stock)
    path = os.path.join(path, file_name)
    return pd.read_csv(path)

# Writes a pandas DataFrame to a csv file
def write_files(path, files):
    for name, data in files.itmes():
        file_name = name + '.csv'
        path = os.path.join(path, file_name)
        data.to_csv(path)
    
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
    df = pd.DataFrame()
    url, attrs, stock = args
    # kw is empty that means we only want to parse the summary page
    if kw == {}:
        # There are no buttons I need to press on this page so no need for selenium
        page = requests.get(url + stock + attrs['stock_key'] + stock)
        soup = BeautifulSoup(page.content, 'html.parser')
        table = soup.find_all('table')
        df = pd.read_html(str(table))
        
    elif kw.get('page') is not None:
        url, attrs, stock, key = args
        # Then I get the driver object and the data table
        driver = webdriver.Chrome('C:\\Users\\karby\\Desktop\\Python Files\\ChromeDriver\\chromedriver')
        driver.get(url + stock + '/' + key + attrs['stock_key'] + stock)
        table = driver.find_element_by_xpath('//*[@id="Col1-1-Financials-Proxy"]/section/div[4]/div[1]/div[1]/div[2]')
        click_buttons(table)
        # Once all of the buttons are pushed I can parse the page
        soup = BeautifulSoup(driver.page_source, 'html.parser')
    
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
        temp = {rows[i // len(cols)] : d.text for i, d in enumerate(data)}

        # The orient (or rows) of my data is stored in the key (or index)
        # Of my dictionary, therefore I just used those values
        df = pd.DataFrame.from_dict(temp, orient='index', columns=cols)
        driver.close()
    else:
        df = wb.DataReader(stock, **kw)
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
