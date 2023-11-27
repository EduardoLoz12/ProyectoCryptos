from datetime import date, datetime
import streamlit as st
import pandas as pd
import mplfinance as mpf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import krakenex
from pykrakenapi import KrakenAPI
import time
import pandas_ta as ta

#---------------Data---------------------------------------------

st.cache_data(persist='disk')
api = krakenex.API()
q=KrakenAPI(api)

def get_data():
    api = krakenex.API()
    k = KrakenAPI(api)
    x = str(symbol)+'USDT'
    data1, last = k.get_ohlc_data(x,1440, since=unixtime)
    crypto1 =data1.drop(['vwap','count'], axis=1)

    crypto1['date'] = ''
    crypto1['date'] = pd.to_datetime(crypto1['time'], dayfirst=True, unit='s')
    crypto1['date'] = crypto1['date'].dt.strftime('%Y-%m-%d')
    crypto1['month'] = pd.to_datetime(crypto1['time'], dayfirst=True, unit='s').dt.month

    return crypto1

#-----Configuracion Streamlit------------------------------

st.title('Graphic Machine')

monedas = ['BTC', 'ETH', 'XRP', 'USDC', 'SOL', 'ADA', 'DOGE', 'TRX', 'LINK']

c1, c2, c3 = st.columns([1, 1, 1])
with c1:
    symbol = st.selectbox('Choose stock symbol', options=monedas, index=1)
with c2:
    date_from = st.date_input('Show data from', date(2023, 1, 1))
    unixtime = time.mktime(date_from.timetuple())
    datefrom=date_from.strftime("%B-%y")

with c3:
    st.markdown('&nbsp;')
    show_data = st.checkbox('Show data table', False)

st.markdown('---')

st.sidebar.subheader('Settings')
st.sidebar.caption('Adjust charts settings and then press apply')



with st.sidebar.form('settings_form'):
    show_nontrading_days = st.checkbox('Show non-trading days', True)

    mystyle = mpf.make_mpf_style(rc={'axes.labelsize': 'medium'}, style_name="My Style")

    chart_styles = [
        'default', 'binance', 'blueskies', 'brasil',
        'charles', 'checkers', 'classic', 'yahoo', mystyle
       ]
    chart_style = st.selectbox('Chart style', options=chart_styles, index=chart_styles.index('default'))

    mav1 = st.number_input('Mav 1', min_value=3, max_value=30, value=3, step=1)
    mav2 = st.number_input('Mav 2', min_value=6, max_value=30, value=6, step=1)
    mav3 = st.number_input('Mav 3', min_value=9, max_value=30, value=9, step=1)

    st.form_submit_button('Apply')

#-------------------------------Calling Function-------------------------------
data = get_data()
print(data)

# Add some indicators
data.ta.stoch(high='high', low='low', k=14, d=3, append=True)

fig = go.Figure()
fig = make_subplots(rows=2, cols=1)
fig.add_trace(go.Candlestick(
    x=data['date'],
    open=data['open'],
    high=data['high'],
    low=data['low'],
    close=data['close'],
    name='Price'
    )
)

epoch_timestamp = int(unixtime)
datetime_obj = datetime.utcfromtimestamp(epoch_timestamp)
fechaInicio = str(datetime_obj.year) + '-' + str(datetime_obj.month) + '-' + str(datetime_obj.day)

# Adjust the date range as needed
fig.update_xaxes(range=[fechaInicio, data.index.max()])

# Adjust the date range as needed
fig.update_yaxes(range=[str(datetime_obj) ,data['high'].max()+data['high'].min()])

# Remove the range slider from the x-axis
fig.update_xaxes(rangeslider_visible=False)

fig.append_trace(
    go.Scatter(
        x=data.index,
        y=data['STOCHk_14_3_3'],
        line=dict(width=2),
        name='fast',
    ), row=2, col=1  #  <------------ lower chart %d
)
fig.append_trace(
    go.Scatter(
        x=data.index,
        y=data['STOCHd_14_3_3'],
        line=dict(width=2),
        name='slow'
    ), row=2, col=1 #  <------------ lower chart
)

# Extend our y-axis a bit
fig.update_yaxes(range=[-10, 110], row=2, col=1)


# Add overbought/oversold
fig.add_hline(y=20, col=1, row=2, line_color='#336699', line_width=2, line_dash='dash') # type: ignore
fig.add_hline(y=80, col=1, row=2, line_color='#336699', line_width=2, line_dash='dash') # type: ignore

fig.update_layout(
    title='Graficas Probando',
    yaxis_title= 'Price',
    width=800,  # Set the width to 800 pixels
    height=600)

st.plotly_chart(fig)
st.subheader('Data')

st.write(data)