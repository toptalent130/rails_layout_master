
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
import numpy as np
import zipfile, os
import yfinance as yf
import mibian
import time
import plotly
import pickle
import math
#import matplotlib
from pathlib import Path
from datetime import timedelta
from datetime import datetime
from matplotlib import pyplot as plt
# import xgboost as xgb
# %matplotlib inline
def loadcsvtodf(directory, filename):
    my_file = Path(directory+filename)
    if my_file.is_file():
        print('File {} found.'.format(filename))
        result = pd.read_csv(my_file)
        if result.empty:
            print('File {} empty.'.format(filename))
        else:
            print('File {} values loaded.'.format(filename))
    else:
        result = pd.DataFrame() 
        print('File {} NOT found !!!'.format(filename))
    return result
global tw_accounts
working_directory = '/home/ubuntu/stock-management-django/app/ocm_data/data/SPX/'
toImport_directory = working_directory+'ToImport/'
tw_directory = '/home/ubuntu/stock-management-django/app/ocm_data/TW/SPX/'
# tw_accounts = {'x2880': 'MB', 'x0197': 'MK'}

ideas_directory = '/home/ubuntu/stock-management-django/app/ocm_data/Ideas/SPX/'

model_directory_results = '/home/ubuntu/stock-management-django/app/ocm_data/ML/'
managers_directory = '/home/ubuntu/stock-management-django/app/ocm_data/Managers/'
accounts_directory = '/home/ubuntu/stock-management-django/app/ocm_data/TradeAccounts/'
tickerSymbol = "^SPX"
ticker = yf.Ticker(tickerSymbol)
# load Accounts
accounts = loadcsvtodf(accounts_directory, 'trade_accounts.csv')
tw_accounts = { row["Key"]: row["Value"] for index, row in accounts.iterrows() }
# load AI model
filename1 = 'OCM_ML_XGB_t1.model' #XGB, DTR
loaded1 = pickle.load(open(model_directory_results+filename1, 'rb'))
filename2 = 'OCM_ML_XGB_t1_3.model' #XGB, DTR
loaded2 = pickle.load(open(model_directory_results+filename2, 'rb'))

root = 'SPX'  # SPXW = weekly expiration
option_type = 'C'

# RFR
interest_rate = 0.465  # in percentage - meaning 0.1% = 0.1

# lookback period
lookbackperiods = {'1W': 7, '1M': 30, '2M': 60}  # fix 3 pieces, otherwise function createdfiv has to be updated
minstrike = 2100

# minimum days to expiration
mindte = 100  # for import
mindte_expslider = 150 # for expiration slider

# minimum quote date
# minquotedate = '2018-01-01'

# miaximum quote date in base.csv file to keep the file size small
# maxquotedatebasecsv = '2020-10-01'

# delta range
mindelta =  0.01
maxdelta = 0.7

# minimum days history to show the strike
minstrikehistory = 15

# top open interest expirations
topexp = 5

# waiting time for csv's save
time_to_wait = 60

def savetocsvwithwaiting(df, directory, filename, time_to_wait, mode): 
  # get saving time
    my_file = directory+filename
    header = True
    if Path(my_file).is_file():
        savetime_old = time.ctime(os.path.getmtime(my_file))
    else:
        savetime_old = '1900-01-01'
        mode = 'w'
    if mode == 'a':
        header = False  
    # save
    df.to_csv(my_file, mode=mode, header=header, index=False)
    # wait until saved
    time_counter = 0
    while not Path(my_file).is_file():
        time.sleep(1)
        time_counter += 1
        if time_counter > time_to_wait:break
    if Path(my_file).is_file():
        time_counter = 0
        while savetime_old == time.ctime(os.path.getmtime(my_file)):
            time.sleep(1)
            time_counter += 1
            if time_counter > time_to_wait:break

def getexpmarks(dfhist_rank, quote_date):
    openinterestsum = dfhist_rank.query("quote_date == @quote_date and dte >= @mindte_expslider")[['expiration','type','openinterest']].groupby(['expiration','type'],as_index=False).agg({"openinterest": 'sum'})
    openinterestsum = openinterestsum.sort_values('openinterest', ascending=False).head(topexp)
    result = np.sort(openinterestsum["expiration"])

    return result

def addOwnGreeks(dfbase, source='CBOE', details=True):
    if source == 'CBOE':
        addstr='_1545'
        dfbase = dfbase[['quote_date','expiration','dte','strike','option_type','bid_1545','ask_1545','active_underlying_price_1545','delta_1545','vega_1545','implied_volatility_1545','trade_volume','open_interest']]
    else:
        addstr=''

    colname_underlaying_price = 'active_underlying_price'+addstr
    colname_bid = 'bid'+addstr  
    colname_ask = 'ask'+addstr
  
  # add clomn mid
    dfbase = dfbase.assign(mid = (dfbase[colname_bid]+dfbase[colname_ask])/2)

    # add own greeks...currently calls only !!!
    if details:
        dfbase['implied_volatility_calc'] = dfbase.apply(
            lambda row: mibian.BS([row[colname_underlaying_price], row['strike'], interest_rate, row['dte']], callPrice = row['mid']).impliedVolatility/100, axis = 1
            )
        dfbase['delta_calc'] = dfbase.apply(
            lambda row: mibian.BS([row[colname_underlaying_price], row['strike'], interest_rate, row['dte']], volatility = row['implied_volatility_calc']*100).callDelta, axis = 1
            )
        dfbase['vega_calc'] = dfbase.apply(
            lambda row: mibian.BS([row[colname_underlaying_price], row['strike'], interest_rate, row['dte']], volatility = row['implied_volatility_calc']*100).vega, axis = 1
            )
    
    return dfbase

def calcRank(dfhist, valcurr, colname):
    min=dfhist[colname].min()
    max=dfhist[colname].max()
    if max>min:
        rank=100*(valcurr-min)/(max-min)
    else:
        rank=0 
    return rank

def calcPercentile(dfhist, valcurr, colname):
    if colname =="implied_volatility_calc":
        nrlower = len(dfhist.query("implied_volatility_calc < @valcurr"))
    else:
        nrlower = 0 
    nrall=len(dfhist)
    if nrall>0:
        percentile = 100*nrlower/nrall
    else:
        percentile = 0
    return percentile

def createdfiv(dfbase, dflookback, lookbackperiods=lookbackperiods, mindflookbackentries=minstrikehistory, owngreeks=True):
    if owngreeks:
        addstr='_calc'
    else:
        addstr='_1545'
    colname_iv = 'implied_volatility'+addstr
    colname_delta = 'delta'+addstr
    colname_vega = 'vega'+addstr

    #define dataframe columns
    df_iv = pd.DataFrame(columns=['quote_date', 'expiration', 'dte', 'underlying_price', 'strike','type','mid','iv','delta','vega','volume','openinterest'])
    df_iv = df_iv.reindex(columns=df_iv.columns.append('ivrank_'+pd.Index(lookbackperiods)))
    df_iv = df_iv.reindex(columns=df_iv.columns.append('ivpercentile_'+pd.Index(lookbackperiods)))
    
  #all expirations
    expirations = np.sort(dfbase["expiration"].unique())
    for expiration in expirations:
        df_ec = dfbase.query("expiration == @expiration")
        #all strikes
        strikes = np.sort(df_ec["strike"].unique())
        for strike in strikes:
            df_ec_strike = df_ec.query("strike == @strike")
            # all quote dates
            quote_dates = np.sort(df_ec_strike["quote_date"].unique())
            for quote_date in quote_dates:
                df_ec_strike_qd = df_ec_strike.query("quote_date == @quote_date")
                ivactual = df_ec_strike_qd[colname_iv].values[0]
                if 'active_underlying_price_1545' in df_ec_strike_qd:
                    #CBOE source
                    actual_underlying_price = df_ec_strike_qd['active_underlying_price_1545'].values[0]
                    volume = df_ec_strike_qd['trade_volume'].values[0]
                    openinterest = df_ec_strike_qd['open_interest'].values[0]
                else:
                    actual_underlying_price = df_ec_strike_qd['active_underlying_price'].values[0]
                    volume = df_ec_strike_qd['volume'].values[0]
                    openinterest = df_ec_strike_qd['openInterest'].values[0]
                dfhelp=pd.DataFrame(columns=['ivrank', 'ivpercentile'])
                skipstrike=False
                for key, value in lookbackperiods.items():  #accessing keys and values
                    lookback_date = datetime.strftime(datetime.strptime(quote_date, '%Y-%m-%d') -  pd.to_timedelta(value, unit='d'),'%Y-%m-%d')
                    dflookback_ec_strike = dflookback.query("expiration == @expiration and strike == @strike and quote_date < @quote_date and quote_date >= @lookback_date")
                    if value>=2*mindflookbackentries and len(dflookback_ec_strike)<mindflookbackentries:  #check min strike history requirements
                        skipstrike=True
                    ivrank = calcRank(dflookback_ec_strike,ivactual,colname_iv)
                    ivpercentile = calcPercentile(dflookback_ec_strike,ivactual,colname_iv)
                    dfhelp.loc[len(dfhelp.index)] = [ivrank, ivpercentile]
                
                if skipstrike==False:
                    df_iv.loc[len(df_iv.index)] = [df_ec_strike_qd['quote_date'].values[0], df_ec_strike_qd['expiration'].values[0], df_ec_strike_qd['dte'].values[0],
                                                  actual_underlying_price, strike, df_ec_strike_qd['option_type'].values[0], df_ec_strike_qd['mid'].values[0], ivactual,df_ec_strike_qd[colname_delta].values[0], 
                                                  df_ec_strike_qd[colname_vega].values[0], volume, openinterest,
                                                  dfhelp['ivrank'].values[0], dfhelp['ivrank'].values[1], dfhelp['ivrank'].values[2], 
                                                  dfhelp['ivpercentile'].values[0], dfhelp['ivpercentile'].values[1], dfhelp['ivpercentile'].values[2]
                                                  ]
                              
    return df_iv 

def createdfiv_ec(dfbase, dflookback, colname_iv, lookbackperiods=lookbackperiods, mindflookbackentries=minstrikehistory):
      
    dflookback = pd.concat([dfbase,dflookback], ignore_index=True)

    #define dataframe columns
    df_iv = pd.DataFrame(columns=['quote_date', 'expiration', 'type', 'ivec_basis'])
    df_iv = df_iv.reindex(columns=df_iv.columns.append('ivrank_ec_'+pd.Index(lookbackperiods)))
    
    #all expirations
    expirations = np.sort(dfbase["expiration"].unique())
    for expiration in expirations:
        df_ec = dfbase.query("expiration == @expiration")
        # all quote dates
        quote_dates = np.sort(df_ec["quote_date"].unique())
        for quote_date in quote_dates:
            df_ec_qd = df_ec.query("quote_date == @quote_date")
            ivactual = df_ec_qd[colname_iv].values[0]
            dfhelp=pd.DataFrame(columns=['ivrank'])
            skipqd=False
            for key, value in lookbackperiods.items():  #accessing keys and values
                lookback_date = datetime.strftime(datetime.strptime(quote_date, '%Y-%m-%d') -  pd.to_timedelta(value, unit='d'),'%Y-%m-%d')
                dflookback_ec = dflookback.query("expiration == @expiration and quote_date < @quote_date and quote_date >= @lookback_date")
                if value>=2*mindflookbackentries and len(dflookback_ec)<mindflookbackentries:  #check min strike history requirements
                    skipqd = True
                ivrank = calcRank(dflookback_ec,ivactual,colname_iv)
                dfhelp.loc[len(dfhelp.index)] = [ivrank]
              
            if skipqd==False:
                df_iv.loc[len(df_iv.index)] = [df_ec_qd['quote_date'].values[0], df_ec_qd['expiration'].values[0], df_ec_qd['type'].values[0], ivactual,
                                            dfhelp['ivrank'].values[0], dfhelp['ivrank'].values[1], dfhelp['ivrank'].values[2]]
                              
    return df_iv 

def prepareTrade(dftw, tw=True):
    dftw = dftw.assign(quantity_withsign = dftw['Quantity'])
    dftw.loc[(dftw["Action"].str.contains("SELL")), 'quantity_withsign'] = -1*dftw["Quantity"]
    dftw = dftw.assign(quantity_withsign_realized = dftw['quantity_withsign'],)
    dftw.loc[(dftw["Action"].str.contains("OPEN")), 'quantity_withsign_realized'] = 0 
    dftw = dftw.assign(value_float = dftw['Value'])
    if tw:
        dftw["value_float"] = dftw["value_float"].str.replace(',','')
        dftw["value_float"] = dftw["value_float"].astype('float')
        dftw = dftw.assign(expiration = pd.to_datetime(dftw["Expiration_Date"]).dt.date.astype('str'))
        dftw = dftw.assign(transaction_date = pd.to_datetime(dftw["Date"].str[0:10]).dt.date.astype('str'))
        # set the minimum transaction date as the default for trade start 
        dftw = dftw.assign(trade_start_date = dftw['transaction_date'])
        dftw_exp_mintransactiondate = dftw[['owner','expiration','transaction_date']].groupby(['owner','expiration'],as_index=False).agg({"transaction_date": 'min'})
        for i in dftw_exp_mintransactiondate.itertuples():
            dftw.loc[(dftw['owner']==i.owner) & (dftw['expiration']==i.expiration), 'trade_start_date'] = i.transaction_date
        # update trade start date
        dftw_tradeclosed = pd.DataFrame(columns=['owner', 'expiration', 'trade_close_date'])
        dftw_ow_exp_strike_td = dftw[['owner','expiration','Strike_Price','transaction_date','quantity_withsign']].groupby(['owner','expiration','Strike_Price','transaction_date'],as_index=False).agg({"quantity_withsign": 'sum'})
        for i in dftw_ow_exp_strike_td.itertuples():
            if len(dftw_tradeclosed.query("trade_close_date == @i.transaction_date")) == 0:
                dftw_quantity = dftw_ow_exp_strike_td.query("owner == @i.owner and expiration == @i.expiration and transaction_date <= @i.transaction_date").groupby(['owner','expiration','Strike_Price'], as_index=False).agg({"quantity_withsign": 'sum'}).query("quantity_withsign !=0")
                if len(dftw_quantity) == 0:
                    dftw_tradeclosed.loc[len(dftw_tradeclosed.index)] = [i.owner,i.expiration,i.transaction_date]
        for i in dftw_tradeclosed.itertuples():
            nexttrade_start_date = dftw.query("owner == @i.owner and expiration == @i.expiration and transaction_date > @i.trade_close_date")['transaction_date'].min()
            dftw.loc[(dftw['owner']==i.owner) & (dftw['expiration']==i.expiration) & (dftw['transaction_date']>=nexttrade_start_date), 'trade_start_date'] = nexttrade_start_date
    
    if tw:
        return dftw, dftw_tradeclosed
    else:
        return dftw

# import new data from ToImport directory
def autoload():
    print("Start autoloading into csv files...")
    regenerate = False #set True if dfhist and dfhist_rank should be regenerated
    newimport = False
    dfnewimport=pd.DataFrame()
    os.chdir(toImport_directory)
    for file in os.listdir(toImport_directory):   # get the list of files
        if zipfile.is_zipfile(file): # if it is a zipfile
            with zipfile.ZipFile(file, 'r') as item:  # create Zipfile object and name it item
              #item.extractall()  # extract it in the working directory
              itemlist=item.namelist()
              for name in itemlist:
                  with item.open(name) as csvfile:
                      dfnewimport = pd.concat([dfnewimport,pd.read_csv(csvfile)], ignore_index=True) # all new imported csv's
                      print('New import: file {}.'.format(csvfile.name))
                      newimport = True 
            os.remove(toImport_directory+file)
            print('File {} deleted from ToImport.'.format(file))

        if newimport or regenerate:
            # pre-prepare New import data
            dfnewimport = dfnewimport.query("root == @root and option_type == @option_type and strike >= @minstrike and strike%50 == 0 and bid_1545 > 0 and ask_1545 > 0")
            dfnewimport = dfnewimport.assign(dte = (pd.to_datetime(dfnewimport['expiration']).astype('datetime64[ns]')-pd.to_datetime(dfnewimport['quote_date']).astype('datetime64[ns]')).dt.days)
            # add new imports to dfhist
            dfhistnewimport = dfnewimport.query("dte > @mindte")    # and quote_date >= @minquotedate
            dfhistnewimport = addOwnGreeks(dfbase=dfhistnewimport)
            if regenerate:
                dfhist = dfhistnewimport
            else:
                dfhist = loadcsvtodf(working_directory,'dfhist.csv') # filtered columns + own greeks
                dfhist = pd.concat([dfhist,dfhistnewimport], ignore_index=True)
            savetocsvwithwaiting(dfhist, working_directory, 'dfhist.csv', time_to_wait, 'w')
            print('New imports added to dfhist.csv'+'...SAVED')
            # add new imports to dfhist_rank
            dfhist_ranknewimport = createdfiv(dfhistnewimport, dfhist)
            if regenerate:
                dfhist_rank = dfhist_ranknewimport
            else:
                dfhist_rank = loadcsvtodf(working_directory,'dfhist_rank.csv') # dfhist + ranks + percentiles
                dfhist_rank = pd.concat([dfhist_rank, dfhist_ranknewimport], ignore_index=True)
            savetocsvwithwaiting(dfhist_rank, working_directory, 'dfhist_rank.csv', time_to_wait, 'w')
            print('New imports added to dfhist_rank.csv'+'...SAVED')
            # add new imports to dfhist_ec_rank
            dfhist_ec_ranknewimport = dfhist_ranknewimport[['quote_date','expiration','type','openinterest']].assign(ivec_basis = dfhist_ranknewimport['openinterest']*dfhist_ranknewimport['iv'])
            dfhist_ec_ranknewimport = dfhist_ec_ranknewimport[['quote_date','expiration','type','openinterest','ivec_basis']].groupby(['quote_date','expiration','type'],as_index=False).agg({"openinterest": 'sum',"ivec_basis": 'sum'})
            dfhist_ec_ranknewimport['ivec_basis'] = dfhist_ec_ranknewimport['ivec_basis']/dfhist_ec_ranknewimport['openinterest']
            if regenerate:
                dfhist_ec_rank = dfhist_ec_ranknewimport
            else:
                dfhist_ec_rank = loadcsvtodf(working_directory,'dfhist_ec_rank.csv') # history of expiration cycles IVR
            dfhist_ec_ranknewimport = createdfiv_ec(dfhist_ec_ranknewimport, dfhist_ec_rank, 'ivec_basis')
            if regenerate:  # yes, once again
                dfhist_ec_rank = dfhist_ec_ranknewimport
            else:
                dfhist_ec_rank = pd.concat([dfhist_ec_rank,dfhist_ec_ranknewimport], ignore_index=True)
            savetocsvwithwaiting(dfhist_ec_rank, working_directory, 'dfhist_ec_rank.csv', time_to_wait, 'w')
            print('New imports added to dfhist_ec_rank.csv'+'...SAVED')
        else:
        # load csv's
            dfhist = loadcsvtodf(working_directory,'dfhist.csv') # filtered columns + own greeks
            dfhist_rank = loadcsvtodf(working_directory,'dfhist_rank.csv') # dfhist + ranks + percentiles
            dfhist_ec_rank = loadcsvtodf(working_directory,'dfhist_ec_rank.csv') # history of expiration cycles IVR

    #time measure for if performance fine-tunning necessary
    # t = time.process_time()
    # #action
    # elapsed_time = time.process_time() - t
    # print(elapsed_time)


    # ______________ set sliders ______________
    qdmarks = np.sort(dfhist_rank["quote_date"].unique())
    # add now date if doesn't exist
    now = datetime.today().strftime('%Y-%m-%d')
    if now not in qdmarks:
        qdmarks = np.append(qdmarks, now)

    lastqd = dfhist_rank['quote_date'].max()
    expmarks = getexpmarks(dfhist_rank, lastqd)


# ______________ import real trades ______________

    dftw = pd.DataFrame()
    os.chdir(tw_directory)
    for file in os.listdir(tw_directory):
        if file.endswith(".csv"):
            dfaccount = pd.read_csv(file)
            dfaccount.columns = dfaccount.columns.str.replace(' #','_nr')
            dfaccount.columns = dfaccount.columns.str.replace(' ','_')
            owner = 'unknown'
            for key, value in tw_accounts.items():
                if key in file:
                    owner = value
            dfaccount = dfaccount.assign(owner = owner)
            dftw = pd.concat([dftw,dfaccount], ignore_index=True)
            print('Trades imported from file {}.'.format(file))

    dftw = dftw.query("Expiration_Date != '12/18/20' and Expiration_Date != '9/18/20'")
    dftw, dftw_tradeclosed = prepareTrade(dftw, tw=True)


    # delete old user interface trades, remove ideas files
    trades_filename = 'trades.csv'
    dftrades = loadcsvtodf(ideas_directory,trades_filename) 
    if not dftrades.empty:
        owners = dftw["owner"].unique()
        for owner in owners:
            max_transaction_date = dftw.query("owner == @owner")['transaction_date'].max()
            dftrades = dftrades.query("transaction_date > @max_transaction_date")
        savetocsvwithwaiting(dftrades, ideas_directory, trades_filename, time_to_wait, 'w')
    print("Autoloading done")
    
