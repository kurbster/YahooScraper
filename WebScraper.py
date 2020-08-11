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
#from pandas_datareader import data as wb

'''
    get_fin_data will get the financial data for the specific stock passed in
    First it will get all of the historic financial data right now that means 
    Income statement, balance sheet, and cash flow statement.
        
        To save time everytime I read a page from yahoo finance I save
        The resulting DataFrame to a csv. Then if the csv exists I just read
        That instead of creating a new selenium driver object.
'''

def get_fin_data(url, attrs, stock, **kw):
    fin_data = {}
    # TODO maybe take in a list of pages you want to get
    # i.e data = [financials, balance-sheet, cash-flow] then iterate through that
    
    # If the path wasn't created then just read the csv
    path = create_folder(stock)
    if not path:
        income_statement = read_csv(stock, 'income.csv')
        balance_sheet    = read_csv(stock, 'balance.csv')
        cash_flow        = read_csv(stock, 'cash.csv')
    else:
        #Here I have to pass in the specific page I want to parse
        income_statement = parse_page(stock, url, attrs, 'financials')
        balance_sheet    = parse_page(stock, url, attrs, 'balance-sheet')
        cash_flow        = parse_page(stock, url, attrs, 'cash-flow')
        write_csv(path, 'income.csv',  income_statement)
        write_csv(path, 'balance.csv', balance_sheet)
        write_csv(path, 'cash.csv',    cash_flow)
    
    
    fin_data[stock] = {'income'   : income_statement, 
                       'balance'  : balance_sheet,
                       'cash'     : cash_flow, 
                       'CurrentP' : parse_page(stock, url, attrs)
                       }
    return fin_data

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
def write_csv(path, file_name, data):
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

def parse_page(stock, *args):
    if len(args) == 2:
        url, attrs = args
        # There are no buttons I need to press on this page so no need for selenium
        page = requests.get(url + stock + attrs['stock_key'] + stock)
        soup = BeautifulSoup(page.content, 'html.parser')
        table = soup.find_all('table')
        df = pd.read_html(str(table))
    elif len(args) == 3:
        url, attrs, key = args
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
        temp = {}
        rows = [n.text for n in names]      # Names of the data we're taking
        cols = [c.text for c in columns]    # Names of the columns
        # I pop the first value from this list because it is just a placeholder and I dont need it
        cols.pop(0)
        
        # Data represents that numbers we are taking in. I am using enumerate
        # Here so I can turn the data into a 2D array and have the corresponding
        # Row names for that data
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
