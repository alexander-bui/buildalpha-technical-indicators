import math, csv, random
import datetime as dt
import numpy as np
import pandas as pd
import talib
import matplotlib.pyplot as plt

## ------------------------------------------------
##  DEFAULT VARIABLES (do not delete them)
##
file_name_base = "D:/Users/alex/TradersToolbox/TradersToolbox/Data/ESRaw.txt"
file_name_market2 = None
file_name_market3 = None
file_name_Vix = None
start = dt.datetime(2017,1,1)
stop  = dt.datetime(2018,1,1)
df1, df2, df3, dfV = None, None, None, None


def iBands(symbol, timeframe, period, deviations, bands_shift, applied_price, mode, shift):
    upperband, middleband, lowerband = talib.BBANDS(
        applied_price, period, deviations, deviations, 0)
    if mode == "MODE_UPPER":
        return upperband
    if mode == "MODE_MAIN":
        return middleband
    if mode == "MODE_LOWER":
        return lowerband


def iMACD(symbol, timeframe, fast_ema_period, slow_ema_period, signal_period, applied_price, mode, shift):
    length = len(applied_price)
    fEMA = talib.EMA(applied_price, fast_ema_period)[0 + shift]
    sEMA = talib.EMA(applied_price, slow_ema_period)[0 + shift]
    return sEMA - fEMA

def iWAE(dataSet, sensitivity, i):
    WAE_MA = iBands(0, 0, 20, 2, 0, dataSet, "MODE_UPPER", 0)[i] - iBands(0, 0, 20, 2, 0, dataSet, "MODE_LOWER", 0)[i]
    Trend = 0
    if(i < len(dataSet) -1):
        Trend = (iMACD(0, 0, 20, 40, 9, dataSet, "MODE_MAIN", i) - iMACD(0, 0, 20, 40, 9, dataSet, "MODE_MAIN", i +1)) * sensitivity
    else:
        Trend = (iMACD(0, 0, 20, 40, 9, dataSet, "MODE_MAIN", i) - iMACD(0, 0, 20, 40, 9, dataSet, "MODE_MAIN", i -1)) * sensitivity
    WAE_Buy = 0
    WAE_Sell = 0
    if Trend >= 0:
        WAE_Buy = Trend
    else:
        WAE_Sell = Trend * -1
    return WAE_Buy

## ------------------------------------------------
##  Read data
##
def ReadData():
        global df1
        df1 = pd.read_csv(file_name_base, delimiter=',', index_col='Date', parse_dates=True)
        df1 = df1[df1.index >= start]
        df1 = df1[df1.index <= stop]

        plt.subplot(2, 1, 1)
        df1['Close'].plot()


## ------------------------------------------------
##  USER VARIABLES and CODE section
##


## ------------------------------------------------
##  CUSTOM INDICATOR FUNCTION
##  (main entry point called from TradersToolbox)
##
def GetCustomSignal():
        ReadData()
        ## -------------------------------------------------
        ## Write signal calculation here
        ##
        ##WAE_MA = iWAE(0, 150)
        ds = df1['Close']
        dataSet = np.array(ds)
        ##WAE_MA, WAE_Buy, WAE_Sell = iWAE(dataSet, 150)
        ##Band1 = iBands(0, 0, 20, 2, 0, dataSet, "MODE_UPPER", 0)[0]
##        for index in dataSet:
##                Signal[index] = iWAE(dataSet,150)

                
        Signal=[]
        Buy = [iWAE(dataSet, 150, index) for index, value in enumerate(dataSet)]
        Signal = [1 if WAEBuy != 0 else 0 for WAEBuy in Buy]

        #print(Signal)

        plt.subplot(2, 1, 2)
        for i in range(len(Signal)):
            #print(Signal[i])
            df1['sig'] = Signal[i]
            print(df1['sig'])
        df1['sig'].plot(label='Signal')

        plt.legend()
        plt.show()   

        ## -------------------------------------------------
        ## Should return list of int (same length as Close)
        ##
        return Signal

if __name__ == "__main__":
    GetCustomSignal()