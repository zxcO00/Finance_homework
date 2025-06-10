import os
import glob
import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1 as stc
import datetime
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import indicator_f_Lo2_short
from order_streamlit import Record

# 已整合的策略模組
from streamlit_ma_strategy import render_ma_strategy_ui
from streamlit_rsi_strategy import render_rsi_strategy_ui
from streamlit_macd_bb_strategy import render_macd_strategy_ui, render_bb_strategy_ui

# ──────────────────────────────── 網頁標題區 ────────────────────────────────
html_temp = """
    <div style="background-color:#3872fb;padding:10px;border-radius:10px">   
    <h1 style="color:white;text-align:center;">金融看板與程式交易平台 </h1>
    <h2 style="color:white;text-align:center;">Financial Dashboard and Program Trading </h2>
    </div>
    """
stc.html(html_temp)

# ──────────────────────────────── 資料載入區 ────────────────────────────────
@st.cache_data(ttl=3600)
def find_all_pkl_files():
    data_folder = './'
    pkl_files = glob.glob(os.path.join(data_folder, '*.pkl'))
    file_display_names = []
    file_lookup = {}
    for filepath in pkl_files:
        filename = os.path.basename(filepath)
        if filename.startswith("stock_KBar_") or filename.startswith("future_KBar_"):
            display_name = filename.replace("stock_KBar_", "股票：").replace("future_KBar_", "期貨：").replace(".pkl", "")
            file_display_names.append(display_name)
            file_lookup[display_name] = filepath
    return file_display_names, file_lookup

@st.cache_data(ttl=3600, show_spinner="正在加載資料...")
def load_data(path):
    return pd.read_pickle(path)

file_display_names, file_lookup = find_all_pkl_files()
choice = st.selectbox("選擇金融商品與資料區間", file_display_names)
selected_file = file_lookup[choice]
df_original = load_data(selected_file)

file_parts = os.path.basename(selected_file).replace(".pkl", "").split("_")
product_name = file_parts[2]
df_original['time'] = pd.to_datetime(df_original['time'])

# ──────────────────────────────── 日期選擇區 ────────────────────────────────
st.subheader("選擇資料時間區間")
all_dates = sorted(df_original['time'].dt.date.unique())
start_date = st.date_input("開始日期", value=all_dates[0], min_value=all_dates[0], max_value=all_dates[-1])
end_date = st.date_input("結束日期", value=all_dates[-1], min_value=start_date, max_value=all_dates[-1])
df = df_original[(df_original['time'] >= pd.to_datetime(start_date)) & (df_original['time'] <= pd.to_datetime(end_date))]

# 資料過長時限縮顯示
if len(df) > 500:
    df = df.iloc[-500:]

# ──────────────────────────────── K 線資料轉換 ────────────────────────────────
@st.cache_data(ttl=3600)
def To_Dictionary(df, product_name):
    d = df.to_dict()
    K = {
        'time':   np.array([t.to_pydatetime() for t in d['time'].values()]),
        'open':   np.array(list(d['open'].values())),
        'high':   np.array(list(d['high'].values())),
        'low':    np.array(list(d['low'].values())),
        'close':  np.array(list(d['close'].values())),
        'volume': np.array(list(d['volume'].values())),
        'amount': np.array(list(d['amount'].values())),
        'product': np.repeat(product_name, len(d['time']))
    }
    return K

KBar_dic = To_Dictionary(df, product_name)
KBar_df = pd.DataFrame({
    'time':   KBar_dic['time'],
    'open':   KBar_dic['open'],
    'high':   KBar_dic['high'],
    'low':    KBar_dic['low'],
    'close':  KBar_dic['close'],
    'volume': KBar_dic['volume']
})

# ──────────────────────────────── 資料預覽區 ────────────────────────────────
st.subheader("資料預覽")
st.write("筆數：", len(KBar_df))
st.write("時間範圍：", KBar_df['time'].iloc[0], "～", KBar_df['time'].iloc[-1])
st.dataframe(KBar_df.head())

# ──────────────────────────────── K 線圖顯示 ────────────────────────────────
st.subheader("K 線圖與成交量")
try:
    fig_candle = indicator_f_Lo2_short.CandlePlot(KBar_dic)
    st.pyplot(fig_candle)
except Exception as e:
    st.error(f"K 線圖繪製失敗：{e}")

# ──────────────────────────────── 策略模擬區 ────────────────────────────────
with st.expander("📊 策略交易模擬 - MA 移動平均交叉"):
    render_ma_strategy_ui(KBar_df)

with st.expander("📉 策略交易模擬 - RSI 超買超賣"):
    render_rsi_strategy_ui(KBar_df)

with st.expander("📈 策略交易模擬 - MACD 差離交叉"):
    render_macd_strategy_ui(KBar_df)

with st.expander("📉 策略交易模擬 - 布林通道突破"):
    render_bb_strategy_ui(KBar_df)
