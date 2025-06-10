# -*- coding: UTF-8 -*-
# 載入相關套件
import numpy, datetime
import pandas as pd
import mplfinance as mpf

# 🔹 補上畫圖函式：K 線圖用
def CandlePlot(ax, KBar_dic):
    df = pd.DataFrame({
        'Open': KBar_dic['open'],
        'High': KBar_dic['high'],
        'Low': KBar_dic['low'],
        'Close': KBar_dic['close'],
        'Volume': KBar_dic['volume']
    }, index=pd.to_datetime(KBar_dic['time']))
    mpf.plot(df, type='candle', volume=True, ax=ax, style='charles')

# K線指標class
# 參數 型態(1:'time' , 2:'volume') 週期
class KBar():
    def __init__(self, date, type='time', cycle=1):
        if type == 'time':
            # 定義週期
            self.Cycle = datetime.timedelta(minutes=cycle)
            self.StartTime = datetime.datetime.strptime(date + '084500', '%Y%m%d%H%M%S') - (self.Cycle * 2)
            self.Time = numpy.array([self.StartTime])
            self.Open = numpy.array([0])
            self.High = numpy.array([0])
            self.Low = numpy.array([10000000000000])
            self.Close = numpy.array([0])
            self.Volume = numpy.array([0])
            self.Prod = numpy.array([''])
            self.flag = 0
        elif type == 'volume':
            self.Cycle = cycle
            self.Amount = 0
            self.Open = numpy.array([])
            self.High = numpy.array([])
            self.Low = numpy.array([])
            self.Close = numpy.array([])

    def TimeAdd(self, time, price, qty, prod):
        while self.flag == 0 and time >= self.StartTime:
            self.Time[-1] = self.StartTime
            self.StartTime += self.Cycle
        self.flag = 1
        if time < self.Time[-1] + self.Cycle:
            self.Close[-1] = price
            self.Volume[-1] += qty
            if price > self.High[-1]:
                self.High[-1] = price
            elif price < self.Low[-1]:
                self.Low[-1] = price
            return 0
        elif time >= self.Time[-1] + self.Cycle:
            self.Time = numpy.append(self.Time, self.Time[-1] + self.Cycle)
            self.Open = numpy.append(self.Open, price)
            self.High = numpy.append(self.High, price)
            self.Low = numpy.append(self.Low, price)
            self.Close = numpy.append(self.Close, price)
            self.Volume = numpy.append(self.Volume, qty)
            self.Prod = numpy.append(self.Prod, prod)
            return 1

    def VolumeAdd(self, price, amount):
        if self.Amount == 0:
            self.Open = numpy.append(self.Open, price)
            self.High = numpy.append(self.High, price)
            self.Low = numpy.append(self.Low, price)
            self.Close = numpy.append(self.Close, price)
            self.Amount = amount
        elif amount - self.Amount < self.Cycle:
            self.Close[-1] = price
            if price > self.High[-1]:
                self.High[-1] = price
            elif price < self.Low[-1]:
                self.Low[-1] = price
            return 0
        elif amount - self.Amount > self.Cycle:
            self.Open = numpy.append(self.Open, price)
            self.High = numpy.append(self.High, price)
            self.Low = numpy.append(self.Low, price)
            self.Close = numpy.append(self.Close, price)
            self.Amount = amount
            return 1

# ⬇️ 其他類別略（若需要可補充，如 BigOrder、BSPower 等）
