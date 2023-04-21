# -*- coding: utf-8 -*-
from jqdatasdk import *
auth('','') # 用户名密码

import numpy as np
import pandas as pd
from datetime import datetime


from jqdatasdk import get_factor_values
from jqdatasdk import get_fundamentals
from jqdatasdk import alpha191

import os
os.chdir(r'') # 指定文件夹

#%% stockCode
stockList = get_index_stocks('000300.XSHG')
#%% tradeDate
tradeDate = get_all_trade_days()
tradeDateDf = pd.DataFrame(tradeDate,columns=['dt']).head(4437).tail(350)
def dt2str(dt1):
    return datetime.strftime(dt1, '%Y-%m-%d')
tradeDateDf['str'] = tradeDateDf['dt'].apply(np.vectorize(dt2str))
tradeDateList = list(tradeDateDf['str'].values)
del tradeDate, tradeDataDf
#%%  alpha191 factor names
num = list(np.arange(1,192,1))
strnum=[]
for ii in num:
    strnum.append(str(int(ii)).zfill(3))
    
strnum.remove('030')
strnum.remove('165')
strnum.remove('183')
del num
#%% download data
for num in strnum:   
    balance = get_query_count()['spare']
    stime = datetime.now()
    df = pd.DataFrame()
    for tradeDate in tradeDateList:
        a= eval('alpha191.alpha_{}(stockList,tradeDate)'.format(num)) # 下载语句
        b = pd.DataFrame(a,columns = ['alpha'+num])
        b.reset_index(drop=False,names='windCode',inplace=True)
        b['tradingDate'] = tradeDate
        b = b[['tradingDate','windCode','alpha'+num]]
        df = pd.concat([df,b],axis=0)
        del a, b
        print(tradeDate)
    print(get_query_count()['spare']-balance)
    print(datetime.now()-stime)
    df.to_csv('alpha{}.csv'.format(num))
    print(num)
#%% data cleansing
filePathList = ['alpha{}.csv'.format(num) for num in strnum]
filePath = 'return.csv'
df = pd.read_csv(filePath,index_col=0)
df.reset_index(drop=True,inplace=True)
df.sort_values(by=['tradingDate','windCode'],inplace=True)
for filePath in filePathList :
    df1 = pd.read_csv(filePath,index_col=0)
    df1.reset_index(drop=True,inplace=True)
    df1.sort_values(by=['tradingDate','windCode'],inplace=True)
    df1.drop(columns = ['tradingDate','windCode'],inplace=True)
    df = pd.concat([df,df1],axis=1)
    print(filePath)
df.rename({'windCode':'stockCode'},inplace=True)
df.to_csv('191.csv')    
    








