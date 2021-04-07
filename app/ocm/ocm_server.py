from jupyter_dash import JupyterDash
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from django_plotly_dash import DjangoDash
from dash.dependencies import Input, Output, State, MATCH, ALL
import plotly.graph_objects as go
#import plotly.express as px
from plotly.subplots import make_subplots
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from import_data import *

# app = DjangoDash('ocm_graph')

# ______________ basic parameters and loads ______________
# in basic_param.py file

# ______________ main functions ______________
# in main_func.py file

# import new data from ToImport directory
# in import_data.py file

# ______________ Chart Dash ______________

empty_row = dbc.Label(html.P(""))
qd_calendar = dbc.Form(
    [
     dcc.DatePickerSingle(
     id='calendar-qd',
     min_date_allowed=qdmarks[0],
     max_date_allowed=qdmarks[len(qdmarks)-1],
     date=qdmarks[len(qdmarks)-2],
     display_format='MMM D, YYYY',
     # number_of_months_shown = 3 
     )
    ]
)

qd_slider = dbc.Form(
    [
        # dbc.Label("Quote Date"),
        dcc.Slider(
                  id='slider-qd',
                  marks={int(i):j[-2:]+'.'+j[5:7] for i,j in zip(range(len(qdmarks)), qdmarks)},
                  min=len(qdmarks)-qdsliderdays,
                  max=len(qdmarks)-1,
                  value=len(qdmarks)-2,
                  step=None,
                  updatemode='drag',
                  included=False,
                  vertical=False,
                  verticalHeight=450,
        )
    ]
)

exp_dropdown = dbc.Form(
    [
     dcc.Dropdown(
     id='dropdown-exp',
     # options=[{'label':exp[5:7]+'/'+exp[:4], 'value':exp} for exp in expmarks],
     options=[{'label':exp, 'value':exp} for exp in expmarks],
     value = expmarks[-1],
     disabled=True,
     clearable=False,
     style={
     'minWidth': '125px', 
     'fontSize': "115%",
     'minHeight': '48px',
     },
     )
    ]
)

exp_slider = dbc.Form(
    [
        # dbc.Label("Expiration"),
        dcc.Slider(
                  id='slider-exp',
                  marks={int(i):j[5:7]+'/'+j[:4] for i,j in zip(range(len(expmarks)), expmarks)},
                  min=0,
                  max=len(expmarks)-1,
                  value=len(expmarks)-1,
                  step=None,
                  updatemode='drag',
                  included=False,
                  vertical=False,
                  verticalHeight=400
        )
    ]
)

iv_checklist = dbc.Checklist(
    id='checklist-iv',
    options=[
        {'label': 'Open Interest', 'value': 'OI'},
        {'label': 'Volume', 'value': 'VOL'},
        {'label': 'IV Percentile', 'value': 'IVP'},
    ],
    value=['OI'],
    inline=True,
)  

rank_checklist = dbc.Checklist(
    id='checklist-rank',
    options=[
        {'label': '1W', 'value': '1W'},
        {'label': '1M', 'value': '1M'},
        {'label': '2M', 'value': '2M'},
    ],
    value=['1M'],
    inline=True,
)

dayaction_radioitems = dbc.FormGroup(
    [
     dbc.Label("Day Action:", html_for="example-radios-row"),
     dbc.Col(
         dbc.RadioItems(
             id='radioitems-dayaction',
             options=[
                      {'label': 'None', 'value': 'none'},
                      {'label': 'Realized', 'value': 'realized'},
                      {'label': 'All', 'value': 'all'},
                      ],
             value='all',
             inline=True,
         ),
     ),
    ],
    row=True,
)

ideas_container = dbc.Spinner(
    id="loading-container-ideas",
    color="secondary",
    children=[
              dash_table.DataTable(
                  id='container-ideas',
                  css=[{"selector": ".Select-menu-outer", "rule": "display: block !important"}],
                  columns=[
                           {'id': 'input-quantity', 'name': 'Qty', 'type': 'numeric'},
                           {'id': 'input-strike', 'name': 'Strike', 'type': 'numeric'},
                           {'id': 'dropdown-action', 'name': 'Action', 'presentation': 'dropdown', 'type': 'text'},
                           {'id': 'input-price', 'name': 'Price', 'type': 'numeric'},
                           {'id': 'delta', 'name': 'Delta', 'type': 'numeric'},
                           {'id': 'vega', 'name': 'Vega', 'type': 'numeric'},
                           {'id': 'strike', 'name': 'Strike-check', 'type': 'numeric'},
                  ],
                  dropdown={
                      'dropdown-action': {
                          'options': [{'label': i, 'value': i} for i in ['BUY', 'SELL']],
                      }
                  },
                  data=[],
                  sort_action="native",
                  # sort_mode="multi",
                  row_selectable="multi",
                  editable=True,
                  row_deletable=True,
                  selected_rows=[],
                  page_action="native",
                  page_current= 0,
                  page_size= 10,
                  # style_as_list_view=True,
                  style_header={
                      'backgroundColor': 'rgb(50, 50, 50)',
                      'fontWeight': 'bold',
                      'color': 'white',
                  },
                  style_cell={
                      # 'backgroundColor': 'rgb(30, 30, 30)',
                      'backgroundColor': 'rgb(225, 250, 250)',
                      'color': 'black',
                      'textAlign': 'center',
                      'minWidth': 65, 'maxWidth': 65, 'width': 65
                      # 'padding': '5px'
                  },
                  style_data_conditional=[
                      {
                          'if': {'row_index': 'odd'},
                          # 'backgroundColor': 'rgb(40, 40, 40)'
                          'backgroundColor': 'rgb(240, 250, 250)'
                      }
                  ],
                  style_cell_conditional=[
                      {
                       'if': {'column_id': c},
                       'display': 'none' } for c in ['delta', 'vega', 'strike']
                  ]
              ),]
)

ideas_container_selected = dash_table.DataTable(
    id='container-ideas-selected',
    css=[{"selector": ".Select-menu-outer", "rule": "display: block !important"}],
    columns=[
             {'id': 'input-quantity', 'name': 'Qty', 'type': 'numeric'},
             {'id': 'input-strike', 'name': 'Strike', 'type': 'numeric'},
             {'id': 'dropdown-action', 'name': 'Action', 'presentation': 'dropdown', 'type': 'text'},
             {'id': 'input-price', 'name': 'Price', 'type': 'numeric'},
             {'id': 'delta', 'name': 'Delta', 'type': 'numeric'},
             {'id': 'vega', 'name': 'Vega', 'type': 'numeric'},
             {'id': 'strike', 'name': 'Strike-check', 'type': 'numeric'},
    ],
    dropdown={
        'dropdown-action': {
            'options': [{'label': i, 'value': i} for i in ['BUY', 'SELL']],
        }
    },
    data=[],
    sort_action="native",
    # sort_mode="multi",
    row_selectable="multi",
    editable=True,
    row_deletable=True,
    selected_rows=[],
    page_action="native",
    page_current= 0,
    page_size= 10,
    # style_as_list_view=True,
    style_header={
        'backgroundColor': 'rgb(50, 50, 50)',
        'fontWeight': 'bold',
        'color': 'white',
    },
    style_cell={
        # 'backgroundColor': 'rgb(30, 30, 30)',
        'backgroundColor': 'rgb(225, 250, 250)',
        'color': 'black',
        'textAlign': 'center',
        'minWidth': 65, 'maxWidth': 65, 'width': 65
        # 'padding': '5px'
    },
    style_data_conditional=[
        {
            'if': {'row_index': 'odd'},
            # 'backgroundColor': 'rgb(40, 40, 40)'
            'backgroundColor': 'rgb(240, 250, 250)'
        }
    ],
    style_cell_conditional=[
        {
          'if': {'column_id': c},
          'display': 'none' } for c in ['delta', 'vega', 'strike']
    ]
),

update_button = dbc.Button(
    "UPDATE",
    id="update",
    n_clicks=0,
    size="sm",
    color="warning",
    disabled=True,
    style={"margin":4}
)

ideas_buttons = html.Div(
    [
      dbc.Button(
      "Clear All",
      id="clear-all",
      n_clicks=0,
      outline=True,
      size="md",
      color="danger",
      style={"margin":4}
    ),
    dbc.Button(
        "Add Row",
        id="add-row",
        n_clicks=0,
        outline=True,
        size="md",
        color="primary",
        style={"margin":4}
    ),
    dbc.FormGroup(
        [
        dcc.Dropdown(
        id='dropdown-delta',
        options=[{'label':delta, 'value':delta} for delta in delta_drop],
        value = delta_drop[0],
        clearable=False,
        style={
        'minWidth': '120px', 
        'fontSize': "100%",
        "margin": 4
        #  'max-height': '30px',
        },
        ),
        dcc.Dropdown(
        id='dropdown-vega',
        options=[{'label':vega, 'value':vega} for vega in vega_drop],
        value = vega_drop[0],
        clearable=False,
        style={
        'minWidth': '120px', 
        'fontSize': "100%",
        "margin": 4
        #  'max-height': '30px',
        },
        ),
        dbc.Button(
            "Propose Action",
            id="propose-action",
            n_clicks=0,
            outline=True,
            size="md",
            color="primary",
            style={"margin":4}
        ),
        dbc.Button(
            "Show Split",
            id="show-split",
            n_clicks=0,
            outline=True,
            size="md",
            color="info",
            style={"margin":4}
        ),
        dbc.Popover(
            [
            dbc.PopoverBody(id="table-split"),
            ],
            id='popover-split',
            target="show-split",
            is_open=False,
            placement='top',
        ),
        ],
        check = True,
        inline = True,
    ),
    dbc.Button(
        "Show Split Closing",
        id="show-splitclose",
        n_clicks=0,
        outline=True,
        size="md",
        color="info",
        style={"margin":4}
    ),
    dbc.Popover(
        [
        dbc.PopoverBody(id="table-splitclose"),
        ],
        id='popover-splitclose',
        target="show-splitclose",
        is_open=False,
        placement='top',
    ),
    ],
    style={"marginLeft": "20%"}
)

project_button = dbc.Button(
    "Project Selection",
    id="project-ideas",
    n_clicks=0,
    # outline=True,
    size="md",
    color="secondary",
    style={"margin":4}
)

apply_button = dbc.Button(
    "Apply Selection",
    id="apply-ideas",
    n_clicks=0,
    # outline=True,
    size="md",
    color="success",
    style={"margin":4},
    disabled="true"
)

trades_info_buttons = html.Div(
    [
     dbc.Button(
         "Trades List",
         id="show-tradeslist",
         n_clicks=0,
        #  outline=True,
         size="sm",
         color="info",
         style={"margin":4}
      ),
      dbc.Popover(
          [
          # dbc.PopoverHeader("Trades List"),
          dbc.PopoverBody(id="table-tradeslist"),
          ],
          id='popover-tradeslist',
          target="show-tradeslist",
          is_open=False,
          placement='right',
      ),
     dbc.Button(
         "Trade action dates",
         id="show-tradeactiondates",
         n_clicks=0,
        #  outline=True,
         size="sm",
         color="info",
         style={"margin":4}
      ),
      dbc.Popover(
          [
          # dbc.PopoverHeader("Action Dates"),
          dbc.PopoverBody(id="table-tradeactiondates"),
          ],
          id='popover-tradeactiondates',
          target="show-tradeactiondates",
          is_open=False,
          placement='right',
      ),
     dbc.Button(
         "Day Actions",
         id="show-dayactions",
         n_clicks=0,
        #  outline=True,
         size="sm",
         color="info",
        #  className="mb-3",
        style={"margin":4}
      ),
      dbc.Collapse(
          dbc.Card(dbc.CardBody(id="table-dayactions")),
          id='collapse-dayactions',
          is_open=False,
      ),
    ]
)

ideas_graph = dbc.Spinner(
    id="loading-graph-ideas",
    color="secondary",
    children=[
              html.Div(dcc.Graph(
                  id='graph-ideas',
                  clear_on_unhover = True,
                  config={
                      'displayModeBar': False,
                      'displaylogo': False,
                      # 'modeBarButtonsToRemove': ['zoom2d', 'hoverCompareCartesian', 'hoverClosestCartesian', 'toggleSpikelines']
                      # 'modeBarButtonsToAdd':['drawline','drawopenpath','drawclosedpath','drawcircle','drawrect','eraseshape']
                      },
                  )
              )]
)
owner_card = dbc.Card(
    [
        dbc.CardHeader(
            dbc.Tabs(
                [],
                id="tabs-owner",
                card=True,
                active_tab="MB",
            )
        ),
        dbc.CardBody([
                      trades_info_buttons, 
                      html.Div(empty_row),
                      html.Div(ideas_container),
                      html.Div(ideas_container_selected, hidden=True),
                      ideas_buttons,
                      html.Div(empty_row),
                      html.Div([project_button, apply_button]),
        ]),
    ],
    style={"width": "auto"},
)

iv_graph = dbc.Spinner(
    # id="loading-graph-iv",
    color="primary",
    children=[
              html.Div(
                  dcc.Graph(
                  id='graph-iv',
                  clear_on_unhover = True,
                  config={
                      'displayModeBar': False,
                      'displaylogo': False,
                      # 'modeBarButtonsToRemove': ['zoom2d', 'hoverCompareCartesian', 'hoverClosestCartesian', 'toggleSpikelines']
                      # 'modeBarButtonsToAdd':['drawline','drawopenpath','drawclosedpath','drawcircle','drawrect','eraseshape']
                      },
                  )
              ),
              html.Div(id="table-tradeStatusOverview"),
              html.Div(dcc.Store(id='memory-iv_ec')),
              html.Div(dcc.Store(id='memory-iv_ec_color')),
              ]
)

#fig.show(config={"displayModeBar": True, "showTips": False})  #if not shown via Dash, otherwise "app"

# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
# external_stylesheets = ['https://stackpath.bootstrapcdn.com/bootswatch/4.5.2/cyborg/bootstrap.min.css']
app = JupyterDash(__name__, external_stylesheets=[dbc.themes.CYBORG])
app.config.suppress_callback_exceptions = True

app.layout = dbc.Container(
    [
     html.Div(empty_row),
     dbc.Row([dbc.Label(html.H5("SPX Calls"), width=2),
              dbc.Col(rank_checklist, width={"size": "auto"}), 
              dbc.Col(iv_checklist, width={"size": 'auto', "offset": 1}),
              dbc.Col(dayaction_radioitems, width={"size": 'auto', "offset": 1}),
              dbc.Col(update_button, width="auto"),
              ], align='start', justify='center'),
     dbc.Row([
              dbc.Col(iv_graph),
              ], align='start', justify='center'),
     dbc.Row([dbc.Col(exp_dropdown, width=1),
              dbc.Col(exp_slider),
              dbc.Col(qd_calendar, width="auto"),
              dbc.Col(qd_slider), 
              ], align='start', justify='center'),
              html.Div(empty_row),
     dbc.Row([
              dbc.Col(ideas_graph),
              ], align='start', justify='center'),
     dbc.Row([
              dbc.Col(owner_card, width=12),
              dbc.Col(html.Div(id="temvalue", style={'color': 'white', 'fontSize': 14}))
              ], align='start', justify='center'),
    ],
    className="p-2",
    fluid=True,
)


#--------------Enable UPDATE button for current day only-------------------
@app.callback(
    Output('update', 'disabled'),
    Input('slider-qd', 'value'),
    )
def set_update_button_state(qdseq):
  if qdseq == len(qdmarks)-1:
    return False
  else:
    return True

#--------------get iv_ec & iv_ec_color DataFrames-------------------
@app.callback(
    Output('memory-iv_ec_color', 'data'),
    Output('memory-iv_ec', 'data'),
    Output('calendar-qd', 'date'),
    Output('slider-qd', 'value'),
    Output('dropdown-exp', 'options'),
    Output('dropdown-exp', 'value'),
    Output('slider-exp', 'value'),
    Output('slider-exp', 'marks'),
    Input('update', 'n_clicks'),
    Input('calendar-qd', 'date'),
    Input('slider-qd', 'value'),
    Input('slider-exp', 'value'),
    State('memory-iv_ec_color', 'data'),
    State('memory-iv_ec', 'data'),
    State('dropdown-exp', 'value'),
    )
def prepare_dfs(update, qdcal, qdseq, expseq, iv_ec_color_dict, iv_ec_dict, expdrop):
  triggered = [t["prop_id"] for t in dash.callback_context.triggered]

  if not 'slider-qd' in triggered[0]:
    qdseq = np.where(qdmarks >= qdcal)[0][0]
  qdseqreturn = max(qdseq, len(qdmarks)-qdsliderdays) # to show the lowest day of slider if the date from calendar is out of the bounds
  
  quote_date =  qdmarks[qdseq]
  # Dig the dates for expiration slider
  if qdseq == len(qdmarks)-1:  # for today we don't have information about all expirations
    expmarks = getexpmarks(dfhist_rank, qdmarks[qdseq-1])
  else:
    expmarks = getexpmarks(dfhist_rank, quote_date)
  expslidermarks = {int(i):j[5:7]+'/'+j[:4] for i,j in zip(range(len(expmarks)), expmarks)}
  expdropopt = [{'label':exp, 'value':exp} for exp in expmarks] # [{'label':exp[5:7]+'/'+exp[:4], 'value':exp} for exp in expmarks]
 
  if 'slider-exp' in triggered[0]:
    expiration = expmarks[expseq]
  else: 
    expiration =  expdrop

  if expiration in expmarks:
    expseqreturn = np.where(expmarks == expiration)[0][0]
  else:
    expseqreturn = len(expmarks)-1
    expiration = expmarks[-1]

  if iv_ec_dict is None or 'update' in triggered[0]:
    iv_ec_dict = []
  iv_ec = pd.DataFrame.from_dict(iv_ec_dict)

  if iv_ec_color_dict is None or 'update' in triggered[0]:
    iv_ec_color = []
  iv_ec_color = pd.DataFrame.from_dict(iv_ec_color_dict)
  
  if not iv_ec.empty:
    iv_ec = iv_ec.query("expiration == @expiration and quote_date == @quote_date")
  if not iv_ec_color.empty:
    iv_ec_color = iv_ec_color.query("expiration == @expiration and quote_date == @quote_date")

  if iv_ec.empty:
    iv_ec = dfhist_rank.query("expiration == @expiration and quote_date == @quote_date")
    iv_ec_color = dfhist_ec_rank.query("expiration == @expiration and quote_date == @quote_date")
    if iv_ec.empty:
      # take data from yfinance
      dfactual = getcurrchain(expiration, option_type, quote_date)
      dfactual = dfactual.assign(dte = (pd.to_datetime(dfactual['expiration']).astype('datetime64[ns]')-pd.to_datetime(dfactual['quote_date']).astype('datetime64[ns]')).dt.days)
      dfactual = dfactual.query("option_type == @option_type and strike >= @minstrike and strike%50 == 0 and bid > 0.0 and ask > 0.0 and dte > @mindte")
      dfactual = addOwnGreeks(dfbase=dfactual, source='yahoofinance')
      iv_ec = createdfiv(dfactual, dfhist)
      dfactual_ec = iv_ec[['quote_date','expiration','type','openinterest']].assign(ivec_basis = iv_ec['openinterest']*iv_ec['iv'])
      dfactual_ec = dfactual_ec[['quote_date','expiration','type','openinterest','ivec_basis']].groupby(['quote_date','expiration','type'],as_index=False).agg({"openinterest": 'sum',"ivec_basis": 'sum'})
      dfactual_ec['ivec_basis'] = dfactual_ec['ivec_basis']/dfactual_ec['openinterest']
      iv_ec_color = createdfiv_ec(dfactual_ec, dfhist_ec_rank, 'ivec_basis')   
    iv_ec = iv_ec.query("delta >= @mindelta and delta <= @maxdelta")
    
  return [iv_ec_color.to_dict('records'), iv_ec.to_dict('records'), quote_date, qdseqreturn, expdropopt, expiration, expseqreturn, expslidermarks]

#--------------Trades List / Trade Action Dates-------------------
@app.callback(
Output('popover-tradeslist', 'is_open'),
Output('popover-tradeactiondates', 'is_open'),
Input('show-tradeslist', 'n_clicks'),
Input('show-tradeactiondates', 'n_clicks'),
State('popover-tradeslist', 'is_open'),
State('popover-tradeactiondates', 'is_open'),
)
def tradeslist_popover(n, n_a, is_open, is_open_a):
  triggered = [t["prop_id"] for t in dash.callback_context.triggered]
  isopen = False
  isopen_a = False
  if 'show-tradeslist' in triggered[0]:
    isopen =  not is_open
    isopen_a = False
  if 'show-tradeactiondates' in triggered[0]:
    isopen_a =  not is_open_a
    isopen = False

  return [isopen, isopen_a]

#--------------Day Actions Collapse-------------------
@app.callback(
    Output("collapse-dayactions", "is_open"),
    Input("show-dayactions", "n_clicks"),
    State("collapse-dayactions", "is_open"),
)
def dayactions_collapse(n, is_open):
  triggered = [t["prop_id"] for t in dash.callback_context.triggered]
  isopen = False
  if 'show-dayactions' in triggered[0]:
    isopen =  not is_open

  return isopen

#--------------Split Selection / Close-------------------
@app.callback(
Output('popover-split', 'is_open'),
Output('popover-splitclose', 'is_open'),
Input('show-split', 'n_clicks'),
Input('show-splitclose', 'n_clicks'),
State('popover-split', 'is_open'),
State('popover-splitclose', 'is_open'),
)
def split_popover(n, n_cl, is_open, is_open_cl):
  triggered = [t["prop_id"] for t in dash.callback_context.triggered]
  isopen = False
  isopen_cl = False
  if 'show-split' in triggered[0]:
    isopen =  not is_open
    isopen_cl = False
  if 'show-splitclose' in triggered[0]:
    isopen_cl =  not is_open_cl
    isopen = False

  return [isopen, isopen_cl]

# # if confirmdialog is used
# @app.callback(
#     Output('confirm-apply', 'displayed'),
#     Input('apply-ideas', 'n_clicks'),
# )
# def display_confirm_apply(n):
#   triggered = [t["prop_id"] for t in dash.callback_context.triggered]
#   if 'apply-ideas' in triggered[0]:
#         return True
#   return False

#--------------ideas-------------------
@app.callback(
    Output('table-split', 'children'),
    Output('table-splitclose', 'children'),
    Output('container-ideas', 'data'),
    Output('container-ideas-selected', 'data'),
    Output('container-ideas', 'selected_rows'),
    Input('update', 'n_clicks'),
    Input('propose-action', 'n_clicks'),
    Input('apply-ideas', 'n_clicks'),
    Input('clear-all', 'n_clicks'),
    Input('add-row', 'n_clicks'),
    Input('show-split', 'n_clicks'),
    Input('show-splitclose', 'n_clicks'),
    Input('container-ideas', 'data'),
    Input('container-ideas', 'selected_rows'),
    Input('memory-iv_ec_color', 'data'),
    Input('memory-iv_ec', 'data'),
    State('dropdown-delta', 'value'),
    State('dropdown-vega', 'value'),
    State('dropdown-exp', 'value'),
    State('calendar-qd', 'date'),
    State('container-ideas-selected', 'data'),
    State('tabs-owner', 'active_tab'),
    )
def add_idea_row(update, propose, apply, clear, add, split, splitclose, ideas, selected_rows, iv_ec_color_dict, iv_ec_dict, delta_input, vega_input, expiration, quote_date, selected_ideas, owner):
  triggered = [t["prop_id"] for t in dash.callback_context.triggered]

  iv_ec = pd.DataFrame.from_dict(iv_ec_dict)
  iv_ec_color = pd.DataFrame.from_dict(iv_ec_color_dict)

  ivrank_ec_1M = iv_ec_color['ivrank_ec_1M'].values[0]

  if 'clear-all' in triggered[0]:
    ideas.clear()

  if 'add-row' in triggered[0]:
    # ideas.append({c['id']: '' for c in columns})
    ideas.append({'input-quantity':10, 'input-strike':'', 'dropdown-action':'SELL', 'input-price':0, 'delta':0, 'vega':0, 'strike':''})
    selected_rows.append(len(ideas)-1)

  lasttrade_close_date = dftw_tradeclosed.query("owner == @owner and expiration == @expiration and trade_close_date <= @quote_date")['trade_close_date'].max()
  if pd.isnull(lasttrade_close_date):
    lasttrade_close_date = '1900-01-01'
  if not dftw.empty:
    dftwideas = dftw.query("owner == @owner and expiration == @expiration")
  filenameTrades = 'trades.csv'
  dftrades = loadcsvtodf(ideas_directory, filenameTrades)
  if not dftrades.empty:
    dftrades = dftrades.query("owner == @owner and expiration == @expiration")
    if not dftrades.empty:
      dftwideas = pd.concat([dftwideas,dftrades], ignore_index=True)

  if not dftwideas.empty:
    if dftwideas.query("trade_start_date >= @lasttrade_close_date").empty:
      isactivetrade = False
    else:
      isactivetrade = True
      dftw_ow_ec_qd = dftwideas.query("transaction_date <= @quote_date and transaction_date > @lasttrade_close_date")[['owner','Strike_Price','trade_start_date','value_float','quantity_withsign']].groupby(['owner','Strike_Price','trade_start_date'],as_index=False).agg({"value_float": 'sum', "quantity_withsign": 'sum'})
      tw_legs = np.sort(dftw_ow_ec_qd.query("quantity_withsign != 0")['Strike_Price'])
      tw_status_pl_current, tw_status = getTradeStatusPL(dftw_ow_ec_qd, iv_ec)
      tw_status_delta = (100*tw_status['delta']*tw_status['quantity_withsign']).sum()
      tw_status_vega = (100*tw_status['vega']*tw_status['quantity_withsign']).sum()
  else:
    isactivetrade = False

  # refresh ideas for those with 0 price
  i = len(ideas)-1
  while i>=0:
    if ideas[i]['input-strike'] != '' and (ideas[i]['input-price'] == 0 or ideas[i]['input-strike'] != ideas[i]['strike']) or 'update' in triggered[0]:
      strike_r, delta_r, vega_r, mid_r, ivrank_r, zone_r = getoptstrike(iv_ec, 0, 0, ideas[i]['input-strike'])
      ideas[i]['input-price']=mid_r
      ideas[i]['delta']=delta_r
      ideas[i]['vega']=vega_r
      ideas[i]['strike']=strike_r
    i=i-1

  # close trade
  close_trade = []
  if isactivetrade:
    for strike in tw_legs:
      strike, delta, vega, mid, ivrank, zone = getoptstrike(iv_ec, 0, 0, strike)
      strike_qty = tw_status.query("strike == @strike")['quantity_withsign'].values[0]
      if strike_qty<0:
        action = 'BUY'
        strike_qty = -strike_qty
      else:
        action = 'SELL'
      close_trade.append({'input-quantity':strike_qty, 'input-strike':strike, 'dropdown-action':action, 'input-price':mid, 'delta':delta, 'vega':vega, 'strike':strike})

  if 'propose-action' in triggered[0]:
    selected_rows=[]

    # required eventualy optimal(=default) delta vega values
    try:
      delta_opt = int(delta_input)
    except:
      delta_opt = delta_opt_abs+delta_opt_rel*ivrank_ec_1M
    try:
      vega_opt = int(vega_input[:-1])*1000
    except:
      vega_opt = vega_opt_abs+vega_opt_rel*ivrank_ec_1M
  
    if not isactivetrade:
      # new trade
      vega = vega_opt/100
      delta = delta_opt/100
      strike1, delta1, vega1, mid1, ivrank1, zone1 = getoptstrike(iv_ec, newtrade_insideshortdeltafrom, newtrade_insideshortdeltato, 0, 'short')
      strike2, delta2, vega2, mid2, ivrank2, zone2 = getoptstrike(iv_ec, newtrade_longdeltafrom, newtrade_longdeltato, 0, 'long')
      strike3, delta3, vega3, mid3, ivrank3, zone3 = getoptstrike(iv_ec, newtrade_outsideshortdeltafrom, newtrade_outsideshortdeltato, 0, 'short')
      strike2_qty = newtrade_longqty
      strike3_qty = ((delta*vega1-delta1*vega+strike2_qty*(delta1*vega2-delta2*vega1))/(delta3*vega1-delta1*vega3)).round(0)
      strike1_qty = ((vega-strike2_qty*vega2-vega3*strike3_qty)/vega1).round(0)
      # strike1
      if strike1_qty<0:
        action1 = 'SELL'
        strike1_qty = -strike1_qty
      else:
        action1 = 'BUY'
      # strike2
      if strike2_qty<0:
        action2 = 'SELL'
        strike2_qty = -strike2_qty
      else:
        action2 = 'BUY'
      # strike3
      if strike3_qty<0:
        action3 = 'SELL'
        strike3_qty = -strike3_qty
      else:
        action3 = 'BUY'
      if strike1_qty>0 and strike2_qty>0 and strike3_qty>0 and ivrank1>=ivrank2 and ivrank3>=ivrank2+newtrade_outsideshort_ivrank_tolerance:  
        ideas.append({'input-quantity':strike1_qty, 'input-strike':strike1, 'dropdown-action':action1, 'input-price':mid1, 'delta':delta1, 'vega':vega1, 'strike':strike1})
        selected_rows.append(len(ideas)-1)
        ideas.append({'input-quantity':strike2_qty, 'input-strike':strike2, 'dropdown-action':action2, 'input-price':mid2, 'delta':delta2, 'vega':vega2, 'strike':strike2})
        selected_rows.append(len(ideas)-1)
        ideas.append({'input-quantity':strike3_qty, 'input-strike':strike3, 'dropdown-action':action3, 'input-price':mid3, 'delta':delta3, 'vega':vega3, 'strike':strike3})
        selected_rows.append(len(ideas)-1)
    else:
      # existing trade
      delta = (delta_opt - tw_status_delta)/100
      vega = (vega_opt - tw_status_vega)/100
      # only spreads are allowed
      selected = False
      for i, strikeinside in enumerate(tw_legs):
        for j, strikeoutside in enumerate(tw_legs):  
          if j>i:
            strike1, delta1, vega1, mid1, ivrank1, zone1 = getoptstrike(iv_ec, 0, 0, strikeinside)
            strike2, delta2, vega2, mid2, ivrank2, zone2 = getoptstrike(iv_ec, 0, 0, strikeoutside)
            if zone1 != zone2:  # not the same zone
              strike2_qty = ((delta*vega1-delta1*vega)/(delta2*vega1-delta1*vega2)).round(0)
              qtyoutside = tw_status.query("delta == @delta2")['quantity_withsign'].values[0]
              if np.sign(strike2_qty) != np.sign(qtyoutside) and abs(strike2_qty) > abs(qtyoutside):  # limit by original leg qty
                  strike2_qty = np.sign(strike2_qty) * abs(qtyoutside)
              strike1_qty = ((vega-strike2_qty*vega2)/vega1).round(0)
              qtyinside = tw_status.query("delta == @delta1")['quantity_withsign'].values[0]
              if np.sign(strike1_qty) != np.sign(qtyinside) and abs(strike1_qty) > abs(qtyinside):  # limit by original leg qty
                  strike1_qty = np.sign(strike1_qty) * abs(qtyinside)
              deltadiff = abs(100*(delta - (strike1_qty*delta1 + strike2_qty*delta2))) # deviation from "management" delta
              if deltadiff<=delta_smooth_max*2: # double
                # strike1
                if strike1_qty<0:
                  action1 = 'SELL'
                  strike1_qty = -strike1_qty
                else:
                  action1 = 'BUY'
                # strike2
                if strike2_qty<0:
                  action2 = 'SELL'
                  strike2_qty = -strike2_qty
                else:
                  action2 = 'BUY'
                if strike1_qty>0 and strike2_qty>0 and action1!=action2 and (action1=='BUY' and ivrank1<=ivrank2 or action1=='SELL' and ivrank1>=ivrank2):  
                  # smooth to get acceptable ratios 1:2 or 1:3
                  if strike1_qty<strike2_qty:
                    deltadiff2 = abs((strike1_qty*2 - strike2_qty)*delta2*100)
                    deltadiff3 = abs((strike1_qty*3 - strike2_qty)*delta2*100)
                    if deltadiff2<=delta_smooth_max:
                      strike2_qty = strike1_qty*2
                    if deltadiff3<=delta_smooth_max and deltadiff3<deltadiff2:
                      strike2_qty = strike1_qty*3
                  elif strike2_qty<strike1_qty:                
                    deltadiff2 = abs((strike2_qty*2 - strike1_qty)*delta1*100)
                    deltadiff3 = abs((strike2_qty*3 - strike1_qty)*delta1*100)
                    if deltadiff2<=delta_smooth_max:
                      strike1_qty = strike2_qty*2
                    if deltadiff3<=delta_smooth_max and deltadiff3<deltadiff2:
                      strike1_qty = strike2_qty*3

                  ideas.append({'input-quantity':strike1_qty, 'input-strike':strike1, 'dropdown-action':action1, 'input-price':mid1, 'delta':delta1, 'vega':vega1, 'strike':strike1})
                  if not selected:
                    selected_rows.append(len(ideas)-1)
                  ideas.append({'input-quantity':strike2_qty, 'input-strike':strike2, 'dropdown-action':action2, 'input-price':mid2, 'delta':delta2, 'vega':vega2, 'strike':strike2})
                  if not selected:
                    selected_rows.append(len(ideas)-1)
                  selected = True  # only 1st proposal will be marked as selected

  selected_ideas = []
  nonselected_ideas = []
  for i, item in enumerate(ideas):
    if i in selected_rows: 
      selected_ideas.append(ideas[i])
    else:
      nonselected_ideas.append(ideas[i])

  # # 4testing
  # test = pd.DataFrame(selected_ideas)
  # savetocsvwithwaiting(test, ideas_directory, 'test.csv', time_to_wait, 'w')

  if 'apply-ideas' in triggered[0]:
    ideas = nonselected_ideas
    selected_ideas = []
    selected_rows = []
    close_trade = [] # rather like this

  # split into acteptable ratios
  dfclose = splitideaintoacceptableratios(pd.DataFrame(close_trade))
  tableSplitClose = dbc.Table.from_dataframe(dfclose, striped=True, hover=True, size='lg')
  dfsplit = splitideaintoacceptableratios(pd.DataFrame(selected_ideas))
  tableSplitSelection = dbc.Table.from_dataframe(dfsplit, striped=True, hover=True, size='lg')

  return [tableSplitSelection, tableSplitClose, ideas, selected_ideas, selected_rows]

#--------------graphs-------------------
@app.callback(
    Output('table-tradeactiondates', 'children'),
    Output('table-tradeslist', 'children'),
    Output('table-dayactions', 'children'),
    Output('table-tradeStatusOverview', 'children'),
    Output('graph-ideas', 'figure'),
    Output('graph-iv', 'figure'),
    Output('tabs-owner', 'children'),
    Output('apply-ideas', 'disabled'),
    Input('update', 'n_clicks'),
    Input('project-ideas', 'n_clicks'),
    Input('apply-ideas', 'n_clicks'),
    # Input('confirm-apply', 'submit_n_clicks'),   # if confirmdialog is used...also change 'apply-ideas' in triggered[0] -> 'confirm-apply' in triggered[0]
    Input('checklist-iv', 'value'),
    Input('checklist-rank', 'value'),
    Input('radioitems-dayaction', 'value'),
    Input('tabs-owner', 'active_tab'),
    Input('memory-iv_ec_color', 'data'),
    Input('memory-iv_ec', 'data'),
    State('dropdown-exp', 'value'),
    State('calendar-qd', 'date'),
    State('slider-qd', 'value'),
    State('container-ideas-selected', 'data'),
    )
def update_figure(update, project, apply, checklistiv, checklistrank, dayaction, owner, iv_ec_color_dict, iv_ec_dict, expiration, quote_date, qdseq, ideas):
  accounts = loadcsvtodf(accounts_directory, 'trade_accounts.csv')
  account_keys_values = [{ 'key': row["Key"], 'value': row["Value"]} for index, row in accounts.iterrows() ]
  current_user = loadcsvtodf(accounts_directory, 'current_user_trade_account.csv')
  current_user_trade_account = [{ 'key': row["Key"], 'value': row["Value"]} for index, row in current_user.iterrows() ]

  triggered = [t["prop_id"] for t in dash.callback_context.triggered]
 
  iv_ec = pd.DataFrame.from_dict(iv_ec_dict)
  iv_ec_color = pd.DataFrame.from_dict(iv_ec_color_dict)

  underlying_price = iv_ec['underlying_price'].values[0]
  dte = iv_ec['dte'].values[0]
    
  lasttrade_close_date = dftw_tradeclosed.query("owner == @owner and expiration == @expiration and trade_close_date <= @quote_date")['trade_close_date'].max()
  if pd.isnull(lasttrade_close_date):
    lasttrade_close_date = '1900-01-01'

  dftwideas_allexp = dftw.query("owner == @owner")
  dftwideas = dftw.query("owner == @owner and expiration == @expiration")

  filenameTrades = 'trades.csv'
  dftrades = loadcsvtodf(ideas_directory, filenameTrades)
  if not dftrades.empty:
    dftrades_allexp = dftrades.query("owner == @owner")
    dftwideas_allexp = pd.concat([dftwideas_allexp,dftrades_allexp], ignore_index=True)
    dftrades = dftrades.query("owner == @owner and expiration == @expiration")
    dftwideas = pd.concat([dftwideas,dftrades], ignore_index=True)

  ideatype = 'Idea'
  dfideas = pd.DataFrame(columns=['owner', 'quantity', 'Strike_Price', 'Action', 'price'])
  if 'project-ideas' in triggered[0] or 'apply-ideas' in triggered[0] or 'checklist-iv' in triggered[0] or 'checklist-rank' in triggered[0] or 'radioitems-dayaction' in triggered[0] or 'update' in triggered[0]:
    if 'apply-ideas' in triggered[0]:
      ideatype = 'Trade'
    # filename = 'ideas_'+owner+'.csv' 
    # dfideas = loadcsvtodf(ideas_directory, filename)
    dfideas = pd.DataFrame(ideas)
    if not dfideas.empty:
      dfideas = dfideas.drop(['delta', 'vega' ,'strike'], axis = 1) 
      dfideas = dfideas.rename(columns={'input-quantity': 'quantity', 'input-strike': 'Strike_Price', 'dropdown-action': 'Action', 'input-price': 'price'})
      dfideas = dfideas.assign(owner=owner)
      # yes, get trade start date which is needed as input
      help = dftwideas.query("transaction_date <= @quote_date and transaction_date > @lasttrade_close_date")[['owner','Strike_Price','trade_start_date','value_float','quantity_withsign']].groupby(['owner','Strike_Price','trade_start_date'],as_index=False).agg({"value_float": 'sum', "quantity_withsign": 'sum'})
      help = help.query("quantity_withsign != 0")
      if not help.empty:
        trade_start_date = help['trade_start_date'].values[0]
      else:
        trade_start_date = quote_date
      dfideas = adaptIdeas(dfideas, dftwideas[['Strike_Price','quantity_withsign']])
      dfideastrade = prepareTradeFromIdeas(dfideas, quote_date, expiration, trade_start_date, iv_ec, ideatype)
      if 'apply-ideas' in triggered[0]:
        savetocsvwithwaiting(dfideastrade, ideas_directory, filenameTrades, time_to_wait, 'a')
        dftwideas_allexp = pd.concat([dftwideas_allexp,dfideastrade], ignore_index=True)
      dftwideas = pd.concat([dftwideas,dfideastrade], ignore_index=True)

  if not dftwideas.empty:
    dftwideas['pl_realized'] = dftwideas.apply(
      lambda row: getRealizedStrikePL(row["owner"], row["expiration"], row["Strike_Price"], row["Action"], row["Quantity"], row["value_float"], row["transaction_date"], row["trade_start_date"], dftwideas), axis=1
      )
      
  dftw_ow_ec_qd = dftwideas.query("transaction_date <= @quote_date and transaction_date > @lasttrade_close_date")[['owner','Strike_Price','trade_start_date','value_float','quantity_withsign']].groupby(['owner','Strike_Price','trade_start_date'],as_index=False).agg({"value_float": 'sum', "quantity_withsign": 'sum'})
  
  # Open price
  tw_status_pl_current, tw_status = getTradeStatusPL(dftw_ow_ec_qd, iv_ec)
  if tw_status.empty:
    isactivetrade = False
  else:
    isactivetrade = True

  if isactivetrade:
    # P&L current
    tw_status_pl_current = (tw_status_pl_current/1000).round(1) 
    trade_start_date = tw_status['trade_start_date'].values[0]
    # P&L in a day
    quote_date_previous = qdmarks[qdseq-1]
    if quote_date_previous < trade_start_date:
      tw_status_pl_previous = 0
    else:  
      iv_ec_previous = dfhist_rank.query("expiration == @expiration and quote_date == @quote_date_previous and delta >= @mindelta and delta <= @maxdelta")
      dftw_ow_ec_qd_previous = dftwideas.query("transaction_date <= @quote_date_previous and transaction_date > @lasttrade_close_date")[['owner','Strike_Price','trade_start_date','value_float','quantity_withsign']].groupby(['owner','Strike_Price','trade_start_date'],as_index=False).agg({"value_float": 'sum', "quantity_withsign": 'sum'})
      tw_status_pl_previous, tw_status_previous = getTradeStatusPL(dftw_ow_ec_qd_previous, iv_ec_previous)
      tw_status_pl_previous = (tw_status_pl_previous/1000).round(1) 
    tw_status_pl_day = (tw_status_pl_current - tw_status_pl_previous).round(1)
    # P&L expiration
    tw_status_pl_expiration = getTradePL(underlying_price, tw_status, dftw_ow_ec_qd, exp=True)
    tw_status_pl_expiration = (tw_status_pl_expiration/1000).round(1)
    iv_ec['pl_expiration'] = iv_ec.apply(
        lambda row: getTradePL(row["strike"], tw_status, dftw_ow_ec_qd, exp=True), axis=1) 
    # P&L theoretical
    iv_ec['pl_theoretical'] = iv_ec.apply(
        lambda row: getTradePL(row["strike"], tw_status, dftw_ow_ec_qd), axis=1) 
    # P&L AI
    iv_ec['pl_model'] = iv_ec.apply(
        lambda row: getTradePL(row["strike"], tw_status, dftw_ow_ec_qd, iv_colname='iv_model'), axis=1) 
    # greeks trade current
    tw_status_delta = (100*tw_status['delta']*tw_status['quantity_withsign']).sum().round(0)
    tw_status_vega = (100*tw_status['vega']*tw_status['quantity_withsign']/1000).sum().round(1)
    # greeks trade over the whole expiration cycle 
    # greeks theoretical
    iv_ec['delta_trade_strike'] = iv_ec.apply(
        lambda row: getTradeGreek(row["strike"], tw_status, 'delta'), axis=1) 
    iv_ec['vega_trade_strike'] = iv_ec.apply(
        lambda row: getTradeGreek(row["strike"], tw_status, 'vega'), axis=1) 
    # greeks AI
    iv_ec['delta_trade_strike_model'] = iv_ec.apply(
        lambda row: getTradeGreek(row["strike"], tw_status, 'delta', 'iv_model'), axis=1) 
    iv_ec['vega_trade_strike_model'] = iv_ec.apply(
        lambda row: getTradeGreek(row["strike"], tw_status, 'vega', 'iv_model'), axis=1) 
    # PM (=portfolio margin) requirement theoretical
    naked_contracts = tw_status['quantity_withsign'].sum()
    total_contracts = tw_status.query("quantity_withsign > 0")['quantity_withsign'].sum()
    total_contracts = total_contracts - tw_status.query("quantity_withsign < 0")['quantity_withsign'].sum()
    tw_status_margin = getPortfolioMarginRequirement(underlying_price, iv_ec, naked_contracts, total_contracts)
    tw_status_margin = (tw_status_margin/1000).round(1)
    # PM theoretical
    iv_ec['margin'] = iv_ec.apply(
        lambda row: getPortfolioMarginRequirement(row["strike"], iv_ec, naked_contracts, total_contracts), axis=1) 
    # PM AI
    iv_ec['margin_model'] = iv_ec.apply(
        lambda row: getPortfolioMarginRequirement(row["strike"], iv_ec, naked_contracts, total_contracts, 'pl_model'), axis=1) 

  # P&L realized
  if dftwideas.empty:
    isplrealizedday = False
    tw_status_pl_realized_day = 0.0
  else:  
    tw_status_realized_day = dftwideas.query("transaction_date == @quote_date")[['trade_start_date','pl_realized']].groupby(['trade_start_date'],as_index=False).agg({"pl_realized": 'sum'})
    if tw_status_realized_day.empty:
      isplrealizedday = False
      tw_status_pl_realized_day = 0.0
    else:
      isplrealizedday = True
      tw_status_pl_realized_day = (tw_status_realized_day['pl_realized'].values[0]/1000).round(1)
      trade_start_date = tw_status_realized_day['trade_start_date'].values[0]

  if isplrealizedday or isactivetrade:
    tw_status_pl_realized_current = dftwideas.query("transaction_date <= @quote_date and transaction_date >= @trade_start_date")['pl_realized'].sum()
    tw_status_pl_realized_current = (tw_status_pl_realized_current/1000).round(1)
    din = (datetime.strptime(quote_date, '%Y-%m-%d') - datetime.strptime(trade_start_date, '%Y-%m-%d')).days

  # ------------------Trades List table-----------------------------
  dfTradesList = pd.DataFrame()
  if not dftwideas_allexp.empty:
   dfTradesList = dftwideas_allexp.query("Type == 'Trade'")[['trade_start_date','expiration']].groupby(['trade_start_date','expiration'],as_index=False).agg({})
   dfTradesList = pd.merge(dfTradesList,dftw_tradeclosed.query("owner == @owner")[['expiration','trade_close_date']].groupby(['expiration'],as_index=False).agg({"trade_close_date": 'max'}), how='left',left_on=['expiration'],right_on=['expiration']) 
   dfTradesList['trade_close_date'] = dfTradesList.apply(
       lambda row: "1900-01-01" if pd.isnull(row['trade_close_date']) else row['trade_close_date'] , axis = 1
       )
   dfTradesList['Status'] = dfTradesList.apply(
       lambda row: "ACTIVE" if row['trade_start_date']>row['trade_close_date'] else "Closed" , axis = 1
       )
   dfTradesList['Expiration'] = dfTradesList.apply(
       lambda row: row['expiration'][5:7]+'/'+row['expiration'][:4], axis = 1
       )
   dfTradesList = dfTradesList.drop(['expiration', 'trade_close_date'], axis = 1)
   dfTradesList = dfTradesList.rename(columns={'trade_start_date': 'Start Date'})
  tableTradesList = dbc.Table.from_dataframe(dfTradesList, key="tableTradeList", striped=True, hover=True, size='md')

  #------------------Trade Action Dates table-----------------------------
  dfTradeActionDates = pd.DataFrame()  #(columns=['owner', 'quantity', 'Strike_Price', 'Action', 'price'])
  if not dftwideas.empty and isactivetrade:
    dfTradeActionDates = dftwideas.query("transaction_date >= @trade_start_date and Type == 'Trade'")[['transaction_date']].groupby(['transaction_date'],as_index=False).agg({})
    dfTradeActionDates = dfTradeActionDates.rename(columns={'transaction_date': 'Transaction Date'})
  tableTradeActionDates = dbc.Table.from_dataframe(dfTradeActionDates, key="tabletradeactiondates", striped=True, hover=True, size='md')

  # ------------------Day Action table------------------------------
  dfDayActions = pd.DataFrame()
  if not dftwideas.empty:
    dfDayActions = dftwideas.query("transaction_date == @quote_date and Type == 'Trade'")[['Quantity','Strike_Price','Action','value_float']]
    dfDayActions["value_float"] = abs(dfDayActions["value_float"]/dfDayActions["Quantity"]/100).round(2)
    dfDayActions = dfDayActions.rename(columns={'Strike_Price': 'Strike', 'value_float': 'Price'})
  tableDayActions = dbc.Table.from_dataframe(dfDayActions, key="tabledayactions", striped=True, hover=True, size='md')

  # ------------------TradeStatusOverview table------------------------------
  dfTradeStatusOverview = pd.DataFrame()
  if not dftwideas.empty:
    dftw_ow_ec_qd_noideas = dftwideas.query("transaction_date <= @quote_date and transaction_date > @lasttrade_close_date and Type != 'Idea'")[['owner','Strike_Price','trade_start_date','value_float','quantity_withsign']].groupby(['owner','Strike_Price','trade_start_date'],as_index=False).agg({"value_float": 'sum', "quantity_withsign": 'sum'}) 
    if not dftw_ow_ec_qd_noideas.empty and not dfideas.empty and ideatype == 'Idea':
      tw_status_pl_realized_current_noideas = dftwideas.query("transaction_date <= @quote_date and transaction_date >= @trade_start_date and Type != 'Idea'")['pl_realized'].sum()
      tw_status_pl_realized_current_noideas = (tw_status_pl_realized_current_noideas/1000).round(1)
      
      tw_status_realized_day_noideas = dftwideas.query("transaction_date == @quote_date and Type != 'Idea'")[['trade_start_date','pl_realized']].groupby(['trade_start_date'],as_index=False).agg({"pl_realized": 'sum'})
      if tw_status_realized_day_noideas.empty:
        tw_status_pl_realized_day_noideas = 0.0
      else:  
       tw_status_pl_realized_day_noideas = (tw_status_realized_day_noideas['pl_realized'].values[0]/1000).round(1)

      tw_status_pl_current_noideas, tw_status_noideas = getTradeStatusPL(dftw_ow_ec_qd_noideas, iv_ec)
      tw_status_pl_expiration_noideas = getTradePL(underlying_price, tw_status_noideas, dftw_ow_ec_qd_noideas, exp=True)
      tw_status_pl_expiration_noideas = (tw_status_pl_expiration_noideas/1000).round(1)

      naked_contracts_noideas = tw_status_noideas['quantity_withsign'].sum()
      total_contracts_noideas = tw_status_noideas.query("quantity_withsign > 0")['quantity_withsign'].sum()
      total_contracts_noideas = total_contracts_noideas - tw_status_noideas.query("quantity_withsign < 0")['quantity_withsign'].sum()
      tw_status_margin_noideas = getPortfolioMarginRequirement(underlying_price, iv_ec, naked_contracts_noideas, total_contracts_noideas)
      tw_status_margin_noideas = (tw_status_margin_noideas/1000).round(1)

      tw_status_delta_noideas = (100*tw_status_noideas['delta']*tw_status_noideas['quantity_withsign']).sum().round(0)
      tw_status_vega_noideas = (100*tw_status_noideas['vega']*tw_status_noideas['quantity_withsign']/1000).sum().round(1)
      
      dfTradeStatusOverview = pd.DataFrame({
          "": ["w/o", "incl."], 
          "P/L realized": [str(tw_status_pl_realized_current_noideas)+"K", str(tw_status_pl_realized_current)+"K"],  
          "P/L realized Day": [str(tw_status_pl_realized_day_noideas)+"K", str(tw_status_pl_realized_day)+"K"],
          "P/L expiration": [str(tw_status_pl_expiration_noideas)+"K", str(tw_status_pl_expiration)+"K"],
          "Portfolio Margin": [str(tw_status_margin_noideas)+"K", str(tw_status_margin)+"K"],
          "DELTA": [str(tw_status_delta_noideas), str(tw_status_delta)],
          "VEGA": [str(tw_status_vega_noideas)+"K", str(tw_status_vega)+"K"],
      })
    elif not dftw_ow_ec_qd_noideas.empty or not dfideas.empty:
      dfTradeStatusOverview = pd.DataFrame({
          "P/L realized": [str(tw_status_pl_realized_current)+"K"],
          "P/L realized Day": [str(tw_status_pl_realized_day)+"K"],
          "P/L expiration": [str(tw_status_pl_expiration)+"K"],
          "Portfolio Margin": [str(tw_status_margin)+"K"],
          "DELTA": [str(tw_status_delta)],
          "VEGA": [str(tw_status_vega)+"K"],
      })
  tableTradeStatusOverview = dbc.Table.from_dataframe(dfTradeStatusOverview, key="tableTradeStatusOverview",striped=True, bordered=True, hover=True, size='md')

  # ------------------Ideas Graph------------------------------
  
  # underlying history + current price if needed
  if not dfideas.empty:
    # df_coupon = dfhist_rank[dfhist_rank['strike'].isin(np.sort(dfideas["Strike_Price"].unique()))].query("expiration == @expiration and dte >= @dte and dte<=@dte+@lookbackperiod_ideas")[['quote_date','dte','underlying_price']].groupby(['quote_date','dte'],as_index=False).agg({"underlying_price": 'min'})
    # take only dates where all strikes existed
    df_coupon = dfhist_rank[dfhist_rank['strike'].isin(np.sort(dfideas["Strike_Price"].unique()))].query("expiration == @expiration and dte >= @dte and dte<=@dte+@lookbackperiod_ideas")[['quote_date','dte','strike','underlying_price']].groupby(['quote_date','dte', 'strike'],as_index=False).agg({"underlying_price": 'min'})
    df_coupon = df_coupon.assign(count = 1)
    df_coupon = df_coupon[['quote_date','dte','underlying_price', 'count']].groupby(['quote_date','dte','underlying_price'],as_index=False).agg({"count": 'sum'})
    count_strikes = len(dfideas["Strike_Price"].unique())
    df_coupon = df_coupon.query('count == @count_strikes').drop(['count'], axis = 1) 
  else:
    df_coupon = dfhist_rank.query("expiration == @expiration and dte >= @dte and dte<=@dte+@lookbackperiod_ideas")[['quote_date','dte','underlying_price']].groupby(['quote_date','dte'],as_index=False).agg({"underlying_price": 'min'})
  if not quote_date in df_coupon['quote_date'].values:
    df_coupon.loc[len(df_coupon.index)] = [quote_date, dte, underlying_price]
  df_coupon = df_coupon.assign(dtp = (pd.to_datetime(df_coupon['quote_date']).astype('datetime64[ns]')-datetime.strptime(quote_date, '%Y-%m-%d')).dt.days)
  df_coupon = df_coupon.assign(coupon = 0.0)

  if not dfideas.empty and ideatype == 'Idea':
    quote_date_min = df_coupon['quote_date'].min()
    iv_ec_min = dfhist_rank.query("expiration == @expiration and quote_date == @quote_date_min")
    dfideas4coupon = prepareTradeFromIdeas(dfideas, quote_date_min, expiration, quote_date_min, iv_ec_min, 'Idea', historicalprice=True)
    # coupon projections
    dfhist_rank_ec = dfhist_rank.query("expiration == @expiration")
    df_coupon['coupon'] = df_coupon.apply(
       lambda row: (-1)*getIdeaStatusPL(owner, expiration, row['quote_date'], quote_date_min, dfideas4coupon, iv_ec, dfhist_rank_ec), axis=1) 
    #define color for coupon line
    npcoupon = df_coupon["coupon"].to_numpy() 
    wsdelta = 0
    for i, value in enumerate(npcoupon):
      if i>0:
       delta = npcoupon[i]-npcoupon[i-1]
       wsdelta = wsdelta + delta*i  
    color_coupon = get_continuous_color(colorscale_bluered, intermed=ideacoloraccelerator*wsdelta/abs(dfideas4coupon['value_float'].sum()))

    df_coupon = df_coupon.assign(deltatime = '')
    df_coupon.loc[df_coupon["dtp"]>=-60, 'deltatime'] = '-2M'
    df_coupon.loc[df_coupon["dtp"]>=-30, 'deltatime'] = '-1M'
    df_coupon.loc[df_coupon["dtp"]>=-7, 'deltatime'] = '-1W'
    previous_trading_day = df_coupon.query("dtp<0")['dtp'].max()
    df_coupon.loc[df_coupon["dtp"]>=previous_trading_day, 'deltatime'] = '-1D'
    df_coupon_deltatime = df_coupon[['quote_date','coupon','deltatime']].groupby(['deltatime'],as_index=False).agg({"quote_date": 'min'})
    df_coupon_deltatime = pd.merge(df_coupon_deltatime,df_coupon, how='left',left_on=['quote_date','deltatime'],right_on=['quote_date','deltatime'])
  
  fig_ideas = make_subplots(specs=[[{"secondary_y": True}]])
 
  fig_ideas.add_trace(go.Scatter(
      x=df_coupon["quote_date"],
      y=df_coupon["underlying_price"],
      # hoverinfo='skip',
      opacity=0.4,
      name="Underlying",
      marker_color='yellow'),
      secondary_y=True,
  )
  if not dfideas.empty and ideatype == 'Idea':
    fig_ideas.add_trace(go.Scatter(
       x=df_coupon["quote_date"],
       y=df_coupon["coupon"],
       customdata = np.stack((df_coupon['dtp'], df_coupon['coupon']/1000), axis=-1),
       hovertemplate=
       '<b>%{customdata[1]:.1f</b>}K<br>' + 
       't%{customdata[0]:.0f}<br>' +
       '<extra></extra>',
       line_width = 2,
       opacity=1,
       name="Coupon",
       marker_color=color_coupon),
       secondary_y=False,
    )
    fig_ideas.add_trace(go.Scatter(
        x=df_coupon_deltatime["quote_date"],
        y=df_coupon_deltatime["coupon"],
        hoverinfo='skip',
        mode='markers+text',
        text=df_coupon_deltatime["deltatime"],
        textposition="top center",
        textfont = dict(
            color='yellow',
            size = 13,
        ),
        marker = dict(
          symbol = 'x',
          color='yellow',
          opacity = 1,
          size = 10,
        ),
      ),
      secondary_y=False,
    )

    # Set y-axis
    fig_ideas.update_yaxes(
        title_text="<b>Coupon</b>",
        secondary_y=False,
        showgrid=False,
        # gridwidth=0.1,
        # gridcolor="gray",
        # zeroline=False,
        layer='below traces',
    )

  # Set x-axis
  fig_ideas.update_xaxes(
      showspikes=True, # Show spike line for X-axis
      # Format spike
      spikethickness=2,
      spikedash="dash",
      spikecolor="white",
      spikemode="across",
      zeroline=False,
      showgrid=False,
      layer='below traces',
      # showticklabels=False,
  )

  fig_ideas.update_yaxes(
      title_text="<b>Underlying</b>",
      secondary_y=True,
      showgrid=False,
      zeroline=False,
      layer='below traces',
    )
  
  fig_ideas.update_layout(
    # height=500,
    # width=300,
    # title='Coupon',
    # xaxis_title="time",
    plot_bgcolor='#111111', #'rgb(232,250,250)',
    paper_bgcolor='#111111',
    font_color='#7FDBFF',
    showlegend=False,
    hovermode="x",
    # hoverlabel=dict(
    #     bgcolor="yellow",
    #     font_size=14,
    #     #font_family="Rockwell"
    # )
  ) 


  # ------------------IV Graph------------------------------

  tw_yaxis='ivrank_1M'
  if '1M' not in checklistrank:
    if '1W' in checklistrank:
      tw_yaxis='ivrank_1W'
    else:
      if '2M' in checklistrank:
        tw_yaxis='ivrank_2M'  

  # expiration cycle IVR color
  ivrank_ec_1M = iv_ec_color['ivrank_ec_1M'].values[0]
  color_ec_1M = get_continuous_color(colorscale_bluered, intermed=ivrank_ec_1M/100)  # 1-ivrank_ec_1M/100 for colors switch
  ivrank_ec_2M = iv_ec_color['ivrank_ec_2M'].values[0]
  color_ec_2M = get_continuous_color(colorscale_bluered, intermed=ivrank_ec_2M/100)
  ivrank_ec_1W = iv_ec_color['ivrank_ec_1W'].values[0]
  color_ec_1W = get_continuous_color(colorscale_bluered, intermed=ivrank_ec_1W/100)
  fig = make_subplots(specs=[[{"secondary_y": True}]])

  # Open interest & volume
  if 'OI' in checklistiv:
    fig.add_trace(go.Bar(
        x=iv_ec["strike"],
        y=iv_ec["openinterest"],
        hoverinfo='skip',
        opacity=0.2,
        width=30,
        name="Open Interest",
        marker_color='blue'),
        secondary_y=True,
    )
  if 'VOL' in checklistiv:
    fig.add_trace(go.Bar(
        x=iv_ec["strike"],
        y=iv_ec["volume"],
        hoverinfo='skip',
        opacity=0.2,
        width=30,
        name="Volume",
        marker_color='aquamarine'), #aliceblue, antiquewhite, aqua, aquamarine, azure,
        secondary_y=True,
    )
      
  # RANKS
  if '1M' in checklistrank:
    if isactivetrade:
      fig.add_trace(go.Scatter(
          x=iv_ec["strike"],
          y=iv_ec["ivrank_1M"].round(0),
          # text = iv_ec["delta"].round(2),
          customdata = np.stack((iv_ec['delta'], iv_ec['pl_theoretical']/1000, iv_ec['pl_expiration']/1000, iv_ec['delta_trade_strike'], iv_ec['vega_trade_strike']/1000, iv_ec['margin']/1000, iv_ec['mid'],
                                 iv_ec['pl_model']/1000, iv_ec['delta_trade_strike_model'], iv_ec['vega_trade_strike_model']/1000, iv_ec['margin_model']/1000), axis=-1),
          hovertemplate=
          '<b>%{y:.0f}</b> IV Rank 1M<br>' +
          # 'delta: %{text}<br>'+
          'delta: %{customdata[0]:.2f}<br>' +
          'mid: %{customdata[6]:.1f}<br>' +
          '---------theo | AI(t1-3)-------<br>' +
          'delta: %{customdata[3]:.0f} | %{customdata[8]:.0f}<br>' +
          'vega:  %{customdata[4]:.1f}K | %{customdata[9]:.1f}K<br>' +
          'PM:  %{customdata[5]:.1f}K | %{customdata[10]:.1f}K<br>' +
          'P/L:   %{customdata[1]:.1f}K | <b>%{customdata[7]:.1f}K</b><br>' +
          '---------exp-------------------<br>' +
          'P/L:   %{customdata[2]:.1f}K<br>' +
          '<extra></extra>',
          name="IV Rank 1M",
          mode='lines',
          line_width = 4,
          marker_color=color_ec_1M,
          opacity=1),
          secondary_y=False,
      )
    else:
      fig.add_trace(go.Scatter(
          x=iv_ec["strike"],
          y=iv_ec["ivrank_1M"].round(0),
          customdata = np.stack((iv_ec['delta'], iv_ec['mid']), axis=-1),
          hovertemplate=
          'IVR1M: <b>%{y:.0f}</b><br>' +
          'delta: %{customdata[0]:.2f}<br>' +
          'mid: %{customdata[1]:.1f}<br>' +
          '<extra></extra>',
          name="IV Rank 1M",
          mode='lines',
          line_width = 4,
          marker_color=color_ec_1M,
          opacity=1),
          secondary_y=False,
      )
  if '1W' in checklistrank:
    fig.add_trace(go.Scatter(
        x=iv_ec["strike"],
        y=iv_ec["ivrank_1W"].round(0),
        name="IV Rank 1W",
        mode='lines',
        line_width = 2,
        marker_color=color_ec_1W,
        opacity=1),
        secondary_y=False,
    )
  if '2M' in checklistrank:
    fig.add_trace(go.Scatter(
        x=iv_ec["strike"],
        y=iv_ec["ivrank_2M"].round(0),
        name="IV Rank 2M",
        mode='lines',
        line_width = 1,
        marker_color=color_ec_2M,
        opacity=1),
        secondary_y=False,
    )

  if 'IVP' in checklistiv:
    if '1M' in checklistrank:
      fig.add_trace(go.Scatter(
          x=iv_ec["strike"],
          y=iv_ec["ivpercentile_1M"].round(0),
          name="IV Percentile 1M",
          mode='lines',
          line_width = 4,
          marker_color='white',
          opacity=1),
          secondary_y=False,
      )
    if '1W' in checklistrank:
      fig.add_trace(go.Scatter(
          x=iv_ec["strike"],
          y=iv_ec["ivpercentile_1W"].round(0),
          name="IV Percentile 1W",
          mode='lines',
          line_width = 2,
          marker_color='white',
          opacity=0.66),
          secondary_y=False,
      )
    if '2M' in checklistrank:
      fig.add_trace(go.Scatter(
          x=iv_ec["strike"],
          y=iv_ec["ivpercentile_2M"].round(0),
          name="IV Percentile 2M",
          mode='lines',
          line_width = 1,
          marker_color='white',
          opacity=0.33),
          secondary_y=False,
      )

  # Trade status  
  if '1M' in checklistrank or '1W' in checklistrank or '2M' in checklistrank:
    fig.add_trace(go.Scatter(
        x=tw_status["strike"],
        y=tw_status[tw_yaxis],
        hoverinfo='skip',
        mode='markers+text',
        text=tw_status["quantity_withsign"],
        textposition="middle center",
        textfont = dict(
            color='yellow',
        ),
        marker = dict(
            symbol = 'hexagon',
            color=list(map(SetColorTWStatus, tw_status["quantity_withsign"])),
            opacity = 1,
            size = 30,
            line = dict(
                color = 'yellow',
                width = 1,
            )
        ),
        opacity = 1,),
        secondary_y=False,
    )
    # Day actions 
    tw_action_ec_qd = dftwideas.query("owner == @owner and expiration == @expiration and transaction_date == @quote_date")[['Strike_Price','value_float','quantity_withsign','quantity_withsign_realized']].groupby(['Strike_Price'],as_index=False).agg({"value_float": 'sum', "quantity_withsign": 'sum', "quantity_withsign_realized": 'sum'})
    tw_action = iv_ec.iloc[np.where(iv_ec.strike.isin(np.sort(tw_action_ec_qd["Strike_Price"].unique())))]
    tw_action = pd.merge(tw_action,tw_action_ec_qd, how='left',left_on=['strike'],right_on=['Strike_Price']) 
    if dayaction == 'realized' or dayaction == 'all':
      if dayaction == 'realized':
        action_quantity_colname = 'quantity_withsign_realized'
        tw_action = tw_action.query("quantity_withsign_realized != 0")
      else:
        action_quantity_colname = 'quantity_withsign'
      fig.add_trace(go.Scatter(
          x=tw_action["strike"],
          y=tw_action[tw_yaxis],
          hoverinfo='skip',
          mode='markers+text',
          text=tw_action[action_quantity_colname],
          textposition="bottom center",
          textfont = dict(
              color=list(map(SetColorTWStatus, tw_action[action_quantity_colname])),
              size = 18,
          ),
          marker = dict(
            symbol = 'circle-open',
            color=list(map(SetColorTWStatus, tw_action[action_quantity_colname])),
            opacity = 1,
            size = 35,
            line = dict(
                width = 3,
            )
          ),
        ),
        secondary_y=False,
    )

  # Underlying price
  fig.add_shape(
      type="line",
      yref="paper",
      x0=underlying_price, y0=0, x1=underlying_price, y1=1,
      opacity=0.6,
      line=dict(
          color="yellow",
          width=2,
          #dash="dot",
          ),
  )

  # Inside short
  insideshortbottom = iv_ec.query("delta <= @insideshortdeltafrom")['strike'].min()
  insideshortup = iv_ec.query("delta >= @insideshortdeltato")['strike'].max()
  fig.add_shape(
      type="rect",
      x0=insideshortbottom, y0=-100, x1=insideshortup, y1=200,
      fillcolor="Red",
      opacity = 0.15,
  )

  # Long
  longbottom = insideshortup
  longup = iv_ec.query("delta >= @longdeltato")['strike'].max()
  fig.add_shape(
      type="rect",
      x0=longbottom, y0=-100, x1=longup, y1=200,
      fillcolor="Green",
      opacity = 0.15,
  )

  # Outside short
  outsideshortbottom = iv_ec.query("delta <= @outsideshortdeltafrom")['strike'].min()
  outsideshortup = iv_ec.query("delta >= @outsideshortdeltato")['strike'].max()
  fig.add_shape(
      type="rect",
      x0=outsideshortbottom, y0=-100, x1=outsideshortup, y1=200,
      fillcolor="Red",
      opacity = 0.15,
  )

  # Set x-axis
  fig.update_xaxes(
      showspikes=True, # Show spike line for X-axis
      # Format spike
      spikethickness=2,
      spikedash="dash",
      spikecolor="white",
      spikemode="across",
      zeroline=False,
      showgrid=False,
      layer='below traces',
  )

  # Set y-axis
  fig.update_yaxes(
      title_text="<b>RANK</b>",
      secondary_y=False,
      gridwidth=0.1,
      gridcolor="gray",
      # zeroline=False,
      layer='below traces',
      range= [iv_ec["ivrank_1M"].min() - min(20,1.5 * abs(iv_ec["ivrank_1M"].min())), iv_ec["ivrank_1M"].max() + min(20,1.5 * abs(iv_ec["ivrank_1M"].max()))]
  )
  if 'OI' in checklistiv or 'VOL' in checklistiv:
    fig.update_yaxes(
        title_text="<b>PIECES</b>",
        secondary_y=True,
        showgrid=False,
        zeroline=False,
        layer='below traces',
    )

  if isactivetrade:
    titletxt = "in "+str(din)+" | "+"<b>"+str(dte)+"</b> dte ... P/L <b>"+str(tw_status_pl_current)+"K</b>                                P/L Day: <b>"+str(tw_status_pl_day)+"K</b>"
  else:
    if isplrealizedday:
      titletxt = "in "+str(din)+" | "+str(dte)+" dte ... P/L <b>"+str(tw_status_pl_realized_current)+"K</b>                                      Trade <b>CLOSED</b>"
    else:  
      titletxt = "<b>"+str(dte)+"</b> dte"  
  # Update layout
  fig.update_layout(
      # height=400, width=1390,
      title=titletxt,
      barmode="stack",
      plot_bgcolor='#111111', #'rgb(232,250,250)',
      paper_bgcolor='#111111',
      font_color='#7FDBFF',
      showlegend=False,
      hovermode="x",
      # hoverlabel=dict(
      #     bgcolor="yellow",
      #     font_size=14,
      #     #font_family="Rockwell"
      # )
  ) 
  apply_select_trigger = True;
  if owner == current_user_trade_account[0]['value']:
    apply_select_trigger = False;
  return [tableTradeActionDates, tableTradesList, tableDayActions, tableTradeStatusOverview, fig_ideas, fig, [dbc.Tab(label=each["value"], tab_id=each["value"]) for each in account_keys_values], apply_select_trigger]
# def get_new_data():
#   managers = loadcsvtodf(managers_directory, 'managers.csv')
#   manager_names = [ row['Name'] for index, row in managers.iterrows() ]
# def get_new_data_every(period=UPDADE_INTERVAL):
#   while True:
#     get_new_data()
#     print("data updated")
#     time.sleep(period)
# def start_multi():
#   executor = ProcessPoolExecutor(max_workers=1)
#   executor.submit(get_new_data_every)
if __name__ == "__main__":
  # start_multi()
  # app.run_server(mode='inline', debug=False, use_reloader=False) #jupyter run server
  app.run_server(port=8060, debug=True, use_reloader=False) #dash run server