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

# TODO:
'''
- 25 or fewer restriction
- read in from api not downloaded json file
'''


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
    cur.execute("CREATE TABLE IF NOT EXISTS Abbott (date DATE PRIMARY KEY, month INTEGER, adjClose FLOAT(2))")
    conn.commit()
    for row in data:
        date = row[1].split('-')
        month = int(date[1])
        cur.execute("INSERT OR IGNORE INTO Abbott (date, month, adjClose) VALUES (?, ?, ?)",(row[1], month, row[0]))
    conn.commit()
    return

def deltaToDB(data, cur, conn):
    cur.execute("CREATE TABLE IF NOT EXISTS Delta (date DATE PRIMARY KEY, month INTEGER, adjClose FLOAT(2))")
    conn.commit()
    for row in data:
        date = row[1].split('-')
        month = int(date[1])
        cur.execute("INSERT OR IGNORE INTO Delta (date, month, adjClose) VALUES (?, ?, ?)",(row[1], month, row[0]))
    conn.commit()
    return

def SPToDB(data, cur, conn):
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

def SPCovidPlot(cur, conn):
    cur.execute(
        '''
        SELECT SP500.adjClose, SP500.date, Covid.positive_inc
        FROM SP500
        JOIN Covid ON SP500.date = Covid.date
        '''
    )
    res = cur.fetchall()
    createLinePlot(res, "S&P 500")

    return

def createLinePlot (res, name):
    yStock = []
    yCovid = []
    x = []
    for mon in reversed(res):
        yStock.append(mon[0])
        yCovid.append(mon[2])
        x.append(mon[1])

    fig, ax1 = plt.subplots() 
  
    ax1.set_xlabel('Date') 
    ax1.set_ylabel('Daily Stock Price') 
    ax1.plot(x, yStock, color = 'red') 
  
    ax2 = ax1.twinx() 
    ax2.plot(x, yCovid, color = 'blue')
    plt.ylabel('Daily Covid-19 Cases')
    ax1.legend([name], loc = "upper left")
    ax2.legend(["New Covid-19 Cases"], loc = "lower right")
    ax1.xaxis.set_ticks(["2020-01-14", "2020-05-14", "2020-09-14", "2020-12-30"])
    plt.title("Covid-19 Cases vs. Stock Price in 2020")
    plt.tight_layout()

    plt.show()
    


def abbottCovidPlot(cur, conn):
    cur.execute(
        '''
        SELECT Abbott.adjClose, Abbott.date, Covid.positive_inc
        FROM Abbott
        JOIN Covid ON Abbott.date = Covid.date
        '''
    )
    res = cur.fetchall()
    createLinePlot(res, "Abbott")
    return

def deltaCovidPlot(cur, conn):
    cur.execute(
        '''
        SELECT Delta.adjClose, Delta.date, Covid.positive_inc
        FROM Delta
        JOIN Covid ON Delta.date = Covid.date
        '''
    )
    res = cur.fetchall()
    
    createLinePlot(res, "Delta")
    return

def Month(cur, conn):
    cur.execute(
        '''
        SELECT Abbott.month, AVG(Covid.positive_inc), AVG(Abbott.adjClose), AVG(Delta.adjClose), AVG(SP500.adjClose)
        FROM Abbott
        JOIN Covid JOIN Delta JOIN SP500 ON Covid.month = Abbott.month AND Delta.month = Abbott.month AND SP500.month = Abbott.month 
        GROUP BY Abbott.month
        '''
    )
    res = cur.fetchall()

    fout = open("Monthly_Data.csv", "w")
    writer = csv.writer(fout)

    headerRow = ["Month", "Covid-19 Daily Average", "Abbott Average Closing Price", "Delta Average Closing Price", "S&P500 Average Closing Price"]
    writer.writerow(headerRow)
    for month in res:
        cases = round(month[1], 2)
        abbott = round(month[2], 2)
        delta = round(month[3], 2)
        sp = round(month[4], 2)
        writer.writerow([month[0], cases, abbott, delta, sp])
    
    fout.close()
    return

def barChart(cur):
    cur.execute(
        '''
        SELECT Delta.adjClose, SP500.adjClose, Abbott.adjClose
        FROM Delta
        JOIN SP500 JOIN Abbott ON Delta.date = SP500.date AND Delta.date = Abbott.date
        '''
    )
    res = cur.fetchall()
    Dfirst, SPfirst, Abbottfirst = res[-1]
    Dend, SPend, Abbottend = res[0]
    Dinc = (Dend - Dfirst) / Dfirst * 100
    SPinc = (SPend - SPfirst) / SPfirst * 100
    Ainc = (Abbottend - Abbottfirst) / Abbottfirst * 100

    plt.bar(["Delta", "S&P 500", "Abbott"], [Dinc, SPinc, Ainc])
    plt.ylabel("Percent Change")
    plt.xlabel("Stock")
    plt.title("Percent Increase of Stocks in 2020")
    plt.tight_layout()
    plt.show()

def pieChart(cur):
    cur.execute(
        '''
        SELECT AVG(Covid.positive_inc)
        FROM Covid
        GROUP BY Covid.month
        '''
    )
    res = cur.fetchall()
    cases = []
    for mon in res:
        cases.append(mon[0])

    months = ["Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    plt.pie(cases[2:], labels=months)
    plt.title("Average Covid-19 Cases per Month in 2020")
    plt.show()

def hospitalizationsPlot(cur):
    cur.execute(
        '''
        SELECT Covid.hospitalized_cur, Covid.date
        FROM Covid
        '''
    )
    res = cur.fetchall()
    y = []
    x = []
    for mon in reversed(res):
        y.append(mon[0])
        x.append(mon[1])

    plt.plot(x, y)

    plt.xticks(["2020-01-14", "2020-05-14", "2020-09-14", "2020-12-30"])
    plt.title("Current Hospitalizations due to Covid-19 in 2020")
    plt.tight_layout()

    plt.show()


def main():
    cur, conn = setUpDatabase("Data.db")
    CovidDatatoDB(retrieveDictfromData('Covid.json'), cur, conn)
    abbottToDB(retrieveData("Abbott.html"), cur, conn)
    deltaToDB(retrieveData("Delta.html"), cur, conn)
    SPToDB(retrieveData("S&P.html"), cur, conn)
    Month(cur, conn)
    SPCovidPlot(cur, conn)
    abbottCovidPlot(cur, conn)
    deltaCovidPlot(cur, conn)
    barChart(cur)
    pieChart(cur)
    hospitalizationsPlot(cur)


class TestCases(unittest.TestCase):
    def testGetData(self):
        self.assertEqual(len(retrieveData("Abbott.html")), 252)
        self.assertEqual(len(retrieveData("S&P.html")), 252)
        self.assertEqual(len(retrieveData("Delta.html")), 252)
    
    def testDatabase(self):
        self.cur, self.conn = setUpDatabase('Data.db')
        self.data = retrieveDictfromData('Covid.json')
        CovidDatatoDB(self.data, self.cur, self.conn)

        self.dataAb = retrieveData("Abbott.html")
        abbottToDB(self.dataAb, self.cur, self.conn)

        self.dataDelta = retrieveData("Delta.html")
        deltaToDB(self.dataDelta, self.cur, self.conn)

        self.dataSP = retrieveData("S&P.html")
        SPToDB(self.dataSP, self.cur, self.conn)

    def testPlots(self):
        self.cur, self.conn = setUpDatabase('Data.db')
        abbottCovidPlot(self.cur, self.conn)
        Month(self.cur, self.conn)
        

if __name__ == '__main__':
    main()
    # unittest.main(verbosity=2)