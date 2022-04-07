from calendar import c
import sqlite3
import os
#import matplotlib.pyplot as plt
#import numpy as np
from queue import Empty
from unittest import result
from xml.sax import parseString
from bs4 import BeautifulSoup
import requests
import re
import os
import csv
import unittest
import json

def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def retrieveDictfromData(fileName):
    try:
        source_dir = os.path.dirname(__file__)
        full_path = os.path.join(source_dir, fileName)
        file = open(full_path, 'r')
        contents = file.read()
        file.close()
        data = json.loads(contents)
    except:
        print("error when reading from file")
        data = []
    return data

def CovidDatatoDB(data, cur, conn):
    cur.execute("CREATE TABLE IF NOT EXISTS Covid (date INTEGER PRIMARY KEY, positive INTEGER, positive_inc INTEGER, hospitalized_cur INTEGER)")
    conn.commit()
    for day in data:
        cur.execute("INSERT OR IGNORE INTO Covid (date, positive, positive_inc, hospitalized_cur) VALUES (?,?,?,?)",(day['date'],day['positive'],day['positiveIncrease'],day['hospitalizedCurrently']))
    conn.commit()


def retrieveData(filename):
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
    cur.execute("CREATE TABLE IF NOT EXISTS Abbott (date DATE PRIMARY KEY, adjClose FLOAT(2))")
    conn.commit()
    for day in data:
        cur.execute("INSERT OR IGNORE INTO Abbott (date, adjClose) VALUES (?, ?)",(day[1], day[0]))
    conn.commit()

def deltaToDB(data, cur, conn):
    cur.execute("CREATE TABLE IF NOT EXISTS Delta (date DATE PRIMARY KEY, adjClose FLOAT(2))")
    conn.commit()
    for day in data:
        cur.execute("INSERT OR IGNORE INTO Delta (date, adjClose) VALUES (?, ?)",(day[1], day[0]))
    conn.commit()

def SPToDB(data, cur, conn):
    cur.execute("CREATE TABLE IF NOT EXISTS SP500 (date DATE PRIMARY KEY, adjClose FLOAT(2))")
    conn.commit()
    for day in data:
        cur.execute("INSERT OR IGNORE INTO SP500 (date, adjClose) VALUES (?, ?)",(day[1], day[0]))
    conn.commit()


def monthNumber(month):
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

def SPCovidPlot():
    SPData = retrieveData("S&P.html")
    pass

def abbottCovidPlot():
    abbott = retrieveData("Abbott.html")
    pass

def deltaCovidPlot():
    delta = retrieveData("Delta.html")
    pass


class TestCases(unittest.TestCase):
    def testGetData(self):
        self.assertEqual(len(retrieveData("Abbott.html")), 252)
        self.assertEqual(len(retrieveData("S&P.html")), 252)
        self.assertEqual(len(retrieveData("Delta.html")), 252)
    
    def testDatabase(self):
        cur, conn = setUpDatabase('Data.db')
        self.data = retrieveDictfromData('Covid.json')
        CovidDatatoDB(self.data,cur,conn)

        self.dataAb = retrieveData("Abbott.html")
        abbottToDB(self.dataAb, cur, conn)

        self.dataDelta = retrieveData("Delta.html")
        deltaToDB(self.dataDelta, cur, conn)

        self.dataSP = retrieveData("S&P.html")
        SPToDB(self.dataDelta, cur, conn)
        



if __name__ == '__main__':
    unittest.main(verbosity=2)