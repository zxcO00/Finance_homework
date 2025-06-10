# -*- coding: utf-8 -*-
"""
金融資料視覺化看板 (自動讀取多檔 .pkl，並呈現 K 棒、MA、RSI、Bollinger 通道、MACD，並支援策略模擬與績效回測)
"""

import os
import glob
import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1 as stc
import datetime
import matplotlib.pyplot as plt
from order_streamlit import Record
import indicator_f_Lo2_short
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ──────────────────────────────────────────────────────────────────────────────
# 網頁標題
html_temp = """
    <div style="background-color:#3872fb;padding:10px;border-radius:10px">   
    <h1 style="color:white;text-align:center;">金融看板與程式交易平台 </h1>
    <h2 style="color:white;text-align:center;">Financial Dashboard and Program Trading </h2>
    </div>
    """
stc.html(html_temp)

# ──────────────────────────────────────────────────────────────────────────────
# 自動尋找所有 .pkl 檔案
@st.cache_data(ttl=3600)
def find_all_pkl_files():
    data_folder = './'
    pkl_files = glob.glob(os.path.join(data_folder, '*.pkl'))
    file_display_names = []
    file_lookup = {}
    for filepath in pkl_files:
        filename = os.path.basename(filepath)
        if filename.startswith("stock_KBar_") or filename.startswith("future_KBar_"):
            display_name = filename \
                .replace("stock_KBar_", "股票：") \
                .replace("future_KBar_", "期貨：") \
                .replace(".pkl", "")
            file_display_names.append(display_name)
            file_lookup[display_name] = filepath
    return file_display_names, file_lookup

# 載入資料
@st.cache_data(ttl=3600, show_spinner="正在加載資料...")
def load_data(path):
    return pd.read_pickle(path)

# ──────────────────────────────────────────────────────────────────────────────
# 選擇商品與載入原始資料
file_display_names, file_lookup = find_all_pkl_files()
choice = st.selectbox("選擇金融商品與資料區間", file_display_names)
selected_file = file_lookup[choice]
df_original = load_data(selected_file)

# 從檔名抓商品代碼
file_parts = os.path.basename(selected_file).replace(".pkl", "").split("_")
product_name = file_parts[2]
df_original['time'] = pd.to_datetime(df_original['time'])

# ──────────────────────────────────────────────────────────────────────────────
# 選擇日期區間
st.subheader("選擇資料時間區間")
all_dates = sorted(df_original['time'].dt.date.unique())
start_date = st.date_input("開始日期", value=all_dates[0], min_value=all_dates[0], max_value=all_dates[-1])
end_date   = st.date_input("結束日期", value=all_dates[-1], min_value=start_date,   max_value=all_dates[-1])
df = df_original[(df_original['time'] >= pd.to_datetime(start_date)) &
                 (df_original['time'] <= pd.to_datetime(end_date))]

# 限制最多顯示最近500筆
if len(df) > 500:
    df = df.iloc[-500:]

# ──────────────────────────────────────────────────────────────────────────────
# 轉為技術分析用字典
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
KBar_df  = pd.DataFrame({
    'time':   KBar_dic['time'],
    'open':   KBar_dic['open'],
    'high':   KBar_dic['high'],
    'low':    KBar_dic['low'],
    'close':  KBar_dic['close'],
    'volume': KBar_dic['volume']
})

# ──────────────────────────────────────────────────────────────────────────────
# 資料摘要
st.subheader("資料預覽")
st.write("筆數：", len(KBar_df))
st.write("時間範圍：", KBar_df['time'].iloc[0], "～", KBar_df['time'].iloc[-1])
st.dataframe(KBar_df.head())

# ──────────────────────────────────────────────────────────────────────────────
# (策略模擬 + 績效回測)
st.subheader("策略模擬：移動平均交叉")
short_window = st.slider("短期 MA 週期", 2, 30, 5)
long_window = st.slider("長期 MA 週期", 10, 60, 20)

KBar_df['short_ma'] = KBar_df['close'].rolling(window=short_window).mean()
KBar_df['long_ma'] = KBar_df['close'].rolling(window=long_window).mean()

KBar_df['signal'] = 0
KBar_df.loc[short_window:, 'signal'] = np.where(
    KBar_df['short_ma'][short_window:] > KBar_df['long_ma'][short_window:], 1, 0
)
KBar_df['position'] = KBar_df['signal'].diff()

KBar_df['return'] = KBar_df['close'].pct_change()
KBar_df['strategy_return'] = KBar_df['signal'].shift(1) * KBar_df['return']
KBar_df['cum_strategy_return'] = (1 + KBar_df['strategy_return']).cumprod()
KBar_df['cum_market_return'] = (1 + KBar_df['return']).cumprod()

fig_perf = go.Figure()
fig_perf.add_trace(go.Scatter(x=KBar_df['time'], y=KBar_df['cum_market_return'], name='市場報酬'))
fig_perf.add_trace(go.Scatter(x=KBar_df['time'], y=KBar_df['cum_strategy_return'], name='策略報酬'))
fig_perf.update_layout(title='績效回測：累積報酬', xaxis_title='時間', yaxis_title='報酬')
st.plotly_chart(fig_perf, use_container_width=True)

st.write("最終策略報酬：", round(KBar_df['cum_strategy_return'].iloc[-1], 4))
st.write("最終市場報酬：", round(KBar_df['cum_market_return'].iloc[-1], 4))
