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
def mesaAdaptiveMovingAverage(high, low, fastLimit, slowLimit, warmUpPeriod):
    data = (high + low) / 2
    s = np.zeros(len(data))  # smooth
    d = np.zeros(len(data))  # detrenders
    p = np.zeros(len(data))  # periods
    sp = np.zeros(len(data))  # smoothed periods
    ph = np.zeros(len(data))  # phases
    q1 = np.zeros(len(data))  # q1
    q2 = np.zeros(len(data))  # q2
    i1 = np.zeros(len(data))  # i1
    i2 = np.zeros(len(data))  # i2
    re = np.zeros(len(data))  # re
    im = np.zeros(len(data))  # im

    MAMA = np.zeros(len(data))  # MAMA out
    FAMA = np.zeros(len(data))  # FAMA out

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

    # --- calculate MAMA and FAMA
    for i in range(len(data)):

        if i < firstNonNan:
            MAMA[i] = np.nan
            FAMA[i] = np.nan

        elif i > lastNonNan:
            MAMA[i] = np.nan
            FAMA[i] = np.nan

        elif i > firstNonNan + 4:

            s[i] = (4 * data[i] + 3 * data[i - 1] + 2 * data[i - 2] + data[i - 3]) / 10
            d[i] = (
                0.0962 * s[i]
                + 0.5769 * s[i - 2]
                - 0.5769 * s[i - 4]
                - 0.0962 * s[i - 6]
            ) * (0.075 * p[i - 1] + 0.54)

            # Compute InPhase and Quadrature components
            q1[i] = (
                0.0962 * d[i]
                + 0.5769 * d[i - 2]
                - 0.5769 * d[i - 4]
                - 0.0962 * d[i - 6]
            ) * (0.075 * p[i - 1] + 0.54)
            i1[i] = d[i - 3]

            # Advance the phase of I1 and Q1 by 90 degrees
            ji = (
                0.0962 * i1[i - i]
                + 0.5769 * i1[i - 2]
                - 0.5769 * i1[i - 4]
                - 0.0962 * i1[i - 6]
            ) * (0.075 * p[i - 1] + 0.54)
            jq = (
                0.0962 * q1[i - i]
                + 0.5769 * q1[i - 2]
                - 0.5769 * q1[i - 4]
                - 0.0962 * q1[i - 6]
            ) * (0.075 * p[i - 1] + 0.54)

            # Phasor addition for 3 bar averaging
            _i2 = i1[i] - jq
            _q2 = q1[i] + ji

            # Smooth the I and Q components before applying the discriminator
            i2[i] = 0.2 * _i2 + 0.8 * i2[i]
            q2[i] = 0.2 * _q2 + 0.8 * q2[i]

            # Homodyne Discriminator
            _re = i2[i] * i2[i - 1] + q2[i] * q2[i - 1]
            _im = i2[i] * q2[i - 1] + q2[i] * i2[i - 1]
            re[i] = 0.2 * _re + 0.8 * re[i - 1]
            im[i] = 0.2 * _im + 0.8 * im[i - 1]

            # set period value
            period = 0
            if _im != 0 and _re != 0:
                period = 360 / np.arctan(_im / _re)
            if period > 1.5 * p[-1]:
                period = 1.5 * p[i - 1]
            if period < 0.67 * p[i - 1]:
                period = 0.67 * p[i - 1]
            if period < 6:
                period = 6
            if period > 50:
                period = 50
            p[i] = 0.2 * period + 0.8 * p[i - 1]
            sp[i] = 33 * p[i - 1] + 0.67 * sp[i - 1]

            if i1[i] != 0:
                ph[i] = np.arctan(q1[i] / i1[i])

            # delta phase
            deltaPhase = ph[i - 1] - ph[i]
            if deltaPhase < 1:
                deltaPhase = 1

            # alpha
            alpha = fastLimit / deltaPhase
            if alpha < slowLimit:
                alpha = slowLimit

            # add to output using EMA formula
            MAMA[i] = alpha * data[i] + (1 - alpha) * MAMA[i - 1]
            FAMA[i] = 0.5 * alpha * MAMA[i] + (1 - 0.5 * alpha) * FAMA[i - 1]

    # remove the MAMA and FAMA warm-up values
    for i in range(warmUpPeriod + 1):

        if i <= warmUpPeriod:

            MAMA[i] = np.nan
            FAMA[i] = np.nan

    return MAMA, FAMA

## ------------------------------------------------
##  CUSTOM INDICATOR FUNCTION
##  (main entry point called from TradersToolbox)
##
def GetCustomSignal():
        ReadData()
        ## -------------------------------------------------
        ## Write signal calculation here
        ##
        df1['MAMA'], df1['FAMA'] = mesaAdaptiveMovingAverage(df1['High'], df1['Low'], 0.5, 0.05, 5)
        df1['sig'] = np.where((df1['MAMA'] > df1['FAMA']) & (df1['MAMA'].shift(1) < df1['FAMA'].shift(1)), 1,0)
        Signal = [1 if s == 1 else 0 for s in df1.sig]
        
        ## -------------------------------------------------
        ## Should return list of int (same length as Close)
        ##
        return Signal
