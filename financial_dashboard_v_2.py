# -*- coding: utf-8 -*-
"""
金融資料視覺化看板 (自動讀取多檔 .pkl)
"""

# 載入必要模組
import os
import glob
import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1 as stc
import datetime
import matplotlib.pyplot as plt
from order_streamlit import Record
import indicator_forKBar_short

# 設定網頁標題
html_temp = """
    <div style="background-color:#3872fb;padding:10px;border-radius:10px">   
    <h1 style="color:white;text-align:center;">金融看板與程式交易平台 </h1>
    <h2 style="color:white;text-align:center;">Financial Dashboard and Program Trading </h2>
    </div>
    """
stc.html(html_temp)

# 自動尋找所有 pkl 檔案
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

# 載入資料函式
@st.cache_data(ttl=3600, show_spinner="正在加載資料...")
def load_data(path):
    return pd.read_pickle(path)

# 讀取所有檔案並顯示選單
file_display_names, file_lookup = find_all_pkl_files()
choice = st.selectbox("選擇金融商品與資料區間", file_display_names)
selected_file = file_lookup[choice]
df_original = load_data(selected_file)

# 從檔名取得商品名稱與起訖日期
file_parts = os.path.basename(selected_file).replace(".pkl", "").split("_")
product_name = file_parts[2]  # 如 '2330'
start_date_str = file_parts[3]
end_date_str = file_parts[4]

# 日期選擇
st.subheader("選擇資料時間區間")
# 從資料中擷取所有日期並轉為字串格式
all_dates = df_original['time'].dt.strftime('%Y-%m-%d').unique().tolist()
all_dates.sort()

# 選擇起訖日期（用下拉選單）
start_date_str = st.selectbox("選擇開始日期", all_dates, index=0)
filtered_end_dates = [d for d in all_dates if d >= start_date_str]
end_date_str = st.selectbox("選擇結束日期", filtered_end_dates, index=len(filtered_end_dates)-1)

# 轉回 datetime 格式
start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d')
end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d')

# 修正：確保 time 欄位為 datetime 格式
df_original['time'] = pd.to_datetime(df_original['time'])

# 篩選資料區間
df = df_original[(df_original['time'] >= start_date) & (df_original['time'] <= end_date)]

# 轉成字典格式供技術分析模組使用
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

# 顯示預覽
st.subheader("資料預覽")
st.write(df.head())

# 更多功能（如技術指標、程式交易）可依需求加入...
