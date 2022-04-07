from calendar import c
import sqlite3
import os
import matplotlib.pyplot as plt
import numpy as np
from queue import Empty
from unittest import result
from xml.sax import parseString
from bs4 import BeautifulSoup
import requests
import re
import os
import csv
import unittest

def retriveCovidData():
    pass


def retrieveSPData():
    pass

def retrieveAbbottData():
    r = requests.get('https://finance.yahoo.com/quote/ABT/history?period1=1577836800&period2=1609372800&interval=1d&filter=history&frequency=1d&includeAdjustedClose=true') 
    soup = BeautifulSoup(r.content, "html.parser")
    
    closeData = []
    rows = soup.find_all('tr', class_ = 'BdT Bdc($seperatorColor) Ta(end) Fz(s) Whs(nw)')
    
    for row in rows:
        dateLocation = row.find_all('td', class_ = 'Py(10px) Ta(start) Pend(10px)')
        date = dateLocation[0].text.strip()
        stock = row.find_all('td', class_ = 'Py(10px) Pstart(10px)')
        if len(stock) == 6:
            price = stock[4].text.strip()
            closeData.append((date, price))
    
    return closeData


def retrieveDeltaData():
    pass

def SPCovidPlot():
    SPData = retrieveSPData
    pass

def abbottCovidPlot():
    pass

def deltaCovidPlot():
    pass


class TestCases(unittest.TestCase):
    def testAbbott(self):
        self.assertEqual(len(retrieveAbbottData()), 256)
