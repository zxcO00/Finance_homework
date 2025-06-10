# 載入必要套件
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.dates as mdates
# from haohaninfo.MicroTest import microtest_db
import numpy as np
# import haohaninfo,time
import time
import streamlit as st

# 下單部位管理物件
class Record():
    def __init__(self ):   ## 建構子
        # 儲存績效
        self.Profit=[]
        self.Profit_rate=[]
        # 未平倉
        self.OpenInterestQty=0
        self.OpenInterest=[]
        # 交易紀錄總計
        self.TradeRecord=[]
    # 進場紀錄
    def Order(self, BS,Product,OrderTime,OrderPrice,OrderQty):
        if BS=='B' or BS=='Buy':
            for i in range(OrderQty):
                self.OpenInterest.append([1,Product,OrderTime,OrderPrice])
                self.OpenInterestQty +=1
        elif BS=='S' or BS=='Sell':
            for i in range(OrderQty):
                self.OpenInterest.append([-1,Product,OrderTime,OrderPrice])
                self.OpenInterestQty -=1
    # 出場紀錄(買賣別需與進場相反，多單進場則空單出場)
    def Cover(self, BS,Product,CoverTime,CoverPrice,CoverQty):
        if BS=='S' or BS=='Sell':
            for i in range(CoverQty):
                # 取得多單未平倉部位
                TmpInterest=[ i for i in self.OpenInterest if i[0]==1 ][0]
                if TmpInterest != []:
                    # 清除未平倉紀錄
                    self.OpenInterest.remove(TmpInterest)
                    self.OpenInterestQty -=1
                    # 新增交易紀錄
                    self.TradeRecord.append(['B',TmpInterest[1],TmpInterest[2],TmpInterest[3],CoverTime,CoverPrice])
                    self.Profit.append(CoverPrice-TmpInterest[3])
                    self.Profit_rate.append((CoverPrice-TmpInterest[3])/TmpInterest[3])
                else:
                    print('尚無進場')
        elif BS=='B' or BS=='Buy':
            for i in range(CoverQty):
                # 取得空單未平倉部位
                TmpInterest=[ i for i in self.OpenInterest if i[0]==-1 ][0]
                if TmpInterest != []:
                    # 清除未平倉紀錄
                    self.OpenInterest.remove(TmpInterest)
                    self.OpenInterestQty +=1
                    # 新增交易紀錄
                    self.TradeRecord.append(['S',TmpInterest[1],TmpInterest[2],TmpInterest[3],CoverTime,CoverPrice])
                    self.Profit.append(TmpInterest[3]-CoverPrice)
                    self.Profit_rate.append((TmpInterest[3]-CoverPrice)/TmpInterest[3])
                else:
                    print('尚無進場')
    # 取得當前未平倉量
    def GetOpenInterest(self):               
        # 取得未平倉量
        return self.OpenInterestQty
    # 取得交易紀錄
    def GetTradeRecord(self):               
        # 取得未平倉量
        return self.TradeRecord   
    # 取得交易盈虧清單
    def GetProfit(self):       
        return self.Profit 
    # 取得交易投資報酬率清單
    def GetProfitRate(self):       
        return self.Profit_rate
    
    # # 將股票的回測紀錄寫入MicroTest當中
    # def StockMicroTestRecord(self,StrategyName,Discount):
    #     microtest_db.login('jack','1234','ftserver.haohaninfo.com')
    #     for row in self.TradeRecord:
    #         Fee=row[3]*1000*0.001425*Discount + row[5]*1000*0.001425*Discount 
    #         Tax=row[5]*1000*0.003
    #         microtest_db.insert_to_server_db(   \
    #         row[1],                             \
    #         row[2].strftime('%Y-%m-%d'),        \
    #         row[2].strftime('%H:%M:%S'),        \
    #         row[3],                             \
    #         row[0],                             \
    #         '1',                                \
    #         row[4].strftime('%Y-%m-%d'),        \
    #         row[4].strftime('%H:%M:%S'),        \
    #         row[5],                             \
    #         Tax,                                \
    #         Fee,                                \
    #         StrategyName)    
    #     microtest_db.commit()
    # # 將期貨的回測紀錄寫入MicroTest當中
    # # def FutureMicroTestRecord(self,StrategyName,ProductValue,Fee):
    # #     microtest_db.login('jack','1234','ftserver.haohaninfo.com')
    # #     for row in self.TradeRecord:
    # #         Tax=row[5]*ProductValue*0.00002*2
    # #         microtest_db.insert_to_server_db(   \
    # #         row[1],                             \
    # #         row[2].strftime('%Y-%m-%d'),        \
    # #         row[2].strftime('%H:%M:%S'),        \
    # #         str(int(row[3])),                             \
    # #         str(row[0]),                             \
    # #         '1',                                \
    # #         row[4].strftime('%Y-%m-%d'),        \
    # #         row[4].strftime('%H:%M:%S'),        \
    # #         str(row[5]),                             \
    # #         str(int(Tax)),                                \
    # #         str(int(Fee)),                                \
    # #         StrategyName) 
    # #     microtest_db.commit()
        
        
    # def FutureMicroTestRecord(self,StrategyName,ProductValue,Fee,volume,account,password):
    #     #microtest_db.login('jack','1234','ftserver.haohaninfo.com')
    #     microtest_db.login(account,password,'140.128.36.207')
    #     #microtest_db.login(account,password,'140.128.36.207')
    #     for row in self.TradeRecord:
    #         Tax=(row[3]+row[5])*ProductValue*0.00002
    #         microtest_db.insert_to_server_db(row[1],row[2].strftime('%Y-%m-%d'),row[2].strftime('%H:%M:%S'),str(int(row[3])),str(row[0]),str(volume),row[4].strftime('%Y-%m-%d'),row[4].strftime('%H:%M:%S'),str(row[5]),str(int(Tax)),str(int(Fee)),StrategyName) 
    #     microtest_db.commit()

    
    
    
    # 取得交易總盈虧
    def GetTotalProfit(self):
        if len(self.Profit)>0:
            return sum(self.Profit)
        else:
            return 0
    # 取得交易次數
    def GetTotalNumber(self): 
        if len(self.Profit)>0:
            return len(self.Profit)
        else: 
            return 0
    # 取得平均交易盈虧(每次)
    def GetAverageProfit(self): 
        if len(self.Profit)>0:
            return sum(self.Profit)/len(self.Profit)
        else:
            return 0
    # 取得交易 "平均" 投資報酬率
    def GetAverageProfitRate(self): 
        if len(self.Profit_rate)>0:
            return sum(self.Profit_rate)/len(self.Profit_rate)
        else:
            return 0
    # 取得勝率
    def GetWinRate(self):
        WinProfit = [ i for i in self.Profit if i > 0 ]
        if len(self.Profit)>0:
            return len(WinProfit)/len(self.Profit)
        else:
            return 0
    # 最大連續虧損
    def GetAccLoss(self):
        if len(self.Profit)>0:
            AccLoss = 0
            MaxAccLoss = 0
            for p in self.Profit:
                if p <= 0:
                    AccLoss+=p
                    if AccLoss < MaxAccLoss:
                        MaxAccLoss=AccLoss
                else:
                    AccLoss=0
            return MaxAccLoss
        else:
            return 0
    # 最大累計盈虧回落(MDD)
    def GetMDD(self):
        if len(self.Profit)>0:
            MDD,Capital,MaxCapital = 0,0,0
            for p in self.Profit:
                Capital += p  ## Capital = Capital+p
                MaxCapital = max(MaxCapital,Capital)
                DD = MaxCapital - Capital
                MDD = max(MDD,DD)
            return MDD
        else:
            return 0
    # 最大累計投資報酬率回落(MDD_rate)
    def GetMDD_rate(self):
        if len(self.Profit_rate)>0:
            MDD_rate,Capital_rate,MaxCapital_rate = 0,0,0
            for p in self.Profit_rate:
                Capital_rate += p
                MaxCapital_rate = max(MaxCapital_rate,Capital_rate)
                DD_rate = MaxCapital_rate - Capital_rate
                MDD_rate = max(MDD_rate,DD_rate)
            return MDD_rate
        else:
            return 0
    # 平均獲利(只看獲利的) 
    def GetAverEarn(self):
        if len(self.Profit)>0:
            WinProfit = [ i for i in self.Profit if i > 0 ]
            if len(WinProfit)>0:
                return sum(WinProfit)/len(WinProfit)
            else:
                return 0
        else:
            return 0
        
    # 平均虧損(只看虧損的)
    def GetAverLoss(self):
        if len(self.Profit)>0:
            FailProfit = [ i for i in self.Profit if i < 0 ]
            if len(FailProfit)>0:
                return sum(FailProfit)/len(FailProfit)
            else:
                return 0
        else:
            return 0
    # 累計盈虧
    def GetCumulativeProfit(self):
        if len(self.Profit)>0:
            TotalProfit=[0]
            for i in self.Profit:
                TotalProfit.append(TotalProfit[-1]+i)
            return TotalProfit
        else:
            return 0
    # 累計投資報酬率
    def GetCumulativeProfit_rate(self):
        if len(self.Profit_rate)>0:
            TotalProfit_rate=[0]
            for i in self.Profit_rate:
                TotalProfit_rate.append(TotalProfit_rate[-1]+i)
            return TotalProfit_rate
        else:
            return 0
    ## 產出交易績效圖(累計盈虧)
    def GeneratorProfitChart(self, choice='stock', StrategyName='Strategy'):
        #### 設置 matplotlib 支持中文的字體: 這裡使用的是 'SimHei' 字體，您也可以替換為任何支持中文的字體
        # matplotlib.rcParams['font.family'] = 'Microsoft YaHei'
        # matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei']
        # matplotlib.rcParams['axes.unicode_minus'] = False  # 解決負號顯示問題
        matplotlib.rcParams['font.family'] = 'Noto Sans CJK JP'
        matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
        
        # #### 定義圖表
        # ax1 = plt.subplot(2,1,1)
        plt.figure()
        
        #### 計算累計績效
        TotalProfit=[0]
        if len(self.Profit)>0:
            for i in self.Profit:
                TotalProfit.append(TotalProfit[-1]+i)
        
        #### 繪製圖形
        # ax.plot( TotalProfit[1:]  , '-', marker='o', linewidth=1 )
        if choice == 'stock':
            TotalProfit_re = [i*1000 for i in TotalProfit]
            plt.plot( TotalProfit_re[1:] , '-', marker='o', linewidth=1 )
        if choice == 'future1':
            TotalProfit_re = [i*200 for i in TotalProfit]
            plt.plot( TotalProfit_re[1:] , '-', marker='o', linewidth=1 )
        if choice == 'future2':
            TotalProfit_re = [i*50 for i in TotalProfit]
            plt.plot( TotalProfit_re[1:] , '-', marker='o', linewidth=1 )
            
        
        ####定義標頭
        # # ax.set_title('Profit')
        # ax.set_title('累計盈虧')
        # ax.set_xlabel('交易編號')
        # ax.set_ylabel('累計盈虧(元/每股)')
        plt.title('累計盈虧(元)')
        plt.xlabel('交易編號')
        plt.ylabel('累計盈虧(元)')
        
        
        
        #### 设置x轴的刻度
        ### 获取TotalProfit的长度
        length = len(TotalProfit)
        ### 创建新的x轴刻度列表，每个值都加1
        new_ticks = range(1, length + 1)
        ### 应用新的x轴刻度
        plt.xticks(ticks=range(length), labels=new_ticks)
        
        #### 顯示繪製圖表
        # plt.show()    # 顯示繪製圖表
        # plt.savefig(StrategyName+'.png') #儲存繪製圖表
        ### 在Streamlit中显示
        st.pyplot(plt)
        
    ## 產出交易績效圖(累計投資報酬率)
    def GeneratorProfit_rateChart(self, StrategyName='Strategy'):
        #### 設置 matplotlib 支持中文的字體: 這裡使用的是 'SimHei' 字體，您也可以替換為任何支持中文的字體
        # matplotlib.rcParams['font.family'] = 'Microsoft YaHei'
        # matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei']
        # matplotlib.rcParams['axes.unicode_minus'] = False  # 解決負號顯示問題
        matplotlib.rcParams['font.family'] = 'Noto Sans CJK JP'
        matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
        
        # #### 定義圖表
        # ax = plt.subplot(2,1,2)
        plt.figure()
        
        #### 計算累計投資報酬率
        TotalProfit_rate=[0]
        if len(self.Profit_rate)>0:
            for i in self.Profit_rate:
                TotalProfit_rate.append(TotalProfit_rate[-1]+i)
                
        
        #### 繪製圖形
        # ax.plot( TotalProfit_rate[1:]  , '-', marker='o', linewidth=1 )
        plt.plot( TotalProfit_rate[1:]  , '-', marker='o', linewidth=1 )
        
        ####定義標頭
        # ax1.set_title('Profit')
        # ax.set_title('累計投資報酬率')
        plt.title('累計投資報酬率')
        # ax.set_xlabel('交易編號')
        plt.xlabel('交易編號')
        # ax.set_ylabel('累計投資報酬率')
        plt.ylabel('累計投資報酬率')
        
        #### 设置x轴的刻度
        ### 获取TotalProfit_rate的长度
        length = len(TotalProfit_rate)
        ### 创建新的x轴刻度列表，每个值都加1
        new_ticks = range(1, length + 1)
        ### 应用新的x轴刻度
        plt.xticks(ticks=range(length), labels=new_ticks)
        
        #### 顯示繪製圖表
        # plt.show()    # 顯示繪製圖表
        # plt.savefig(StrategyName+'.png') #儲存繪製圖表
        ### 在Streamlit中显示
        st.pyplot(plt)
        
        
        
        
        
        
        
    

    

# # 市價委託單(預設非當沖、倉別自動)
# def OrderMKT(Broker,Product,BS,Qty,DayTrade='0',OrderType='A'):
#     # 送出交易委託
#     # print([Broker, Product, BS, '',str(Qty), "IOC", "MKT" ,str(DayTrade),OrderType])
#     #OrderNo=GOC.Order(Broker, Product, BS, '0',str(Qty), "IOC", "MKT" ,str(DayTrade),OrderType)
#     #print(OrderNo)
#     # 判斷是否委託成功(這邊以元富為例)
#     if OrderNo != '委託失敗':
#         while True:
#             # 取得成交帳務
#             MatchInfo=GOC.MatchAccount(Broker,OrderNo)
#             # 判斷是否成交
#             if MatchInfo != []:
#                 # 成交則回傳
#                 return MatchInfo[0].split(',')
#     else:
#         return False
            
     
            
# # 範圍市價單(預設非當沖、倉別自動、掛上下N檔價1-5[預設3]、N秒尚未成交刪單[預設10])
# def OrderRangeMKT(Broker,Product,BS, Qty,DayTrade='0',OrderType='A',OrderPriceLevel=3,Wait=10): 
#     # 新增訂閱要下單的商品，預防沒有取到該商品報價
#     # GOC.AddQuote(Broker,Product,True)
#     # 取得委託商品的上下五檔來進行限價委託(這邊預設下單與報價使用同一個券商，若不同則需另外調整)
#     UpdnInfo=GOQ.SubscribeLast(Broker,'updn5',Product)
#     # 如果是買單，則掛上五檔委託
#     if BS == 'B':
#         OrderPoint=UpdnInfo[OrderPriceLevel*2]
#     elif BS == 'S':
#         OrderPoint=UpdnInfo[10+OrderPriceLevel*2]
#     # 送出交易委託
#     print([Broker, Product, BS, str(OrderPoint), str(Qty), "ROD", "LMT" ,str(DayTrade),OrderType])
#     OrderNo=GOC.Order(Broker, Product, BS, str(OrderPoint), str(Qty), "ROD", "LMT" ,str(DayTrade),OrderType )
#     # 設定刪單時間
#     EndTime=time.time()+Wait
#     # 判斷是否委託成功(這邊以元富為例)
#     if OrderNo != '委託失敗':
#         # 若大於刪單時間則跳出迴圈
#         while time.time() < EndTime:
#             # 取得成交帳務
#             MatchInfo=GOC.MatchAccount(Broker,OrderNo)
#             # 判斷是否成交
#             if MatchInfo != []:
#                 # 成交則回傳
#                 return MatchInfo[0].split(',')
#             # 稍等0.5秒
#             time.sleep(0.5)
#             print('尚未成交')
#         # 刪單並確認委託成功刪除
#         GOC.Delete(Broker,OrderNo)
#         GOC.GetAccount(Broker,OrderNo)
#         print('到期刪單')
#         return False
#     else:
#         return False 

# # 範圍市價單(預設非當沖、倉別自動、掛上下N檔價1-5[預設3]、N秒尚未成交刪單[預設10])
# def RangeMKTDeal(Broker,Product,BS, Qty,DayTrade='0',OrderType='A',OrderPriceLevel=3,Wait=10):
#     # 防止例外狀況，最多下三次單
#     for i in range(3):
#         OrderInfo=OrderRangeMKT(Broker,Product,BS,Qty,DayTrade,OrderType,OrderPriceLevel,Wait)
#         if OrderInfo != False:
#             return OrderInfo
#     # 三次委託皆失敗，建議當日不做交易
#     return False
