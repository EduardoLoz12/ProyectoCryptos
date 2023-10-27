from datetime import date, datetime
import streamlit as st
import pandas as pd
import mplfinance as mpf
import krakenex
from pykrakenapi import KrakenAPI
import time

# hola Eduardo

st.cache_data(persist='disk')
api = krakenex.API()
q=KrakenAPI(api)

def make_graph():
    api = krakenex.API()
    k = KrakenAPI(api)
    x = symbol
    data1, last = k.get_ohlc_data(x,1440, since=unixtime)
    crypto1 =data1.drop(['time','vwap','count'], axis=1)
    crypto1.index.name = 'Date'

    #Creando el indicador "oscilador estocastico"

    crypto1["Stocastic"]= (crypto1["close"]-crypto1["low"])*100/(crypto1["high"]-crypto1["low"])



    #La funcion mpf necesita datos numericos para graficas. En esta parte logro ese objetivo

    for i, col in crypto1.items():
        crypto1[i] = pd.to_numeric(col, errors='coerce')
    return crypto1


st.title('Graphic Machine')

monedas = q.get_tradable_asset_pairs()
monedas = monedas["altname"].unique()

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


data = make_graph()
print(data)

mystyle = mpf.make_mpf_style(rc={'axes.labelsize': 'medium'})
stocast = mpf.make_addplot(data["Stocastic"], panel=2, ylabel="Stocastic", color="brown", mav=(int(mav1),int(mav2),int(mav3)))
fig, ax = mpf.plot(data, type="candle", volume=True, datetime_format="%B-%y",
                   addplot=stocast, main_panel=1, volume_panel=0, xrotation=90, fontscale=0.8, figscale=0.8,
                   style=chart_style, returnfig=True, show_nontrading=show_nontrading_days)

fig.suptitle(f"Analazing {symbol} from {datefrom}")
st.pyplot(fig)

if show_data:
    st.markdown('---')
    st.dataframe(data)