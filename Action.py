import threading
import requests
import Config
import Postmaster as pm
import LogUtil as lu
from Core import StockWatcher
import DateUtil as du
import time
import GupiaoDataSource as gs

forbidden_Count = 0
forbidden_Limit = 5

class ThreadLocal:
    def __init__(self):
        self.buyCount = 0
    def getBuyCount(self):
        return self.buyCount

def startListenZhangting():
    threadLocal = ThreadLocal()
    if Config.Enable == True:
        thread1 = ListenZhangtingThread(1, Config.QueryWords, Config.StartTime, Config.EndTime, threadLocal)
        thread1.start()
        pm.sendListenStartEmail()
        lu.log("监听程序启动")

def startNotifyInTimeBigEmotion4Sell():
    while True:
        hms = du.getHMS()
        if '09:25' in hms or '09:30' in hms or '09:32' in hms or '09:35' in hms or '09:40' in hms or '09:50' in hms or '10:00' in hms:
            if Config.isBigEmotionGood == False:
                pm.sendContent('市场环境氛围_差', '市场环境氛围_差')
            else:
                pm.sendContent('市场环境氛围_好', '市场环境氛围_好')
            time.sleep(60)
        time.sleep(1)
        print("[" + du.getHMS() + "] startNotifyInTimeBigEmotion4Sell: tik tok...")
        if hms > '10:30:00':
            break

def buyAction(code, name, price, posi):
    config_words = code + "," + name + "," + posi + "," + price + ",0"
    f_config = open('C:/auto/BuyAction.txt', 'w')
    f_config.write(config_words)
    f_config.close()
    pm.sendBuyDoneEmail(code)
    lu.log("已写入执行句子：" + config_words)
    f = open('persist.txt', 'w')
    f.write(code)
    f.close()

def sellAction(code=None, name=None, price=None, posi='100'):
    if name is None:
        df = gs.getDataFrame(code)
        name = gs.getStockName(df)
        price = str(round(float(df['b1_p'][0]), 2))
        posi = '100'
    if du.getHMS() < '09:25:00':
        df = gs.getDataFrame(code)
        pre_close = str(round(float(df['pre_close'][0]), 2))
        price = round(float(pre_close) * 0.92, 2)
    config_words = code + "," + name + "," + posi + "," + str(price) + ",0"
    f_config = open('C:/auto/SellAction.txt', 'w')
    f_config.write(config_words)
    f_config.close()
    pm.sendSellDoneEmail(code)
    lu.log("SellAction: 已写入执行句子：" + config_words)
    f = open('persist.txt', 'w')
    f.write("")
    f.close()

def sellIn0925():
    res = requests.get("http://95.163.200.245:11252/chicang/read")
    if res.text is None or res.text == "Nothing":
        return
    code = str(res.text)
    while True:
        time.sleep(5)
        if du.getHMS() > Config.SellTime:
            df = gs.getDataFrame(code)
            if df is None:
                return
            name = gs.getStockName(df)
            pre_close = str(round(float(df['pre_close'][0]), 2))
            sp = str(round(float(pre_close)*0.91, 2))
            sellAction(code, name, sp, '100')
            requests.get("http://95.163.200.245:11252/chicang/deleteall")
            break
        else:
            print('[' + du.getHMS() + ']:sellIn0925 waitting...')

def serialListenForSell():
    f = open('persist.txt', 'r')
    code = str(f.readline())
    f.close()
    if code is not None and code != 'Nothing' and code != "":
        print("[" + str(du.getHMS()) + "]:已获取code:" + code)
        df = gs.getDataFrame(code)
        pre_b1_v = float(df['b1_v'][0])
        while True:
            if du.getHMS() < "09:24:20":
                time.sleep(5)
                continue
            df = gs.getDataFrame(code)
            rate = float(gs.getRate(gs.getDataFrame(code)))

            if rate < 0 and du.getHMS() < "10:30:00":
                time.sleep(5)
                continue

            if rate > 9.89:
                b1_v = float(df['b1_v'][0])
                if pre_b1_v - b1_v > 1280:
                    sellAction(code=code)
                    break
            else:
                sellAction(code=code)
                break
            print("[" + str(du.getHMS()) + "]:持续监听卖出->rate:" + str(rate) + "->b1_v:" + str(pre_b1_v) + "->volumeDis:" + str(pre_b1_v - b1_v))
            pre_b1_v = float(df['b1_v'][0])
            time.sleep(5)
    else:
        print("[" + str(du.getHMS()) + "]:没有持仓")

def getForbiddenCodeString(line, forbidden_control_msg):
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!forbidden_control_msg.count: " + str(forbidden_control_msg['count']))
    count = forbidden_control_msg['count']
    if count >= forbidden_control_msg['limit']:
        #res = requests.get("http://95.163.200.245:11252/forbidden_code_byhand/read")
        line = ""#str(res.text)
        return {'line': line, 'msg': {'count': 0, 'limit': forbidden_control_msg['limit']}}
    return {'line': line, 'msg': {'count': count+1, 'limit': forbidden_control_msg['limit']}}

class ListenZhangtingThread(threading.Thread):
    def __init__(self, threadId, queryWords, start_limit_time, end_limit_time, threadLocal):
        threading.Thread.__init__(self)
        self.threadId = threadId
        self.queryWords = queryWords
        self.start_limit_time = start_limit_time
        self.end_limit_time = end_limit_time
        self.threadLocal = threadLocal

    def run(self):
        sw = StockWatcher(self.queryWords, self.start_limit_time, self.end_limit_time,
                          self.threadLocal)
        sw.startListen()