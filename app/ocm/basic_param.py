
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
        # print('File {} found.'.format(filename))
        result = pd.read_csv(my_file)
        # if result.empty:
        #     print('File {} empty.'.format(filename))
        # else:
        #     print('File {} values loaded.'.format(filename))
    else:
        result = pd.DataFrame() 
        # print('File {} NOT found !!!'.format(filename))
    return result
global account_keys_values
global tw_accounts
working_directory = 'E:\\Python\\ocm_project\\app\\ocm_data\\data\\SPX\\'
toImport_directory = working_directory+'ToImport\\'

tw_directory = 'E:\\Python\\ocm_project\\app\\ocm_data\\TW\\SPX\\'
# tw_accounts = {'x2880': 'MB', 'x0197': 'MK'}

ideas_directory = 'E:\\Python\\ocm_project\\app\\ocm_data\\Ideas\\SPX\\'

model_directory_results = 'E:\\Python\\ocm_project\\app\\ocm_data\\ML\\'
managers_directory = 'E:\\Python\\ocm_project\\app\\ocm_data\\Managers\\'
accounts_directory = 'E:\\Python\\ocm_project\\app\\ocm_data\\TradeAccounts\\'
tickerSymbol = "^SPX"
ticker = yf.Ticker(tickerSymbol)
UPDADE_INTERVAL = 5
# load Accounts
accounts = loadcsvtodf(accounts_directory, 'trade_accounts.csv')
tw_accounts = { row["Key"]: row["Value"] for index, row in accounts.iterrows() }
# load AI model
filename1 = 'OCM_ML_XGB_t1.model' #XGB, DTR
loaded1 = pickle.load(open(model_directory_results+filename1, 'rb'))
filename2 = 'OCM_ML_XGB_t1_3.model' #XGB, DTR
loaded2 = pickle.load(open(model_directory_results+filename2, 'rb'))

# pickle.dump(model, open(file_new, 'wb'))
# filename3 = 'OCM_ML_XGB_t1_CBOE_history.model' #XGB, DTR
# loaded3 = pickle.load(open(model_directory_results+filename3, 'rb'))
# filename4 = 'OCM_ML_XGB_t1_3_CBOE_history.model' #XGB, DTR
# loaded4 = pickle.load(open(model_directory_results+filename4, 'rb'))

# model = xgb.Booster()
# filename1 = 'OCM_ML_XGB_t1.model' #XGB, DTR
# loaded1 = model.load_model(model_directory_results + filename1)
# filename2 = 'OCM_ML_XGB_t1_3.model' #XGB, DTR
# loaded2 = model.load_model(model_directory_results + filename2)
# filename1 = 'OCM_ML_XGB_t1.model' #XGB, DTR
# bst = xgb.Booster({'nthread': 4})  # init model
# loaded1 = bst.load_model('E:\\Python\\ocm_project\\app\\ocm_data\\ML\\OCM_ML_XGB_t1.model')

root = 'SPX'  # SPXW = weekly expiration
option_type = 'C'

# RFR
interest_rate = 0.465  # in percentage - meaning 0.1% = 0.1

# lookback period
lookbackperiods = {'1W': 7, '1M': 30, '2M': 60}  # fix 3 pieces, otherwise function createdfiv has to be updated
minstrike = 2100
lookbackperiod_ideas = 60

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

# number of days on quote date slider
qdsliderdays = 20

# higher number will 'push' the ideas color faster
ideacoloraccelerator = 1  

# waiting time for csv's save
time_to_wait = 60

# PM margin
cost_contract = 0  #fix costs (probably 35) per contract, not sure whether exists that's why zero
# rule 1
# worst P/L case in the range
underlying_down = 0.2  #underlying asset down move e.g. 0.2 = 20% ove down scenario
underlying_up = 0.15  #underlying asset up move e.g. 0.15 = 15% move up scenario
# rule 2
naked_coef = 0.003  #default by broker 0.005, formula: naked_coef * underlying_price * naked_contracts * 100
# rule 3 - not used for now
vega_koef = 10 # vega_koef * net vega

# delta limits for inside sort / long / outsideshort
insideshortdeltafrom = 0.65
insideshortdeltato = 0.55
longdeltato = 0.35
outsideshortdeltafrom = 0.20
outsideshortdeltato = 0.10

# New trade 
# optimal delta limits for inside sort / long / outsideshor
newtrade_insideshortdeltafrom = 0.60
newtrade_insideshortdeltato = 0.50
newtrade_longdeltafrom = 0.45
newtrade_longdeltato = 0.35
newtrade_outsideshortdeltafrom = 0.2
newtrade_outsideshortdeltato = 0.1
# default quantity
newtrade_longqty = 20
# outside short iv rank tolerance
newtrade_outsideshort_ivrank_tolerance = -100

# Manage trade formula parameters
vega_opt_abs = 500
vega_opt_rel = -70
delta_opt_abs = -100
delta_opt_rel = 0.8
delta_smooth_max = 10

# dropdowns
delta_drop = ['Delta default','-50','-40','-30','-20','-10','0','10','20','30','40','50']
vega_drop = ['Vega default','-5K','-4K','-3K','-2K','-1K','0','1K','2K','3K','4K','5K','6K','7K','8K','9K','10K']

# colorscale for expiration cycle
bluered_colors, _ = plotly.colors.convert_colors_to_same_type(plotly.colors.sequential.Bluered)
colorscale_bluered = plotly.colors.make_colorscale(bluered_colors)