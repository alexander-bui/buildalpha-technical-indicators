import math, csv, random
import datetime as dt
import numpy as np
import pandas as pd
import talib

## ------------------------------------------------
##  DEFAULT VARIABLES (do not delete them)
##
file_name_base = "c:\\ESRaw.txt"
file_name_market2 = None
file_name_market3 = None
file_name_Vix = None
start = dt.datetime(2010,1,1)
stop  = dt.datetime(2011,1,1)
df1, df2, df3, dfV = None, None, None, None

## ------------------------------------------------
##  Read data
##
def ReadData():
        global df1
        df1 = pd.read_csv(file_name_base, delimiter=',', index_col='Date', parse_dates=True)
        df1 = df1[df1.index >= start]
        df1 = df1[df1.index <= stop]

        if file_name_market2 != None and len(file_name_market2) > 0:
                global df2
                df2 = pd.read_csv(file_name_market2, delimiter=',', index_col='Date', parse_dates=True)
                df2 = df2[df2.index >= start]
                df2 = df2[df2.index <= stop]

        if file_name_market3 != None and len(file_name_market3) > 0:
                global df3
                df3 = pd.read_csv(file_name_market3, delimiter=',', index_col='Date', parse_dates=True)
                df3 = df3[df3.index >= start]
                df3 = df3[df3.index <= stop]

        if file_name_Vix != None and len(file_name_Vix) > 0:
                global dfV
                dfV = pd.read_csv(file_name_Vix, delimiter=',', index_col='Date', parse_dates=True)
                dfV = dfV[dfV.index >= start]
                dfV = dfV[dfV.index <= stop]


## ------------------------------------------------
##  USER VARIABLES and CODE section
##
def double_smooth(close, first, second):
        data = close

        first_smooth = data.ewm(first).mean()
        second_smooth = first_smooth.ewm(second).mean()
        return second_smooth


def calcTSI(close, first, second, signal):
        data = close
        pc = data - data.shift(1)

        double_smooth_pc = double_smooth(pc, first, second)
        double_smooth_abs_pc = double_smooth(abs(pc), first, second)
        
        df1['TSI'] = 100 * (double_smooth_pc / double_smooth_abs_pc)
        df1['EMA_TSI'] = df1['TSI'].ewm(signal).mean()

        # Remove warmup values
        for i in range(first + 1):
                if i <= first:
                        df1['TSI'][i] = np.nan
                        df1['EMA_TSI'][i] = np.nan

## ------------------------------------------------
##  CUSTOM INDICATOR FUNCTION
##  (main entry point called from TradersToolbox)
##
def GetCustomSignal():
        ReadData()
        ## -------------------------------------------------
        ## Write signal calculation here
        ##
        calcTSI(df1.iloc[:, 4],25, 13, 13)
        df1['sig'] = np.where((df1['TSI'] > 0), 1,0)        

        Signal = [1 if s==1 else 0 for s in zip(df1.sig)]
        
        ## -------------------------------------------------
        ## Should return list of int (same length as Close)
        ##
        return Signal
