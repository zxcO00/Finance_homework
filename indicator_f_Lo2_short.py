# -*- coding: utf-8 -*-
"""
技術指標模組 - 簡易版本
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# K 線圖與移動平均線

def CandlePlot(ax, Data):
    time = Data['time']
    open_ = Data['open']
    close = Data['close']
    high = Data['high']
    low = Data['low']

    # 繪製K棒
    for i in range(len(time)):
        color = 'red' if close[i] >= open_[i] else 'green'
        ax.plot([time[i], time[i]], [low[i], high[i]], color=color)
        ax.plot([time[i], time[i]], [open_[i], close[i]], linewidth=6, color=color)

    # 設定時間格式
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.set_title('K 線圖')
    ax.set_xlabel('日期')
    ax.set_ylabel('價格')
    ax.grid(True)

    # 計算移動平均線
    close_series = np.array(close)
    MA5 = np.convolve(close_series, np.ones(5)/5, mode='valid')
    MA20 = np.convolve(close_series, np.ones(20)/20, mode='valid')
    time_np = np.array(time)

    # 移動平均線起始時間要對齊資料長度
    ax.plot(time_np[4:], MA5, label='MA5', color='blue', linestyle='--')
    ax.plot(time_np[19:], MA20, label='MA20', color='orange', linestyle='--')

    ax.legend()


# 可在此加入其他指標函式...
