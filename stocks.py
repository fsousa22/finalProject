from calendar import c
import sqlite3
import os
from tkinter import Y
import matplotlib.pyplot as plt
import matplotlib.dates as mdate
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
import io
import sys
import json


def setUpDatabase(db_name): 
    ''' This funct takes in the database name and finds the database or creates a database and 
    return the cursor and the connection'''
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def retrieveData(filename):
    ''' This function takes in the filename of a html file and converts the information from the html to a list
    with the date and stock price. It returns the list of tuples with the stock data.'''
    with open(filename) as fp:
        soup = BeautifulSoup(fp, "html.parser")
    
    closeData = []
    rows = soup.find_all('tr', class_ = 'BdT Bdc($seperatorColor) Ta(end) Fz(s) Whs(nw)')
    
    for row in rows:
        dateLocation = row.find_all('td', class_ = 'Py(10px) Ta(start) Pend(10px)')
        if len(dateLocation) != 0:
            dateUnformat = dateLocation[0].text.strip()
            dateUnformat = dateUnformat.split()
            month = monthNumber(dateUnformat[0])
            date = dateUnformat[2] + '-' + month + '-' + dateUnformat[1].strip(',')

            stock = row.find_all('td', class_ = 'Py(10px) Pstart(10px)')
            price = stock[4].text.strip()
            closeData.append((price, date))
    
    return closeData

def abbottToDB(data, cur, conn):
    ''' This function takes in the data in the format of a list of tuples containing the date and closing stock price.
    It then creates and adds this information to the Abbott table in the database. It returns nothing.'''
    cur.execute("CREATE TABLE IF NOT EXISTS Abbott (date DATE PRIMARY KEY, month INTEGER, adjClose FLOAT(2))")
    conn.commit()
    for row in data:
        date = row[1].split('-')
        month = int(date[1])
        cur.execute("INSERT OR IGNORE INTO Abbott (date, month, adjClose) VALUES (?, ?, ?)",(row[1], month, row[0]))
    conn.commit()
    return

def deltaToDB(data, cur, conn):
    ''' This function takes in the data in the format of a list of tuples containing the date and closing stock price.
    It then creates and adds this information to the Delta table in the database. It returns nothing.'''
    cur.execute("CREATE TABLE IF NOT EXISTS Delta (date DATE PRIMARY KEY, month INTEGER, adjClose FLOAT(2))")
    conn.commit()
    for row in data:
        date = row[1].split('-')
        month = int(date[1])
        cur.execute("INSERT OR IGNORE INTO Delta (date, month, adjClose) VALUES (?, ?, ?)",(row[1], month, row[0]))
    conn.commit()
    return

def SPToDB(data, cur, conn):
    ''' This function takes in the data in the format of a list of tuples containing the date and closing stock price.
    It then creates and adds this information to the S&P 500 table in the database. It returns nothing.'''
    cur.execute("CREATE TABLE IF NOT EXISTS SP500 (date DATE PRIMARY KEY, month INTEGER, adjClose FLOAT(2))")
    conn.commit()
    for row in data:
        date = row[1].split('-')
        month = int(date[1])
        stock = row[0].replace(',', "")
        cur.execute("INSERT OR IGNORE INTO SP500 (date, month, adjClose) VALUES (?, ?, ?)",(row[1], month, stock))
    conn.commit()
    return

def monthNumber(month):
    ''' This function takes in the month name as a string and returns the month number as a string.'''
    if month == 'Jan': 
        return '01'
    if month == 'Feb': 
        return '02'
    if month == 'Mar': 
        return '03'
    if month == 'Apr': 
        return '04'
    if month == 'May': 
        return '05'
    if month == 'Jun': 
        return '06'
    if month == 'Jul': 
        return '07'
    if month == 'Aug': 
        return '08'
    if month == 'Sep': 
        return '09'
    if month == 'Oct': 
        return '10'
    if month == 'Nov': 
        return '11'
    if month == 'Dec': 
        return '12'

def main():
    ''' This function calls all the above functions.'''
    # Creating database
    cur, conn = setUpDatabase("Data.db")
    abbottToDB(retrieveData("Abbott.html"), cur, conn)
    deltaToDB(retrieveData("Delta.html"), cur, conn)
    SPToDB(retrieveData("S&P.html"), cur, conn)
    return

class TestCases(unittest.TestCase):
    def testGetData(self):
        self.assertEqual(len(retrieveData("Abbott.html")), 252)
        self.assertEqual(len(retrieveData("S&P.html")), 252)
        self.assertEqual(len(retrieveData("Delta.html")), 252)
    
    def testDatabase(self):
        self.cur, self.conn = setUpDatabase('Data.db')

        self.dataAb = retrieveData("Abbott.html")
        abbottToDB(self.dataAb, self.cur, self.conn)

        self.dataDelta = retrieveData("Delta.html")
        deltaToDB(self.dataDelta, self.cur, self.conn)

        self.dataSP = retrieveData("S&P.html")
        SPToDB(self.dataSP, self.cur, self.conn)
        

if __name__ == '__main__':
    main()
    # unittest.main(verbosity=2)
