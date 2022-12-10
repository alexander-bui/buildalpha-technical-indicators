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
def calcVortex(a,b,c,d):
    tr = np.zeros(len(a))
    vp = np.zeros(len(a))
    vm = np.zeros(len(a))
    trd = np.zeros(len(a))
    vpd = np.zeros(len(a))
    vmd = np.zeros(len(a))

    vpn = np.zeros(len(a))
    vmn = np.zeros(len(a))


    tr[0] = a[0]-b[0]
    for i in range(1,len(a)):
        hl = a[i]-b[i]
        hpc = np.fabs(a[i]-c[i-1])
        lpc = np.fabs(b[i]-c[i-1])
        tr[i] = np.amax(np.array([hl,hpc,lpc]))
        vp[i] = np.fabs(a[i]-b[i-1])
        vm[i] = np.fabs(b[i]-a[i-1])
    for j in range(len(a)-d+1):
        trd[d-1+j] = np.sum(tr[j:j+d])
        vpd[d-1+j] = np.sum(vp[j:j+d])
        vmd[d-1+j] = np.sum(vm[j:j+d])
    
    vpn = vpd/trd
    vmn = vmd/trd
    return vpn,vmn

## ------------------------------------------------
##  CUSTOM INDICATOR FUNCTION
##  (main entry point called from TradersToolbox)
##
def GetCustomSignal():
        ReadData()
        ## -------------------------------------------------
        ## Write signal calculation here
        ##
        df1['Vortex'],df1['VIM'] = calcVortex(df1.iloc[:, 2], df1.iloc[:, 3], df1.iloc[:, 4], 14)
        df1['sig'] = np.where((df1['Vortex'] > df1['VIM']), 1,0)
        
        Signal = [1 if s==1 else 0 for s in zip(df1.sig)]
        
        ## -------------------------------------------------
        ## Should return list of int (same length as Close)
        ##
        return Signal
