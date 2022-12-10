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
def calcRSX(close, length):
    data = close

    f8 = np.zeros(len(data))
    f10 = np.zeros(len(data))
    v8 = np.zeros(len(data))
    f18 = np.zeros(len(data))
    f20 = np.zeros(len(data))
    f28 = np.zeros(len(data))
    f30 = np.zeros(len(data))
    vC = np.zeros(len(data))
    f38 = np.zeros(len(data))
    f40 = np.zeros(len(data))
    v10 = np.zeros(len(data))
    f48 = np.zeros(len(data))
    f50 = np.zeros(len(data))
    v14 = np.zeros(len(data))
    f58 = np.zeros(len(data))
    f60 = np.zeros(len(data))
    v18 = np.zeros(len(data))
    f68 = np.zeros(len(data))
    f70 = np.zeros(len(data))
    v1C = np.zeros(len(data))
    f78 = np.zeros(len(data))
    f80 = np.zeros(len(data))
    v20 = np.zeros(len(data))
    v4 = np.zeros(len(data))

    RSX = np.zeros(len(data))

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

    # --- calculate RSX
    for i in range(len(data)):

        if i < firstNonNan:
            RSX[i] = np.nan
        
        elif i > lastNonNan:
            RSX[i] = np.nan

        else:
            f8[i] = 100.0 * data[i]
            f10[i] = f8[i-1]
            v8[i] = f8[i] - f10[i]

            f18[i] = 3 / (length + 2)
            f20[i] = 1 - f18[i]

            f28[i] = f20[i] * f28[i-1] + f18[i] * v8[i]

            f30[i] = f18[i] * f28[i] + f20[i] * f30[i-1]
            vC[i] = f28[i] * 1.5 - f30[i] * 0.5

            f38[i] = f20[i] * f38[i-1] + f18[i] * vC[i]

            f40[i] = f18[i] * f38[i] + f20[i] * f40[i-1]
            v10[i] = f38[i] * 1.5 - f40[i] * 0.5

            f48[i] = f20[i] * f48[i-1] + f18[i] * v10[i]

            f50[i] = f18[i] * f48[i] + f20[i] * f50[i-1]
            v14[i] = f48[i] * 1.5 - f50[i] * 0.5

            f58[i] = f20[i] * f58[i-1] + f18[i] * abs(v8[i])

            f60[i] = f18[i] * f58[i] + f20[i] * f60[i-1]
            v18[i] = f58[i] * 1.5 - f60[i] * 0.5

            f68[i] = f20[i] * f68[i-1] + f18[i] * v18[i]

            f70[i] = f18[i] * f68[i] + f20[i] * f70[i-1]
            v1C[i] = f68[i] * 1.5 - f70[i] * 0.5

            f78[i] = f20[i] * f78[i-1] + f18[i] * v1C[i]

            f80[i] = f18[i] * f78[i] + f20[i] * f80[i-1]
            v20[i] = f78[i] * 1.5 - f80[i] * 0.5

            if (v20[i] > 0):
                v4[i] = (v14[i] / v20[i] + 1) * 50
            else:
                v4[i] = 50

            if (v4[i] > 100.0):
                RSX[i] = 100.0
            elif (v4[i] < 0.0):
                RSX[i] = 0.0
            else:
                RSX[i] = v4[i]

    #Remove warmup values
    for i in range(3 + 1):

        if i <= 3:

            RSX[i] = np.nan

    return RSX

## ------------------------------------------------
##  CUSTOM INDICATOR FUNCTION
##  (main entry point called from TradersToolbox)
##
def GetCustomSignal():
        ReadData()
        ## -------------------------------------------------
        ## Write signal calculation here
        ##
        df1['RSX'] = calcRSX(df1['Close'], 14)
        df1['sig'] = np.where((df1['RSX'] > 50) & (df1['RSX'].shift(1) < 50), 1,0)
        
        Signal = [1 if s==1 else 0 for s in df1.sig]
        
        ## -------------------------------------------------
        ## Should return list of int (same length as Close)
        ##
        return Signal
