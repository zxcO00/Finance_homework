# -*- coding: utf-8 -*-
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

# 網頁標題
html_temp = """
    <div style="background-color:#3872fb;padding:10px;border-radius:10px">   
    <h1 style="color:white;text-align:center;">金融看板與程式交易平台 </h1>
    <h2 style="color:white;text-align:center;">Financial Dashboard and Program Trading </h2>
    </div>
    """
stc.html(html_temp)

# 自動找所有 .pkl 檔案
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

# 選擇商品
file_display_names, file_lookup = find_all_pkl_files()
choice = st.selectbox("選擇金融商品與資料區間", file_display_names)
selected_file = file_lookup[choice]
df_original = load_data(selected_file)

# 從檔名抓商品代碼與日期
file_parts = os.path.basename(selected_file).replace(".pkl", "").split("_")
product_name = file_parts[2]
df_original['time'] = pd.to_datetime(df_original['time'])

# 日期選擇
st.subheader("選擇資料時間區間")
all_dates = sorted(df_original['time'].dt.date.unique())
start_date = st.date_input("選擇開始日期", value=all_dates[0], min_value=all_dates[0], max_value=all_dates[-1])
end_date = st.date_input("選擇結束日期", value=all_dates[-1], min_value=start_date, max_value=all_dates[-1])

# 篩選日期區間
df = df_original[(df_original['time'] >= pd.to_datetime(start_date)) & (df_original['time'] <= pd.to_datetime(end_date))]

# ✅ 限制顯示最近 500 筆
if len(df) > 500:
    df = df.iloc[-500:]

# 轉換為字典格式
@st.cache_data(ttl=3600)
def To_Dictionary(df, product_name):
    KBar_dic = df.to_dict()
    KBar_dic['open'] = np.array(list(KBar_dic['open'].values()))
    KBar_dic['product'] = np.repeat(product_name, len(KBar_dic['open']))
    KBar_dic['time'] = np.array([t.to_pydatetime() for t in list(KBar_dic['time'].values())])
    KBar_dic['low'] = np.array(list(KBar_dic['low'].values()))
    KBar_dic['high'] = np.array(list(KBar_dic['high'].values()))
    KBar_dic['close'] = np.array(list(KBar_dic['close'].values()))
    KBar_dic['volume'] = np.array(list(KBar_dic['volume'].values()))
    KBar_dic['amount'] = np.array(list(KBar_dic['amount'].values()))
    return KBar_dic

KBar_dic = To_Dictionary(df, product_name)

# 資料摘要
st.subheader("資料預覽")
st.write("目前資料筆數：", len(KBar_dic['time']))
st.write("時間範圍：", KBar_dic['time'][0], "~", KBar_dic['time'][-1])
st.write(df.head())

# K線圖畫圖區塊
st.subheader("K 線圖與成交量")
try:
    fig = indicator_f_Lo2_short.CandlePlot(KBar_dic)
    st.pyplot(fig)
except Exception as e:
    st.error(f"畫圖失敗：{e}")

# 測試圖表
st.subheader("測試圖表")
test_fig, test_ax = plt.subplots()
test_ax.plot(np.arange(10), np.random.rand(10))
st.pyplot(test_fig)
