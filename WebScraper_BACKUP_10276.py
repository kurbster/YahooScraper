# -*- coding: utf-8 -*-
"""
Created on Tue Aug  4 13:37:46 2020

@author: karby
"""

<<<<<<< HEAD
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import os
import requests
import re

def get_fin_data(url, attrs, tickers):
    global stocks, base_url, web_attrs
    base_url = url
    web_attrs = attrs
    stocks = tickers
    fin_data = {}
    # TODO maybe take in a list of pages you want to get
    # i.e data = [financials, balance-sheet, cash-flow] then iterate through that
    for stock in stocks:
        # If we did not create a new folder then read the data
        # Both of these methods return a pd DataFrame
        path = create_folder(stock)
        if not path:
            income_statement = read_csv(stock, 'income.csv')
            balance_sheet    = read_csv(stock, 'balance.csv')
            cash_flow        = read_csv(stock, 'cash.csv')
        else:
            income_statement = parse_page('financials',    stock)
            balance_sheet    = parse_page('balance-sheet', stock)
            cash_flow        = parse_page('cash-flow',     stock)
            write_csv(path, 'income.csv',  income_statement)
            write_csv(path, 'balance.csv', balance_sheet)
            write_csv(path, 'cash.csv',    cash_flow)
        # fin_data is a dict that maps the stock name to another dict 
        # Which maps a string to the DataFrame corresponding to that string
        fin_data[stock] = {'income' : income_statement, 'balance' : balance_sheet
                           , 'cash' : cash_flow}
    return fin_data

# TODO this will be my method for returning the current stock price
# IDK if I should have a time frame or not
def get_stock_data(url, attrs, tickers):
    global stocks, base_url, web_attrs
    base_url = url
    web_attrs = attrs
    stocks = tickers
    for stock in stocks:
        stock_info = parse_page(stock=stock)

# Making the parent directory point to our financial data folder
parent = os.getcwd()
parent = os.path.join(parent, 'Financial Data')

def create_folder(stock):
    path = os.path.join(parent, stock)
=======
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
>>>>>>> V1.1
    # I try to make the folder to store the stock data in
    try:
        os.mkdir(path)
        return path
<<<<<<< HEAD
    # If I get an exception the file already exists
    # Therefore the data is already in there so I return
    # False and read the data in a different method
    except:
        return False

# Returns a pandas DataFrame from the csv file
def read_csv(stock, file_name):
    path = os.path.join(parent, stock)
    path = os.path.join(path, file_name)
    return pd.read_csv(path)

# Writes a pandas DataFrame to a csv file
def write_csv(path, file_name, data):
    path = os.path.join(path, file_name)
    data.to_csv(path)

def parse_page(key, stock):
    # If the key is None then I want to get the front page of the app
    # Which contains the current price of the stock
    if key is None:
        url = base_url + stock + web_attrs['stock_key'] + stock + web_attrs['price_key']
        # There are no buttons I need to press on this page so no need for selenium
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')
        regex = re.compile('W(100%)*')
        table = soup.find_all('table', class_=regex)
        for t in table:
            print(t.text)
    else:
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
        columns = tabl_info.find_all('span')
        
        # This gives me the data table
        tabl = soup.find('div', class_='D(tbrg)')
        data = tabl.find_all('div', {'data-test' : 'fin-col'})
        names = tabl.find_all('span', class_='Va(m)')
       
        # These are the lists and dictionary I will use to create my pd DataFrame
        temp = {}
        rows = []
        cols = []
        # Columns represents the dates we are taking
        for c in columns:
            cols.append(c.text)
        # I pop the first value from this list because it is just a placeholder and I dont need it
        cols.pop(0)
        # Names represents the type of data we are taking
        for n in names:        
            rows.append(n.text)
        
        # Data represents that numbers we are taking in. I am using enumerate
        # Here so I can turn the data into a dictionary 
        for i,d in enumerate(data):
            row_num = i // len(cols)
            # If this is the first entry in a row we have to make the list
            if i % len(cols) == 0:
                temp[rows[row_num]] = [d.text]
            # Otherwise I append the value to the list
            else:
                temp[rows[row_num]].append(d.text)
        
        # The orient (or rows) of my data is stored in the key (or index)
        # Of my dictionary, therefore I just used those values
        df = pd.DataFrame.from_dict(temp, orient='index', columns=cols)
        driver.close()
        return df
    
=======
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

>>>>>>> V1.1

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
