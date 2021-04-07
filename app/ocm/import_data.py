from main_func import *
# import new data from ToImport directory
# import new data from ToImport directory
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

