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

def retrieveDictfromData(): 
    ''' This function takes in a filename, find the file and loads the json content and 
    returns a list of dictionaries with the json content'''
    try:
        resp = requests.get("https://api.covidtracking.com/v1/us/daily.json")
        json = resp.json()
    except:
        print("error reading in from url")
        json = []
    return json

def CovidDatatoDB(data, cur, conn):
    ''' This function takes in a cursor, connection, and the loaded in json content in a list of dictionaries. 
    It then adds the Covid-19 data to our database and returns nothing'''
    cur.execute("CREATE TABLE IF NOT EXISTS Covid (date DATE PRIMARY KEY, month INTEGER, positive INTEGER, positive_inc INTEGER, hospitalized_cur INTEGER)")
    conn.commit()
    for row in data:
        date = str(row['date'])
        day = date[-2:]
        month = date[4:6]
        year = date[0:4]
        if year != '2020':
            continue
        date = year + '-' + month + '-' + day
        cur.execute("INSERT OR IGNORE INTO Covid (date, month, positive, positive_inc, hospitalized_cur) VALUES (?,?,?,?,?)",(date, month, row['positive'],row['positiveIncrease'],row['hospitalizedCurrently']))
    conn.commit()
    return

def main():
    ''' This function calls all the above functions.'''
    # Creating database
    cur, conn = setUpDatabase("Data.db")
    CovidDatatoDB(retrieveDictfromData('Covid.json'), cur, conn)
    return


class TestCases(unittest.TestCase):
    def testDatabase(self):
        self.cur, self.conn = setUpDatabase('Data.db')
        self.data = retrieveDictfromData()
        CovidDatatoDB(self.data, self.cur, self.conn)
        

if __name__ == '__main__':
    main()
    # unittest.main(verbosity=2)
