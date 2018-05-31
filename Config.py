positions = ['50', '100']
hostname = 'HUATAI'
RATE_2_Listen = 3 #进入监听队列必须大于此涨跌幅，目的是优化程序，减少不必要的请求
LOOPCOUNT_2_REFRESH_NONEEDTOCHECKISZHANGTING = 14 # 循环n次后，重新分配不需要监听的队列
Code_Risk_Rel = None
isBigEmotionGood = True

IS_TEST = False
IS_SEND_MAIL = True
IS_PRINT_CONSOLE = True
IS_PRINT_FILE = True
Enable = True
StartTime = '09:31:30'
EndTime = '15:00:00'
SellTime = '09:20:00'

QueryWords = [
    '非st；涨跌幅<9；今日开盘涨跌幅＜5且>3；昨日涨跌幅<6且换手率<24且价格>7；按今日开盘涨跌幅降序排序',
    '非st；涨跌幅<9；前日涨跌幅<9；今日开盘涨跌幅<6；昨日换手率<24且涨跌幅>=-6且<-5；按今日开盘涨跌幅降序排序',
    '非st；涨跌幅<9；前日涨跌幅<9；今日开盘涨跌幅<6；昨日换手率<24且涨跌幅>=-7.5且<-6；按今日开盘涨跌幅降序排序',
    '非st；涨跌幅<9；前日涨跌幅<9；今日开盘涨跌幅<6；昨日换手率<24且涨跌幅>-11且<-7.5；按今日开盘涨跌幅降序排序'
]







































