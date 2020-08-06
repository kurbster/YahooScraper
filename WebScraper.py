# -*- coding: utf-8 -*-
"""
Created on Tue Aug  4 13:37:46 2020

@author: karby
"""

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
  
def get_stock_data(url, attrs, tickers):
    global stocks, base_url, web_attrs
    base_url = url
    web_attrs = attrs
    stocks = tickers
    for stock in stocks:
        stock_info = parse_page(stock=stock)

parent = 'C:\\Users\\karby\\Desktop\\Python Files\\Finance\\Trading\\YahooScraper\\Financial Data\\'
def create_folder(stock):
    path = os.path.join(parent, stock)
    # I try to make the folder to store the stock data in
    try:
        os.mkdir(path)
        return path
    # If I get an exception the file already exists
    # Therefore the data is already in there so I return
    # False and read the data in a different method
    except:
        return False

def read_csv(stock, file_name):
    path = os.path.join(parent, stock)
    path = os.path.join(path, file_name)
    return pd.read_csv(path)

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
