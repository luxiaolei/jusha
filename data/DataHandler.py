
import datetime
import os, os.path
import pandas as pd
import numpy.random as rand
import numpy as np
from abc import ABCMeta, abstractmethod
#from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

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
                     eod.close_, eod.volume]).where(
                         eod.symbol_id == symbolid)

    #set data start date
    se_sql = se_sql.where(eod.traded_on >= start_data).where(eod.traded_on <= end_date)

    #set data period
    if period != None:
        se_sql = se_sql.limit(period)

    #index is datetime.date obj
    df = pd.read_sql_query(se_sql, db.engine)#, parse_dates= True)
    col = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
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


if __name__ == '__main__':
    reportDate = pd.read_csv('600005report.csv').ix[:,1].dropna()
    df = genReportFilter(reportDate)
