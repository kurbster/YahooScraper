# -*- coding: utf-8 -*-
"""
Created on Tue Sep 15 14:08:12 2020

@author: karby

This file is basic and is the file that will handle out Input/Output
"""

import os
import pandas as pd
import numpy as np
from bs4 import Tag


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
    try:
        return pd.read_csv(os.path.join(path, name))
    except FileNotFoundError:
        raise BaseException('This directory did not have the proper files and need to be deleted')

def write_files(path, files, ext='.csv'):
    for name, data in files.items():
        data.to_csv(os.path.join(path, name + ext))
        
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