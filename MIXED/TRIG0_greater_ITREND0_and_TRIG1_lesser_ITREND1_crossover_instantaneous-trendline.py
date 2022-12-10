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
def calcIT(high, low, alpha):
    data = (high + low) / 2

    ITREND = np.zeros(len(data))
    TRIGGER = np.zeros(len(data))

    # --- get first non nan index
    for i in range(len(data)):

        if np.isnan(data[i]) == False:

            firstNonNan = i
            break

    # --- get last non nan index
    for i in reversed(range(len(data))):

        if np.isnan(data[i]) == False:

            lastNonNan = i
            break

    # --- calculate Voss
    for i in range(len(data)):

        if i < firstNonNan:
            ITREND[i] = np.nan
            TRIGGER[i] = np.nan

        elif i > lastNonNan:
            ITREND[i] = np.nan
            TRIGGER[i] = np.nan

        elif i < firstNonNan + 6:
            ITREND[i] = (data[i]+2*data[i-1]+data[i-2]) / 4

        else:
            ITREND[i] = (alpha-alpha*alpha/4)*data[i] + 0.5*alpha*alpha*data[i-1] - (alpha-0.75*alpha*alpha)*data[i-2] + 2*(1-alpha)*ITREND[i-1] - (1-alpha)*(1-alpha)*ITREND[i-2]

        TRIGGER[i] = 2*ITREND[i]-ITREND[i-2]

    # remove the warm-up values
    for i in range(3 + 1):

        if i <= 3:

            ITREND[i] = np.nan
            TRIGGER[i] = np.nan

    return ITREND, TRIGGER

## ------------------------------------------------
##  CUSTOM INDICATOR FUNCTION
##  (main entry point called from TradersToolbox)
##
def GetCustomSignal():
        ReadData()
        ## -------------------------------------------------
        ## Write signal calculation here
        ##
        df1['ITREND'], df1['TRIGGER'] = calcIT(df1['High'], df1['Low'], 0.07)
        df1['sig'] = np.where((df1['TRIGGER'] > df1['ITREND']) & (df1['TRIGGER'].shift(1) < df1['ITREND'].shift(1)), 1,0)

        Signal = [1 if s==1 else 0 for s in df1.sig]
        
        ## -------------------------------------------------
        ## Should return list of int (same length as Close)
        ##
        return Signal
