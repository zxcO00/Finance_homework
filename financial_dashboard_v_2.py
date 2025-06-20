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
            display_name = filename                 .replace("stock_KBar_", "股票：")                 .replace("future_KBar_", "期貨：")                 .replace(".pkl", "")
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

# ──────────────────────────────────────────────────────────────────────────────
# 限制最多顯示最近500筆
#if len(df) > 500:
#    df = df.iloc[-500:]
#

# 資料筆數上限（使用者輸入）與提醒
st.subheader("設定顯示的資料筆數上限")
max_rows = st.number_input("輸入最大筆數（最近幾筆資料）", min_value=100, max_value=2000, value=500, step=100)

# 顯示提示：過多資料可能造成顯示問題
if max_rows > 1500:
    st.warning("⚠️ 警告：資料筆數過多可能導致圖表無法顯示或系統卡頓，建議不要超過 1500 筆！")

# 限制最多顯示 max_rows 筆資料（從尾端開始）
if len(df) > max_rows:
    df = df.iloc[-int(max_rows):]

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
# K 線圖與成交量
st.subheader("K 線圖與成交量")
try:
    fig_candle = indicator_f_Lo2_short.CandlePlot(KBar_dic)
    st.pyplot(fig_candle)
except Exception as e:
    st.error(f"K 線圖繪製失敗：{e}")

# 移動平均線 MA
st.subheader("移動平均線 (MA)")
ma_long  = st.slider("長期 MA 週期", 1, 60, 20, key='ma_long')
ma_short = st.slider("短期 MA 週期", 1, 60, 5,  key='ma_short')
KBar_df['MA_long']  = KBar_df['close'].rolling(window=ma_long).mean()
KBar_df['MA_short'] = KBar_df['close'].rolling(window=ma_short).mean()
fig_ma = make_subplots(specs=[[{"secondary_y": True}]])
fig_ma.add_trace(go.Candlestick(x=KBar_df['time'], open=KBar_df['open'], high=KBar_df['high'],
                                low=KBar_df['low'], close=KBar_df['close'], name='K 線'), secondary_y=True)
fig_ma.add_trace(go.Scatter(x=KBar_df['time'], y=KBar_df['MA_long'], mode='lines', name=f'MA {ma_long}'), secondary_y=True)
fig_ma.add_trace(go.Scatter(x=KBar_df['time'], y=KBar_df['MA_short'], mode='lines', name=f'MA {ma_short}'), secondary_y=True)
fig_ma.add_trace(go.Bar(x=KBar_df['time'], y=KBar_df['volume'], name='成交量', marker=dict(color='lightgray')), secondary_y=False)
fig_ma.update_layout(yaxis2_title="價格", yaxis_title="成交量")
st.plotly_chart(fig_ma, use_container_width=True)

# RSI
st.subheader("相對強弱指標 (RSI)")
rsi_period = st.slider("RSI 週期", 2, 30, 14, key='rsi')
delta = KBar_df['close'].diff()
gain  = delta.where(delta>0, 0).rolling(window=rsi_period).mean()
loss  = (-delta.where(delta<0, 0)).rolling(window=rsi_period).mean()
rs    = gain / loss
KBar_df['RSI'] = 100 - (100 / (1 + rs))
fig_rsi = go.Figure()
fig_rsi.add_trace(go.Scatter(x=KBar_df['time'], y=KBar_df['RSI'], mode='lines', name='RSI'))
fig_rsi.add_hline(y=70, line_dash="dash", line_color="red")
fig_rsi.add_hline(y=30, line_dash="dash", line_color="green")
fig_rsi.update_layout(yaxis_title="RSI 值", xaxis_title="時間")
st.plotly_chart(fig_rsi, use_container_width=True)

# 布林通道
st.subheader("布林通道 (Bollinger Bands)")
bb_period = st.slider("布林通道週期", 5, 60, 20, key='bb_period')
bb_std    = st.slider("標準差倍數", 1.0, 3.0, 2.0, step=0.1, key='bb_std')
KBar_df['BB_MID']  = KBar_df['close'].rolling(window=bb_period).mean()
KBar_df['BB_STD']  = KBar_df['close'].rolling(window=bb_period).std()
KBar_df['BB_UP']   = KBar_df['BB_MID'] + bb_std * KBar_df['BB_STD']
KBar_df['BB_DOWN'] = KBar_df['BB_MID'] - bb_std * KBar_df['BB_STD']
fig_bb = make_subplots(specs=[[{"secondary_y": True}]])
fig_bb.add_trace(go.Candlestick(x=KBar_df['time'], open=KBar_df['open'], high=KBar_df['high'],
                                low=KBar_df['low'], close=KBar_df['close'], name='K 線'), secondary_y=True)
fig_bb.add_trace(go.Scatter(x=KBar_df['time'], y=KBar_df['BB_MID'], mode='lines', name='中軌'), secondary_y=True)
fig_bb.add_trace(go.Scatter(x=KBar_df['time'], y=KBar_df['BB_UP'], mode='lines', name='上軌'), secondary_y=True)
fig_bb.add_trace(go.Scatter(x=KBar_df['time'], y=KBar_df['BB_DOWN'], mode='lines', name='下軌'), secondary_y=True)
fig_bb.add_trace(go.Bar(x=KBar_df['time'], y=KBar_df['volume'], name='成交量', marker=dict(color='lightgray')), secondary_y=False)
fig_bb.update_layout(yaxis2_title="價格", yaxis_title="成交量")
st.plotly_chart(fig_bb, use_container_width=True)

# MACD
st.subheader("異同移動平均線 (MACD)")
fastp = st.slider("MACD 快線", 5, 30, 12, key='macd_fast')
slowp = st.slider("MACD 慢線", 10, 60, 26, key='macd_slow')
sigp  = st.slider("MACD 訊號線", 5, 20, 9, key='macd_sig')
ema_fast = KBar_df['close'].ewm(span=fastp, adjust=False).mean()
ema_slow = KBar_df['close'].ewm(span=slowp, adjust=False).mean()
KBar_df['MACD']       = ema_fast - ema_slow
KBar_df['MACD_SIGNAL'] = KBar_df['MACD'].ewm(span=sigp, adjust=False).mean()
KBar_df['MACD_HIST']  = KBar_df['MACD'] - KBar_df['MACD_SIGNAL']
fig_macd = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3], vertical_spacing=0.05)
fig_macd.add_trace(go.Scatter(x=KBar_df['time'], y=KBar_df['MACD'], mode='lines', name='MACD'), row=1, col=1)
fig_macd.add_trace(go.Scatter(x=KBar_df['time'], y=KBar_df['MACD_SIGNAL'], mode='lines', name='Signal'), row=1, col=1)
fig_macd.add_trace(go.Bar(x=KBar_df['time'], y=KBar_df['MACD_HIST'], name='Histogram', marker=dict(color='gray')), row=2, col=1)
fig_macd.update_layout(yaxis_title="MACD", yaxis2_title="Histogram", xaxis_title="時間")
st.plotly_chart(fig_macd, use_container_width=True)

# ──────────────────────────────────────────────────────────────────────────────
# 策略模擬與績效回測
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


#st.write("最終策略報酬：", f"{round(KBar_df['cum_strategy_return'].iloc[-1] * 100, 2)}%")
#st.write("最終市場報酬：", f"{round(KBar_df['cum_market_return'].iloc[-1] * 100, 2)}%")

st.success(f"最終策略報酬：{(KBar_df['cum_strategy_return'].iloc[-1] - 1) * 100:.2f}%")
st.info(f"最終市場報酬：{(KBar_df['cum_market_return'].iloc[-1] - 1) * 100:.2f}%")


# ──────────────────────────────────────────────────────────────────────────────
# RSI 策略模擬與績效回測
st.subheader("策略模擬：RSI 策略（超賣買進，超買賣出）")

rsi_buy_thres = st.slider("超賣進場（低於）", 5, 50, 30, key='rsi_buy')
rsi_sell_thres = st.slider("超買出場（高於）", 50, 95, 70, key='rsi_sell')

KBar_df['rsi_signal'] = 0
KBar_df.loc[KBar_df['RSI'] < rsi_buy_thres, 'rsi_signal'] = 1   # 進場
KBar_df.loc[KBar_df['RSI'] > rsi_sell_thres, 'rsi_signal'] = 0  # 出場
KBar_df['rsi_signal'] = KBar_df['rsi_signal'].ffill()  # 持倉訊號延續

KBar_df['rsi_strat_return'] = KBar_df['rsi_signal'].shift(1) * KBar_df['return']
KBar_df['cum_rsi_strat_return'] = (1 + KBar_df['rsi_strat_return']).cumprod()

fig_rsi_perf = go.Figure()
fig_rsi_perf.add_trace(go.Scatter(x=KBar_df['time'], y=KBar_df['cum_market_return'], name='市場報酬'))
fig_rsi_perf.add_trace(go.Scatter(x=KBar_df['time'], y=KBar_df['cum_rsi_strat_return'], name='RSI 策略報酬'))
fig_rsi_perf.update_layout(title='RSI 策略績效：累積報酬', xaxis_title='時間', yaxis_title='報酬')
st.plotly_chart(fig_rsi_perf, use_container_width=True)


#st.write("最終 RSI 策略報酬：", f"{round(KBar_df['cum_rsi_strat_return'].iloc[-1] * 100, 2)}%")

st.success(f"最終 RSI 策略報酬：{(KBar_df['cum_rsi_strat_return'].iloc[-1] - 1) * 100:.2f}%")
