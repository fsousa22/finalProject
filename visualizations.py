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

def SPCovidPlot(cur, conn):
    ''' This function takes in a cursor and connection. It selects the adjusted close of the S&P 500 stock, the increase
    in Covid-19 cases and the date. It calls the function createLinePlot using the fetched information in the form of
    a list of tuples. It returns nothing. 
    '''
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
    ''' This function takes in a list of tuples containing the date, stock closing price, and daily increase in 
    Covid-19 cases as well as the stock name. It creates a line plot of the stock price vs. Covid-19 daily cases.
    It return nothing. '''
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
    return
    
def abbottCovidPlot(cur, conn):
    ''' This function takes in a cursor and connection. It selects the adjusted close of the Abbott stock, the increase
    in Covid-19 cases and the date. It calls the function createLinePlot using the fetched information in the form of
    a list of tuples. It returns nothing. 
    '''
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
    ''' This function takes in a cursor and connection. It selects the adjusted close of the Delta stock, the increase
    in Covid-19 cases and the date. It calls the function createLinePlot using the fetched information in the form of
    a list of tuples. It returns nothing. 
    '''
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

def Month(cur):
    ''' This function takes in the cursor to our database and retrieves monthly average the adjusted close for all 
    three stocks and Covid-19 positive cases. It will create a table in a csv file with the monthly averages. 
    It returns nothing.'''
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
    ''' This function takes in a cursor to our database and creates a bar chart of the percent change in stock price
    for all three stocks. It returns nothing.'''
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
    ''' This function takes in a cursor to our database and creates a pie chart of the average Covid-19 cases per
    month. This function returns nothing.'''
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
    ''' This function takes in a cursor to our database and creates a line chart of the Covid-19 hospitalizations. 
    This function returns nothing.'''
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
    return


def main():
    ''' This function calls all the above functions.'''
    # Creating database
    cur, conn = setUpDatabase("Data.db")
    # CVS file with monthly averages
    Month(cur)
    # Visualizatons
    SPCovidPlot(cur, conn)
    abbottCovidPlot(cur, conn)
    deltaCovidPlot(cur, conn)
    barChart(cur)
    pieChart(cur)
    hospitalizationsPlot(cur)
    return

if __name__ == '__main__':
    main()
