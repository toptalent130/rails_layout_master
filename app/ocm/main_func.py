
from basic_param import *

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

def get_continuous_color(colorscale, intermed):
  """
  Plotly continuous colorscales assign colors to the range [0, 1]. This function computes the intermediate
  color for any value in that range.

  Plotly doesn't make the colorscales directly accessible in a common format.
  Some are ready to use:
  
      colorscale = plotly.colors.PLOTLY_SCALES["Greens"]

  Others are just swatches that need to be constructed into a colorscale:

      viridis_colors, scale = plotly.colors.convert_colors_to_same_type(plotly.colors.sequential.Viridis)
      colorscale = plotly.colors.make_colorscale(viridis_colors, scale=scale)

  :param colorscale: A plotly continuous colorscale defined with RGB string colors.
  :param intermed: value in the range [0, 1]
  :return: color in rgb string format
  :rtype: str
  """
  if len(colorscale) < 1:
      raise ValueError("colorscale must have at least one color")

  if intermed <= 0 or len(colorscale) == 1:
      return colorscale[0][1]
  if intermed >= 1:
      return colorscale[-1][1]

  for cutoff, color in colorscale:
      if intermed > cutoff:
          low_cutoff, low_color = cutoff, color
      else:
          high_cutoff, high_color = cutoff, color
          break

  # noinspection PyUnboundLocalVariable
  return plotly.colors.find_intermediate_color(
      lowcolor=low_color, highcolor=high_color,
      intermed=((intermed - low_cutoff) / (high_cutoff - low_cutoff)),
      colortype="rgb")

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

def getcurrchain(expiration, option_type, quote_date):
  chain = pd.DataFrame()  #necessary???
  if option_type == 'C':
    chain = ticker.option_chain(expiration).calls[['strike','lastPrice','lastTradeDate','volume','bid','ask','openInterest','impliedVolatility']]
  else:
    if option_type == 'P':
      chain = ticker.option_chain(expiration).puts[['strike','lastPrice','lastTradeDate','volume','bid','ask','openInterest','impliedVolatility']]
  
  chain = chain.assign(option_type=option_type)
  chain = chain.assign(quote_date=quote_date)
  chain = chain.assign(expiration=expiration)
  
  # Underlaying asset additional info
  actual_underlying_price = ticker.history(period='1d')['Close'].values[0]
  chain = chain.assign(active_underlying_price=actual_underlying_price)

  return chain



def getTradeStatusPL(dftw_ow_ec_qd, iv_ec):
      
  tw_status_price_open = dftw_ow_ec_qd['value_float'].sum()
  
  dftw_status_ow_ec_qd = dftw_ow_ec_qd.query("quantity_withsign != 0")
  tw_status = iv_ec.iloc[np.where(iv_ec.strike.isin(np.sort(dftw_status_ow_ec_qd["Strike_Price"].unique())))]
  tw_status = pd.merge(tw_status,dftw_status_ow_ec_qd, how='left',left_on=['strike'],right_on=['Strike_Price'])   
  tw_status_price_qd = (100*tw_status['mid']*tw_status['quantity_withsign']).sum()
  
  tw_status_PL_qd = tw_status_price_qd + tw_status_price_open
  
  return tw_status_PL_qd, tw_status

def getIdeaStatusPL(owner, expiration, quote_date, lasttrade_close_date, dftwideas, iv_ec_current, dfhist_rank_ec):
      
  iv_ec = dfhist_rank_ec.query("quote_date == @quote_date")
  if iv_ec.empty:
    iv_ec = iv_ec_current
  dftw_ow_ec_qd = dftwideas.query("owner == @owner and expiration == @expiration and transaction_date <= @quote_date and transaction_date >= @lasttrade_close_date")[['owner','Strike_Price','trade_start_date','value_float','quantity_withsign']].groupby(['owner','Strike_Price','trade_start_date'],as_index=False).agg({"value_float": 'sum', "quantity_withsign": 'sum'})

  tw_status_PL_qd, tw_status = getTradeStatusPL(dftw_ow_ec_qd, iv_ec)  
  
  return tw_status_PL_qd

def getRealizedStrikePL(owner, expiration, strike, action, quantity_withsign_realized, value_float, transaction_date, trade_start_date, dftw):
  action_search = ''
  if action == 'BUY_TO_CLOSE':
    action_search = 'SELL_TO_OPEN'
  else:
    if action == 'SELL_TO_CLOSE':
      action_search = 'BUY_TO_OPEN'
  
  dfsum = dftw.query("owner == @owner and expiration == @expiration and Strike_Price == @strike and Action == @action_search and transaction_date <= @transaction_date and transaction_date >= @trade_start_date")[['value_float','Quantity']].sum()
  if dfsum.Quantity !=0:
    avg_price = dfsum.value_float/dfsum.Quantity
    realizedStrikePL = (quantity_withsign_realized*avg_price).round(0)
    realizedStrikePL = realizedStrikePL + value_float
  else:
    realizedStrikePL = 0

  return realizedStrikePL

def getexpirationprice(option_type, uderlying_price, strike):
  expiration_price = 0
  if option_type == 'C':
    if uderlying_price > strike:
      expiration_price = uderlying_price - strike
  if option_type == 'P':
    if uderlying_price < strike:
      expiration_price = strike - uderlying_price

  return expiration_price

def addivfrommodel(underlying_price, tw_status, iv_colname):
  tw_status = tw_status.assign(strike_underlying_price = underlying_price)
  tw_status = tw_status.assign(price_1 = 100*(tw_status['strike_underlying_price']-tw_status['underlying_price'])/tw_status['underlying_price'])
  tw_status.reset_index(inplace = True, drop = True) # to be able to make join with AI predictions
  columns=['dte','iv','delta','vega','ivrank_1M', 'ivrank_2M','ivrank_1W','price_1'] 
  # note: dte decrease not applied as it is neglectable
  X = tw_status[columns]
  X['dte'] = X['dte'].astype(int)
  preds1 = loaded1.predict(X)
  preds2 = loaded2.predict(X)
  #  XX = X.drop(["ivrank_1M","ivrank_2M","ivrank_1W"], axis = 1)
  #  preds3 = loaded3.predict(XX)
  #  preds4 = loaded4.predict(XX)
  preds = (preds1+preds2)/2
  tw_status = tw_status.join(pd.DataFrame(data = preds, columns = [iv_colname]))

  return tw_status

def getTradePL(underlying_price, tw_status, dftw_ow_ec_qd, iv_colname='iv', exp=False):
  owner = tw_status['owner'].values[0]
  expiration = tw_status['expiration'].values[0]
  quote_date = tw_status['quote_date'].values[0]
  trade_start_date = tw_status['trade_start_date'].values[0]
  option_type = tw_status['type'].values[0]

  tw_status_price_open = dftw_ow_ec_qd['value_float'].sum()
  
  # AI
  if iv_colname == 'iv_model':
    tw_status = addivfrommodel(underlying_price, tw_status, iv_colname)

  if exp:
    tw_status['mid_PL'] = tw_status.apply(
        lambda row: getexpirationprice(option_type, underlying_price, row["strike"]), axis=1
        )
  else:
    if option_type == 'C':
      tw_status['mid_PL'] = tw_status.apply(
          lambda row: mibian.BS([underlying_price, row['strike'], interest_rate, row['dte']], volatility = row[iv_colname]*100).callPrice, axis = 1
          )
    else:
      if option_type == 'P':
        tw_status['mid_PL'] = tw_status.apply(
            lambda row: mibian.BS([underlying_price, row['strike'], interest_rate, row['dte']], volatility = row[iv_colname]*100).putPrice, axis = 1
            )

  tw_price_qd = (100*tw_status['mid_PL']*tw_status['quantity_withsign']).sum()
  tw_PL_qd = tw_price_qd + tw_status_price_open
  
  return tw_PL_qd

def getTradeGreek(underlying_price, tw_status, greek, iv_colname='iv'):
    
  # AI
  if iv_colname == 'iv_model':
    tw_status = addivfrommodel(underlying_price, tw_status, iv_colname)

  if greek == 'vega':
    tw_status['vega_trade'] = tw_status.apply(
        lambda row: mibian.BS([underlying_price, row['strike'], interest_rate, row['dte']], volatility = row[iv_colname]*100).vega, axis = 1
        )
  
  if greek == 'delta':
    if option_type == 'C':
      tw_status['delta_trade'] = tw_status.apply(
          lambda row: mibian.BS([underlying_price, row['strike'], interest_rate, row['dte']], volatility = row[iv_colname]*100).callDelta, axis = 1
          )
    else:
      if option_type == 'P':
        tw_status['delta_trade'] = tw_status.apply(
            lambda row: mibian.BS([underlying_price, row['strike'], interest_rate, row['dte']], volatility = row[iv_colname]*100).putDelta, axis = 1
            )     

  tw_greek = (100*tw_status[greek+'_trade']*tw_status['quantity_withsign']).sum()
  
  return tw_greek

def getPortfolioMarginRequirement(underlying_price, iv_ec, naked_contracts, total_contracts, pl='pl_theoretical'):
  # min of 2 rules
  # rule 1 ... with strike simplification which doesn't hurt at all...
  strike_min = iv_ec['strike'].min()
  strike_min = max(strike_min, underlying_price * (1-underlying_down))
  strike_down = iv_ec.query("strike <= @strike_min")['strike'].max()
  strike_max = iv_ec['strike'].max()
  strike_max = min(strike_max, underlying_price * (1+underlying_up))
  strike_up = iv_ec.query("strike >= @strike_max")['strike'].min()
  margin_r1 = iv_ec.query("strike >= @strike_down and strike <= @strike_up")[pl].min()
  margin_r1 = margin_r1 - total_contracts * cost_contract
  # rule 2
  margin_r2 = naked_coef * underlying_price * naked_contracts * 100  - total_contracts * cost_contract

  margin = abs(min(margin_r1, margin_r2))
  
  return margin

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

def getStrikeMid(strike, dfsource):
  mid = dfsource.query("strike == @strike")['mid'].values[0]
  return mid

def adaptIdeas(dfideas, dftw):
  owner = dfideas["owner"].to_numpy()
  quantity = dfideas["quantity"].to_numpy()
  strike = dfideas["Strike_Price"].to_numpy()
  action = dfideas["Action"].to_numpy()
  price = dfideas["price"].to_numpy()

  dfideasadapted = pd.DataFrame(columns=['owner', 'quantity', 'Strike_Price', 'Action', 'price'])

  for i, s in enumerate(strike):
    q = quantity[i]
    quantity_open = dftw.query('Strike_Price == @s')['quantity_withsign'].sum()
    if action[i] == 'BUY':
      dftw.loc[len(dftw.index)] = [s, q]
      quantity_to_close = max(0, q - max(0, quantity_open + q))
      if quantity_to_close > 0:
        dfideasadapted.loc[len(dfideasadapted.index)] = [owner[i], quantity_to_close, s, 'BUY_TO_CLOSE', price[i]]
      quantity_to_open = q - quantity_to_close
      if quantity_to_open > 0:
        dfideasadapted.loc[len(dfideasadapted.index)] = [owner[i], quantity_to_open, s, 'BUY_TO_OPEN', price[i]]
    else:
      dftw.loc[len(dftw.index)] = [s, (-1)*q]
      quantity_to_close = max(0, q + min(0, quantity_open - q))
      if quantity_to_close > 0:
        dfideasadapted.loc[len(dfideasadapted.index)] = [owner[i], quantity_to_close, s, 'SELL_TO_CLOSE', price[i]]
      quantity_to_open = q - quantity_to_close
      if quantity_to_open > 0:
        dfideasadapted.loc[len(dfideasadapted.index)] = [owner[i], quantity_to_open, s, 'SELL_TO_OPEN', price[i]]

  return dfideasadapted

def prepareTradeFromIdeas(dfideas, quote_date, expiration, trade_start_date, iv_ec, ideatype, historicalprice=False):
  dfideas = dfideas.query("quantity>0 and Strike_Price>0")
  now = str(datetime.now().isoformat())
  dfideas = dfideas.assign(Date=now, Type=ideatype, Symbol='SPX', Instrument_Type='Equity Option', Description='NA', 
                           Commission=0.0, Fees=0.0, Multiplier=100, Underlying_Symbol='SPX', Expiration_Date='NA',
                           Call_or_Put='CALL', Order_nr=100000000, transaction_date=quote_date, expiration=expiration, trade_start_date=trade_start_date,
                           )
  
  dfideas["Quantity"] = dfideas["quantity"].astype('int') 
  
  #Set Price
  if historicalprice:
    dfideas['Average_Price'] = dfideas.apply(
        lambda row: 100*getStrikeMid(row["Strike_Price"], iv_ec), axis=1
        )
  else:
    dfideas['Average_Price'] = dfideas.apply(
        lambda row: 100*row["price"] if row["price"]>0 else 100*getStrikeMid(row["Strike_Price"], iv_ec), axis=1
    )
  dfideas.loc[(dfideas["Action"].str.contains("BUY")), 'Average_Price'] = -1*dfideas["Average_Price"]

  dfideas = dfideas.assign(Value=dfideas['Average_Price']*dfideas['Quantity'])
  dfideas = dfideas.assign(value_float=dfideas['Value'])

  dfideas = prepareTrade(dfideas, tw=False)

  dfideas = dfideas.drop(['quantity', 'price'], axis = 1) 
  
  return dfideas

def getzone(delta):
  if delta>insideshortdeltafrom:
    return 'zone1'
  elif delta>insideshortdeltato:
    return 'zone2'
  elif delta>longdeltato:
    return 'zone3'
  elif delta>outsideshortdeltafrom:
    return 'zone4'
  elif delta>outsideshortdeltato:
    return 'zone5'
  return 'zone6'

def getoptstrike(df, deltamax, deltamin, strike=0, ls='long', col='ivrank_1M'):
  optstrike = strike
  if optstrike == 0:
    if ls == 'short':
      optstrike = df[df[col]==df.query("delta <= @deltamax and delta >= @deltamin and strike%100 == 0")[col].max()]['strike'].values[0]
    else:
      optstrike = df[df[col]==df.query("delta <= @deltamax and delta >= @deltamin and strike%100 == 0")[col].min()]['strike'].values[0]

  delta = df.query("strike == @optstrike")['delta'].values[0]
  vega = df.query("strike == @optstrike")['vega'].values[0]
  mid = df.query("strike == @optstrike")['mid'].values[0]
  mid = mid.round(2)
  ivrank = df.query("strike == @optstrike")['ivrank_1M'].values[0]
  zone = getzone(delta)

  return optstrike, delta, vega, mid, ivrank, zone

# ______________ Chart Dash Func ______________

def splitideaintoacceptableratios(dfselected):
  dfsplit = pd.DataFrame()
  if not dfselected.empty:
    dfselected = dfselected.drop(['delta', 'vega', 'strike'], axis = 1)
    dfselected = dfselected.rename(columns={'input-quantity': 'Qty', 'input-strike': 'Strike', 'dropdown-action': 'Action', 'input-price': 'Price'})
    dfselected['db/cr'] = dfselected.apply(
        lambda row: 'db' if row["Action"]=='BUY' else 'cr', axis=1)
    dfselected = dfselected.query("Qty > 0 and Strike !=''")  
  if not dfselected.empty:
    dfsplit = pd.DataFrame(columns=dfselected.columns)
    dfbuy = dfselected.query("Action == 'BUY' and Qty > 0").sort_values(by=['Strike']) 
    dfsell = dfselected.query("Action == 'SELL' and Qty > 0").sort_values(by=['Strike'])
    while not (dfbuy.empty and dfsell.empty):
      dfbuy.reset_index(inplace = True, drop = True)
      dfsell.reset_index(inplace = True, drop = True)
      if not dfbuy.empty:
        buy_r1_qty = dfbuy.head(1)['Qty'].values[0].astype(int)
        buy_r1_price = dfbuy.head(1)['Price'].values[0].round(2)
        buy_r1_strike = dfbuy.head(1)['Strike'].values[0]
        if not dfsell.empty:
          sell_r1_qty = dfsell.head(1)['Qty'].values[0].astype(int)
          sell_r1_price = dfsell.head(1)['Price'].values[0].round(2)
          sell_r1_strike = dfsell.head(1)['Strike'].values[0]
          if buy_r1_qty > sell_r1_qty:
            spread_ratio = buy_r1_qty//sell_r1_qty
            if spread_ratio > 3:
              spread_ratio = 3
            sell_qty = sell_r1_qty
            buy_qty = spread_ratio * sell_qty
          else:
            spread_ratio = sell_r1_qty//buy_r1_qty
            if spread_ratio > 3:
              spread_ratio = 3
            buy_qty = buy_r1_qty
            sell_qty = spread_ratio * buy_qty
          lots = math.gcd(buy_qty, sell_qty)  
          spread_price = (buy_r1_price * buy_qty - sell_r1_price * sell_qty)/lots
          spread_price = spread_price.round(2)
          if spread_price>0:
            dbcr = 'db'
          else:
            dbcr='cr'
            spread_price = abs(spread_price)
          if buy_r1_strike < sell_r1_strike:
            dfsplit.loc[len(dfsplit.index)] = [buy_qty, buy_r1_strike, 'BUY', '', '']
            dfsplit.loc[len(dfsplit.index)] = [sell_qty, sell_r1_strike, 'SELL', spread_price, dbcr]
          else:
            dfsplit.loc[len(dfsplit.index)] = [sell_qty, sell_r1_strike, 'SELL', '', ''] 
            dfsplit.loc[len(dfsplit.index)] = [buy_qty, buy_r1_strike, 'BUY', spread_price, dbcr]
        else:
          buy_qty = buy_r1_qty
          sell_qty = 0
          dfsplit.loc[len(dfsplit.index)] = [buy_qty, buy_r1_strike, 'BUY', buy_r1_price, 'db']
      else:
        sell_r1_qty = dfsell.head(1)['Qty'].values[0].astype(int)
        sell_r1_price = dfsell.head(1)['Price'].values[0].round(2)
        sell_r1_strike = dfsell.head(1)['Strike'].values[0]
        sell_qty = sell_r1_qty 
        buy_qty = 0
        dfsplit.loc[len(dfsplit.index)] = [sell_qty, sell_r1_strike, 'SELL', sell_r1_price, 'cr']

      if buy_qty > 0:
        dfbuy.at[0,'Qty'] = buy_r1_qty-buy_qty
      if sell_qty > 0:
        dfsell.at[0,'Qty'] = sell_r1_qty-sell_qty

      dfbuy = dfbuy.query("Action == 'BUY' and Qty > 0").sort_values(by=['Strike'])
      dfsell = dfsell.query("Action == 'SELL' and Qty > 0").sort_values(by=['Strike'])

    if not dfsplit.empty:
      dfsplit['Qty'] = dfsplit.apply(
          lambda row: -row['Qty'] if row["Action"]=='SELL' else row['Qty'], axis=1)

  return dfsplit

def SetColorTWStatus(x):
  if x >= 0:
    return "green"
  else:
    return "red"