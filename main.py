import krakenex
from pykrakenapi import KrakenAPI
import streamlit as st
import pandas as pd
from datetime import datetime


st.title('Proyecto')
data_load_state = st.text('Crypto Prices')
options = st.selectbox(
    'Cotizaciones',
    ['BTC', 'ETH', 'XRP', 'USDC', 'SOL', 'ADA', 'DOGE', 'TRX', 'LINK'],
    placeholder= 'Cryptos'
    )

#st.write('You selected:', options)
st.divider()
st.subheader('Grafica')

import plotly.graph_objects as go
from plotly.subplots import make_subplots

api = krakenex.API()
k = KrakenAPI(api)
parSeleccionado = str(options)+'USDT'
sinceDate = 1640995200
ohlc, last = k.get_ohlc_data(pair=parSeleccionado, interval=10080, since=sinceDate)

ohlc['epoch_time'] = ''
ohlc['epoch_time'] = pd.to_datetime(ohlc['time'], dayfirst=True, unit='s')
ohlc['epoch_time']= ohlc['epoch_time'].dt.strftime('%Y-%m-%d')
ohlc['month']= pd.to_datetime(ohlc['time'], dayfirst=True, unit='s').dt.month


import pandas_ta as ta
# Add some indicators
ohlc.ta.stoch(high='high', low='low', k=14, d=3, append=True)

fig = go.Figure()
fig = make_subplots(rows=2, cols=1)
fig.add_trace(go.Candlestick(
    x=ohlc['epoch_time'], 
    open=ohlc['open'], 
    high=ohlc['high'], 
    low=ohlc['low'], 
    close=ohlc['close'],
    name='Price'
    ) 
)

epoch_timestamp = int(sinceDate)
datetime_obj = datetime.utcfromtimestamp(epoch_timestamp) 
fechaInicio = str(datetime_obj.year) + '-' + str(datetime_obj.month) + '-' + str(datetime_obj.day)

fig.update_xaxes(
    range=[fechaInicio, ohlc.index.max()]
)  # Adjust the date range as needed

fig.update_yaxes(
    range=[str(datetime_obj) ,ohlc['high'].max()+ohlc['high'].min()]
    )  # Adjust the date range as needed

# Remove the range slider from the x-axis
fig.update_xaxes(rangeslider_visible=False)

fig.append_trace(
    go.Scatter(
        x=ohlc.index,
        y=ohlc['STOCHk_14_3_3'],
        line=dict(width=2),
        name='fast',
    ), row=2, col=1  #  <------------ lower chart %d
)
fig.append_trace(
    go.Scatter(
        x=ohlc.index,
        y=ohlc['STOCHd_14_3_3'],
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
    title=parSeleccionado,
    yaxis_title= 'Price',
    width=800,  # Set the width to 800 pixels
    height=600 
)

st.plotly_chart(fig)
st.subheader('Data')

st.write(ohlc)