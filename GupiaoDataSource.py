import tushare as ts
import time

def getDataFrame(code):
    try:
        df = ts.get_realtime_quotes(code)
    except Exception as e:
        print(e)
        return None
    return df

def isZhangting(data):
    try:
        df = data
        a5_p = str(round(float(df['a5_p'][0]), 2))
        a4_p = str(round(float(df['a4_p'][0]), 2))
        a3_p = str(round(float(df['a3_p'][0]), 2))
        a2_p = str(round(float(df['a2_p'][0]), 2))
        currentPrice = str(round(float(df['a1_p'][0]), 2))
        if a5_p == '0.0' or a4_p == '0.0' or a3_p == '0.0' or a2_p == '0.0' or currentPrice == '0.0':
            return True
        rate = getRate(df)
        if rate > float(9.5):
            return True
        print("监听："+ df['code'][0] + "$" + df['name'][0] + "-> currentPrice: " + currentPrice)
        return False
    except Exception as e:
        time.sleep(5)
        return False

def getZhangtingPrice(data):
    try:
        df = data
        yesterday_closePrice = str(round(float(df['pre_close'][0]), 2))
        today_zhangtingPrice = str(round(float(yesterday_closePrice)*1.1, 2))
        return today_zhangtingPrice
    except Exception as e:
        time.sleep(5)
        return 0

def getRate(data):
    try:
        df = data
        pre_close = round(float(df['pre_close'][0]), 2)
        price = round(float(df['price'][0]), 2)
        return round(float((price - pre_close) / pre_close)*100, 2)
    except Exception as e:
        time.sleep(5)
        return 0

def getPrice(data):
    try:
        return round(float(data['b1_p'][0]), 2)
    except Exception as e:
        time.sleep(5)
        return 0

def getStockName(data):
    try:
        df = data
        return df['name'][0]
    except Exception as e:
        time.sleep(5)
        return ""

#print(ts.get_realtime_quotes('002806'))
