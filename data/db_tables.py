# -*- coding: utf-8 -*-
"""
metadata of non-trading data
tables are created acording data's porperties, frequency, usages
- daily
- irregular
- static data
- descriptive data
- quantitative transfomation

bug: fr)
possiable bug: when add foreign constrain

"""

from datetime import  date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (MetaData, Table, Column, Numeric, Integer, BIGINT, String, \
                        Boolean, UnicodeText, Date, ForeignKey, create_engine)

engine = create_engine('mysql://root:911Ljsam@127.0.0.1/stock')
metadata = MetaData()
Base = declarative_base(bind= engine)

#This table stores stock basic infomation
stock_info = Table('stock_info', metadata,
                Column('symbol_id',  String(8), primary_key= True),\
                Column('stock_name',  String(8)),\
                Column('exchange',  String(20)),\
                Column('ipo_date', Date()),\
                Column('sina_industry',  String(100)),\
                Column('sina_concept',  String(100)),\
                Column('sina_area',  String(100)),\
                Column('in_trade', Boolean(), default= False),\
                Column('updated_date', Date(), default= date.today(), onupdate= date.today())\
                )

#This table stores stocks End Of Day (eod) data
stock_eod = Table('stock_eod', metadata,
                #composite primary key [symbol_id, traded_on]
                Column('symbol_id',  String(8), ForeignKey('stock_info.symbol_id'), primary_key= True),                
                Column('stock_name',  String(8)),\
                Column('traded_on', Date(), primary_key= True),\
                #renamming open & close is for avoding clashes with mysql keywords
                Column('open_', Numeric(10,2)),\
                Column('high_', Numeric(10,2)),\
                Column('low_', Numeric(10,2)),\
                Column('close_', Numeric(10,2)),\
                Column('backward_adj_price', Numeric(10,2)),\
                Column('forward_adj_price', Numeric(10,2)),\
                Column('change_', Numeric(30,2)),\
                Column('volume', Integer()),\
                Column('turnover', BIGINT()),\
                Column('turnover_rate', Numeric(10,2)),\
                Column('circulation_value', BIGINT()),\
                Column('total_value', BIGINT()),\
                Column('limit_up', Boolean(), default= False),\
                Column('limit_down',Boolean(), default= False),\
                Column('pe', Numeric(10,2)),\
                Column('ps', Numeric(10,2)),\
                Column('pcf', Numeric(10,2)),\
                Column('pb', Numeric(10,2)),\
                Column('MA_5', Numeric(10,2)),\
                Column('MA_10', Numeric(10,2)),\
                Column('MA_20', Numeric(10,2)),\
                Column('MA_30', Numeric(10,2)),\
                Column('MA_60', Numeric(10,2)),\
                Column('MA_gold_die', String(8)),\
                Column('MACD_DIF', Numeric(10,2)),\
                Column('MACD_DEA', Numeric(10,2)),\
                Column('MACD_MACD', Numeric(10,2)),\
                Column('MACD_gold_die', String(8)),\
                Column('KDJ_K', Numeric(10,2)),\
                Column('KDJ_D', Numeric(10,2)),\
                Column('KDJ_J', Numeric(10,2)),\
                Column('KDJ_gold_die', String(8)),\
                Column('bullin_mid', Numeric(10,2)),\
                Column('bullin_up', Numeric(10,2)),\
                Column('bullin_down', Numeric(10,2)),\
                Column('psy', Numeric(10,2)),\
                Column('psyma', Numeric(10,2)),\
                Column('rsi1', Numeric(10,2)),\
                Column('rsi2', Numeric(10,2)),\
                Column('rsi3', Numeric(10,2))\
                )


#This table stores none-eod data, which generated daily
daily_dfcf = Table('daily_dfcf1', metadata,
                #composite primary key [symbol_id, create_date]
                Column('symbol_id',  String(8), ForeignKey('stock_info.symbol_id'), primary_key= True),\
                Column('create_on', Date(), default= date.today(), primary_key= True),\
                Column('hotness', Integer()),\
                Column('institutional_cost', Numeric(10,2)),\
                #org_participation is a percentage value
                Column('institutional_participation', Numeric(10,2)),\
                #the unit of flow is 10000
                Column('institute_inflow', Integer()),\
                #percent is percentage value
                Column('institute_percent', Numeric(10,2)),\
                Column('megacap_inflow', Integer()),\
                Column('megacap_percent', Numeric(10,2)),\
                Column('large_inflow', Integer()),\
                Column('large_percent', Numeric(10,2)),\
                Column('mid_inflow', Integer()),\
                Column('mid_percent', Numeric(10,2)),\
                Column('small_inflow', Integer()),\
                Column('samll_percent', Numeric(10,2))
                )

#This table describes general infomation about orgnizations
org_info_dfcf = Table('org_info_dfcf', metadata,
                Column('org_name',  String(20), primary_key= True),\
                #influce is rated from 0-5, translated from ******
                #should update it regularly\
                Column('org_influence', Integer()),\
                Column('create_on', Date(), default= date.today()),\
                Column('updated_on', Date(), default= date.today(), onupdate= date.today())
                )


#This table stores reports published by orgnizations, both url and contents
org_report_dfcf = Table('org_report_dfcf', metadata,
                #??assumes each report only binds to ONE org
                Column('report_title', String(200), primary_key= True),\
                Column('publish_date', Date(), primary_key= True),\
                Column('org_name', String(20), ForeignKey('org_info_dfcf.org_name')),\
                Column('report_url',  String(200)),\
                Column('report_body', UnicodeText()),\
                )

#irregularly with a minimum frequency 1day, a web crawler should check it daily
irregular_schedu_dfcf = Table('irregular_scedu_dfcf', metadata,
                #composite primary key [symbol_id, report_title, ]
                Column('symbol_id', String(8), ForeignKey('stock_info.symbol_id'), primary_key= True),\
                Column('report_title', String(200), ForeignKey('org_report_dfcf.report_title'), primary_key= True),
                Column('publish_date', Date()), #ForeignKey('org_report_dfcf.publish_date')),
                Column('grade_name', Integer()),#, ForeignKey('grade_info_dfcf.grade')),\
                Column('grade_change_name', Integer())#, ForeignKey('grade_change_info_dfcf.grade_change'))\
                )

##This table links grade_name to grade, which could used for quantitative processing
#grade_info_dfcf = Table('grade_info_dfcf', metadata,
                #Column('grade_name', String(20), primary_key= True),\
                #Column('grade', Integer(), autoincrement= True)
                #)

##This table links grade_change_name to grade_change, which could used for quantitative processing
#grade_change_info_dfcf = Table('grade_change_info_dfcf', metadata,
                #Column('grade_change_name', String(20), primary_key= True),\
                #Column('grade_change',Integer(), autoincrement= True)#, primary_key= True)
                #)



class Stock_info(Base):
    __table__ = stock_info

class Stock_eod(Base):
    __table__ = stock_eod

class Daily_dfcf(Base):
    __table__ = daily_dfcf

class Org_info_dfcf(Base):
    __table__ = org_info_dfcf  

class Org_report_dfcf(Base):
    __table__ = org_report_dfcf

#class Grade_info_dfcf(Base):
    #__table__ = grade_info_dfcf

#class Grade_change_info_dfcf(Base):
    #__table__ = grade_change_info_dfcf

class Irregular_schedu_dfcf(Base):
    __table__ = irregular_schedu_dfcf

if __name__=='__main__':
    
    metadata.bind = engine
    #grade_info_dfcf.create()
    #grade_change_info_dfcf.create()
    #org_info_dfcf.create()
    #org_report_dfcf.create()
    #irregular_schedu_dfcf.create()
    
    

