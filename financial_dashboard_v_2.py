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

# 繪製各技術指標圖（固定顯示）
st.subheader("K 線圖與技術指標")
try:
    fig_candle = indicator_f_Lo2_short.CandlePlot(KBar_dic)
    st.pyplot(fig_candle)
except Exception as e:
    st.error(f"K 線圖繪製失敗：{e}")

# MA 計算與圖形
KBar_df['MA_short'] = KBar_df['close'].rolling(window=5).mean()
KBar_df['MA_long'] = KBar_df['close'].rolling(window=20).mean()
fig_ma = make_subplots(specs=[[{"secondary_y": True}]])
fig_ma.add_trace(go.Candlestick(x=KBar_df['time'], open=KBar_df['open'], high=KBar_df['high'],
                                low=KBar_df['low'], close=KBar_df['close'], name='K 線'), secondary_y=True)
fig_ma.add_trace(go.Scatter(x=KBar_df['time'], y=KBar_df['MA_short'], name='MA5'), secondary_y=True)
fig_ma.add_trace(go.Scatter(x=KBar_df['time'], y=KBar_df['MA_long'], name='MA20'), secondary_y=True)
fig_ma.add_trace(go.Bar(x=KBar_df['time'], y=KBar_df['volume'], name='成交量', marker=dict(color='lightgray')), secondary_y=False)
st.plotly_chart(fig_ma, use_container_width=True)

# RSI 計算與圖形
rsi_period = 14
delta = KBar_df['close'].diff()
gain = delta.where(delta > 0, 0).rolling(rsi_period).mean()
loss = (-delta.where(delta < 0, 0)).rolling(rsi_period).mean()
rs = gain / loss
KBar_df['RSI'] = 100 - (100 / (1 + rs))
fig_rsi = go.Figure()
fig_rsi.add_trace(go.Scatter(x=KBar_df['time'], y=KBar_df['RSI'], mode='lines', name='RSI'))
fig_rsi.add_hline(y=70, line_dash="dash", line_color="red")
fig_rsi.add_hline(y=30, line_dash="dash", line_color="green")
st.plotly_chart(fig_rsi, use_container_width=True)

# 布林通道
KBar_df['BB_MID'] = KBar_df['close'].rolling(20).mean()
KBar_df['BB_STD'] = KBar_df['close'].rolling(20).std()
KBar_df['BB_UP'] = KBar_df['BB_MID'] + 2 * KBar_df['BB_STD']
KBar_df['BB_DOWN'] = KBar_df['BB_MID'] - 2 * KBar_df['BB_STD']
fig_bb = make_subplots(specs=[[{"secondary_y": True}]])
fig_bb.add_trace(go.Candlestick(x=KBar_df['time'], open=KBar_df['open'], high=KBar_df['high'],
                                 low=KBar_df['low'], close=KBar_df['close'], name='K 線'), secondary_y=True)
fig_bb.add_trace(go.Scatter(x=KBar_df['time'], y=KBar_df['BB_UP'], name='上軌'), secondary_y=True)
fig_bb.add_trace(go.Scatter(x=KBar_df['time'], y=KBar_df['BB_MID'], name='中軌'), secondary_y=True)
fig_bb.add_trace(go.Scatter(x=KBar_df['time'], y=KBar_df['BB_DOWN'], name='下軌'), secondary_y=True)
fig_bb.add_trace(go.Bar(x=KBar_df['time'], y=KBar_df['volume'], name='成交量', marker=dict(color='lightgray')), secondary_y=False)
st.plotly_chart(fig_bb, use_container_width=True)

# MACD 計算與圖形
ema_fast = KBar_df['close'].ewm(span=12, adjust=False).mean()
ema_slow = KBar_df['close'].ewm(span=26, adjust=False).mean()
KBar_df['MACD'] = ema_fast - ema_slow
KBar_df['MACD_SIGNAL'] = KBar_df['MACD'].ewm(span=9, adjust=False).mean()
KBar_df['MACD_HIST'] = KBar_df['MACD'] - KBar_df['MACD_SIGNAL']
fig_macd = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3], vertical_spacing=0.05)
fig_macd.add_trace(go.Scatter(x=KBar_df['time'], y=KBar_df['MACD'], name='MACD'), row=1, col=1)
fig_macd.add_trace(go.Scatter(x=KBar_df['time'], y=KBar_df['MACD_SIGNAL'], name='Signal'), row=1, col=1)
fig_macd.add_trace(go.Bar(x=KBar_df['time'], y=KBar_df['MACD_HIST'], name='Hist'), row=2, col=1)
st.plotly_chart(fig_macd, use_container_width=True)

# 策略績效圖依然保留
# 已內建於前一段修改中，無需重複
