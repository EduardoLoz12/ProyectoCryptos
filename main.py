from datetime import date, datetime
import streamlit as st
import pandas as pd
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

st.sidebar.subheader('Moving Average Selector')
st.sidebar.caption('Select the days of rollback and then press apply')



with st.sidebar.form('Movin Average Selector'):

    mav1 = st.number_input('Mav 1', min_value=3, max_value=50, value=3, step=1)
    mav2 = st.number_input('Mav 2', min_value=6, max_value=50, value=6, step=1)

    st.form_submit_button('Apply')

#-------------------------------Calling Function-------------------------------
data = get_data()
print(data)

# Add some indicators
data.ta.stoch(high='high', low='low', k=14, d=3, append=True)

fig = go.Figure()
fig = make_subplots(rows=3, cols=1,
                    shared_xaxes=True,
                    row_heights=[0.3, 0.8, 0.3],
                    )

fig.for_each_xaxis(lambda x: x.update(showticklabels=True))

fig.add_trace(go.Candlestick(
    x=data['date'],
    open=data['open'],
    high=data['high'],
    low=data['low'],
    close=data['close'],
    name='Price',
    ), row=2, col=1,
)

fig.add_trace(go.Bar(
    x=data['date'],
    y=data['volume'],
    name='Volume',),
    row=1, col=1,
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
        line=dict(width=2, color='pink'),
        name='fast',
    ), row=3, col=1  #  <------------ lower chart %d
)
fig.append_trace(
    go.Scatter(
        x=data.index,
        y=data['STOCHd_14_3_3'],
        line=dict(width=2, color='purple'),
        name='slow'
    ), row=3, col=1 #  <------------ lower chart
)
#Creating moving Average

data['MA1'] = data.close.rolling(mav1).mean()
data['MA2'] = data.close.rolling(mav2).mean()


fig.append_trace(
    go.Scatter(
        x=data.index,
        y=data.MA1,
        line=dict(color='white', width=1),
        name=f'MA {mav1}'),
        row=2, col=1)

fig.append_trace(
    go.Scatter(
        x=data.index,
        y=data.MA2,
        line=dict(color='grey', width=1),
        name=f'MA {mav2}'),
        row=2, col=1)




# Add overbought/oversold
fig.add_hline(y=20, col=1, row=3, line_color='#336699', line_width=2, line_dash='dash') # type: ignore
fig.add_hline(y=80, col=1, row=3, line_color='#336699', line_width=2, line_dash='dash') # type: ignore

# Add MAVs


fig.update_layout(
        title={
        'text': f'Graficas de {symbol}',
        'font': {'size': 25}},
        width=800, height=800)

fig.update_yaxes(title_text = "Volume", row=1, col=1)
fig.update_yaxes(title_text = "OHLC", row=2, col=1)
fig.update_yaxes(title_text = "Stocastic", row=3, col=1)

st.plotly_chart(fig)
if show_data:
    st.markdown('---')
    st.subheader('Data')
    st.dataframe(data)