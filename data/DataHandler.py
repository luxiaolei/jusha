
import datetime
import os, os.path
import pandas as pd
import numpy.random as rand
import numpy as np
from abc import ABCMeta, abstractmethod
#from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
import matplotlib.pylab as plt
import db_tables as db
from  db_tables import Stock_eod as eod

def read_data_from_db(symbolid, start_data, end_date, period= None):
    """
    Fetch eod data from db.stock, convert result to dataframe
    within a symbol dictionary

    symbol_data structure: {'sh600001': pd.dataframe,..}
    where the dataframe has index= datetime

    """

    se_sql = select([eod.traded_on, eod.open_, eod.high_, eod.low_,
                     eod.close_, eod.volume, eod.turnover_rate,\
                     eod.MA_5, eod.MA_30, eod.change_, eod.limit_up, eod.limit_down]).where(
                         eod.symbol_id == symbolid)

    #set data start date
    se_sql = se_sql.where(eod.traded_on >= start_data).where(eod.traded_on <= end_date)

    #set data period
    if period != None:
        se_sql = se_sql.limit(period)

    #index is datetime.date obj
    df = pd.read_sql_query(se_sql, db.engine)#, parse_dates= True)
    col = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'TrunOverRate',\
            'MA5', 'MA30', 'Change', 'UP', 'DOWN']
    df.columns = col
    #df.to_csv(symbolid+'.csv', index=False)
    return df


def genReportFilter(reportDate):
    """
    Join Eod data with report df,
    """
    reportDate.sort_values(inplace=True)
    reportDate = reportDate.values

    symbolid = 'sh600005'
    start = reportDate.min()
    end = reportDate.max()
    df = read_data_from_db(symbolid, start, end)

    eodDate = df.ix[:, 0].astype(str).values

    reportFilter = np.empty(eodDate.shape[0])
    for k, ed in enumerate(eodDate):
        condition = reportDate <= ed
        count = condition.sum()
        reportFilter[k] = count

    reportFilterShift = np.roll(reportFilter, 1)
    reportFilterShift[0] = 0
    reportFilter = reportFilter - reportFilterShift

    df['reportFilter'] = reportFilter
    df.to_csv(symbolid+'_'+start+'_'+end+'_Filter.csv',index=False)
    df.to_csv('stock.csv',index=False)
    return df

class GenF:
    """
    Generates features for each ts data, includes:
    1. Dis2low, distance to the lowest price previously, in price
    2. Dis2high, distance to the hightest price previously, in price
    3. VolumeM5, (Volumn- averageVolume_in_past_5_days)/Volume
    4. VolumeVarianceM5, std of volume in past 5 dys.
    5. PriceBandM5, MaxPrice - MinPrice in past 5dys. Positive for increase
    6. inBandM5, -1 for close price below the band, 0 for in, 1 for above
    7. Dis2M5, Close price distance to M5 price
    8. PriceStability, number of trading-days whose priceband(high-low) inclues current days' close price\
        divided by total number of past trading days
    9. TomorrowUp, boolean, indicates will tomorrow limit_up
    10. TomorrowDown, boolean, indicates will tomorrow limit_down
    """
    def __init__(self, df, verbose= True):
        self.df = df
        self.verbose = verbose

    def StartGen(self):
        """
        Generate fetures
        """
        data = np.empty((self.df.shape[0], 8))
        col = ['Dis2low', 'Dis2high', 'VolumeM5', 'VolumeVarianceM5',\
                    'PriceBandM5', 'inBandM5', 'Dis2M5', 'PriceStability']
        for i in self.df.index:
            dfpart = df.ix[:i, :]
            data[i,[0,1]] = self.__Dis2highlow(i, dfpart)
            data[i,[2,3,4,5,6]] = self.__M5(i, dfpart)
            data[i,7] = self.__PriceStability(i, dfpart)
        newdf = pd.DataFrame(data, columns = col)

        self.__GenInfoLeakF()


        return self.df.join(newdf)



    def __Dis2highlow(self, index, dfpart):
        """
        1. Dis2low, distance to the lowest price previously, in price
        2. Dis2high, distance to the hightest price previously, in price
        """
        lowest = dfpart.Close.min()
        hightest = dfpart.High.max()
        Dis2high = hightest - dfpart.High[index]
        Dis2low = dfpart.Low[index] - lowest
        return (Dis2high, Dis2low)

    def __M5(self, index, dfpart):
        """
        3. VolumeM5, (Volumn- averageVolume_in_past_5_days)/Volume
        4. VolumeVarianceM5, std of volume in past 5 dys.
        5. PriceBandM5, MaxPrice - MinPrice in past 5dys. Positive for increase
        6. inBandM5, -1 for close price below the band, 0 for in, 1 for above
        7. Dis2M5, Close price distance to M5 price
        """
        if index>= 5:
            dfpast5 = dfpart.ix[index-5:index-1, :]
            assert dfpast5.shape[0] == 5
            Vmean, VolumeVarianceM5 = dfpast5.Volume.mean(), dfpast5.Volume.std()
            VolumeM5 = dfpart.Volume[index] - Vmean
            #5, 6
            Hi, Lo = dfpast5.High.values, dfpast5.Low.values
            MaxPrice, MinPrice = Hi.max(), Lo.min()
            if Hi.argmax() >= Lo.argmin():
                #increasing
                PriceBandM5 = MaxPrice - MinPrice
            else:
                PriceBandM5 = MinPrice - MaxPrice
            currentPrice = dfpart.Close[index]
            if currentPrice <= MinPrice:
                inBandM5 = -1
            elif currentPrice >= MaxPrice:
                inBandM5 = 1
            else:
                inBandM5 = 0
            #7
            Dis2M5 = currentPrice - dfpart.MA5[index]


            return (VolumeM5, VolumeVarianceM5, PriceBandM5, inBandM5, Dis2M5)
        else:
            return (dfpart.Volume[index], 0, dfpart.Close[index]*.2, 0, 0)

    def __PriceStability(self, index, dfpart):
        """
        8. PriceStability, number of trading-days whose priceband(high-low) inclues current days' close price
        """
        cp = dfpart.Close[index]
        if index > 100:
            dfpast = dfpart.ix[: index-1, :]
            PriceStability = dfpast.ix[(dfpast.High> cp) &\
                                       (dfpast.Low< cp)].shape[0]
            return float(PriceStability) / dfpart.shape[0]
        else:
            #the first 100 points contains too large error
            return 0.02

    def __GenInfoLeakF(self):
        """
        Geneates features that possiablely leak infomation about feature
        """
        self.df['UP'] = self.df['UP'].astype(int)
        self.df['DOWN'] = self.df['DOWN'].astype(int)
        self.df['TomorrowUp'] = self.df['UP'].shift(-1)
        self.df['TomorrowDown'] = self.df['DOWN'].shift(-1)
        upmask, downmask = self.df.Change >= 0.05 , self.df.Change <= -0.05
        upmask, downmask = upmask.astype(int), downmask.astype(int)
        self.df['TomorrowUp_5percent'] = upmask.shift(-1)
        self.df['TomorrowDown_5percent'] = downmask.shift(-1)

        self.df = self.df.fillna(0)





if __name__ == '__main__':
    reportDate = pd.read_csv('600005report.csv').ix[:,1].dropna()
    df = genReportFilter(reportDate)
    newdf = GenF(df)
    newdf = newdf.StartGen()
    newdf['TimeIndex'] = newdf.index
    newdf.to_csv("newdftest.csv",index=False)
