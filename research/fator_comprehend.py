import Action
from time import clock
from bs4 import BeautifulSoup
from selenium import webdriver
import os
import execjs
import time
import GupiaoDataSource
import Config
import LogUtil as lu
import DateUtil as du
import Judgement
import tushare as ts
import Postmaster

def getZhangTingCodeArr(date):
    preDate = du.getPreDayYMD(1, date)
    qw = '非st；'+preDate+'日涨跌幅；'+date+'日最大涨幅>9.89；'+preDate+'日涨跌幅<9'
    return getCodeArr(qw)

def getCodeArr(queryWords):
    w = execjs.eval("encodeURIComponent('" + queryWords + "')")
    url = 'https://www.iwencai.com/stockpick/search?typed=1&preParams=&ts=1&f=3&qs=pc_~soniu~stock~stock~history~query&selfsectsn=&querytype=stock&searchfilter=&tid=stockpick&w=' + w
    browser = None
    try:
        browser = webdriver.Chrome(os.path.abspath('..') + '\driver\chromedriver.exe')
        browser.get(url)
        time.sleep(4)
        browser.implicitly_wait(1)
        try:
            isClicked = False
            elem70 = browser.find_element_by_css_selector('#resultWrap #showPerpage select option[value="70"]')
            if elem70 is not None and isClicked == False:
                elem70.click()
                isClicked = True
            elem50 = browser.find_element_by_css_selector('#resultWrap #showPerpage select option[value="50"]')
            if elem50 is not None and isClicked == False:
                elem50.click()
                isClicked = True
            elem30 = browser.find_element_by_css_selector('#resultWrap #showPerpage select option[value="30"]')
            if elem30 is not None and isClicked == False:
                elem30.click()
            time.sleep(5)
        except:
            time.sleep(0.1)
        html = browser.execute_script("return document.documentElement.outerHTML")
        browser.quit()  # 关闭浏览器。当出现异常时记得在任务浏览器中关闭PhantomJS，因为会有多个PhantomJS在运行状态，影响电脑性能
        soup = BeautifulSoup(html, "html.parser")
        eles = soup.select('#resultWrap .static_con_outer .tbody_table tr td.item div.em')
        index = 0
        codeArr = []
        while index < eles.__len__():
            o_str = eles[index].text.strip()
            if (o_str.isdigit()):
                codeArr.append(o_str)
            index = index + 1
    except Exception as e:
        browser.quit()
        return None
    return codeArr

def isBelow3(df):
    index = range(len(df.index)).stop
    pre_close = df['close'].iloc[index-2]
    open = df['open'].iloc[index-1]
    return round(float(open-pre_close)/float(pre_close), 4) > 3

def isAbove5(df):
    index = range(len(df.index)).stop
    pre_close = df['close'].iloc[index-2]
    open = df['open'].iloc[index-1]
    return round(float(open-pre_close)/float(pre_close), 4) < 5

def isBetween3And5(code, date):
    index = range(len(df.index)).stop
    pre_close = df['close'].iloc[index - 2]
    open = df['open'].iloc[index - 1]
    rate = round(float(open - pre_close) / float(pre_close), 4)
    if rate > 3 and rate < 5:
        return True
    else:
        return False

def getHisDataFrame(code, date):
    preOneDay = du.getPreDayYMD(30, date)
    df = ts.get_k_data(code, preOneDay, date)
    return df

def isHasBigGoDownAfterZhangTingDay(df):
    pre_close = 0
    riskcount = 0
    yesterdayIsZhangting = False
    count = 0
    isHasPlus4PercentDay = False
    for x in range(len(df.index)):
        if x == 0:
            pre_close = df['close'].iloc[x]
            continue
        # code = df['code'].iloc[x]
        # date = df['date'].iloc[x]
        # low = df['low'].iloc[x]
        # volume = df['volume'].iloc[x]
        open = df['open'].iloc[x]
        close = df['close'].iloc[x]
        high = df['high'].iloc[x]

        # 当日最高阶幅度
        h_rate = round(float((high - pre_close) / pre_close) * 100, 2)
        # 当日收盘幅度
        c_rate = round(float((close - pre_close) / pre_close) * 100, 2)
        # 当日开盘幅度
        o_rate = round(float((open - pre_close) / pre_close) * 100, 2)
        # 保证取到14天的数据
        if count + 20 < len(df.index):
            pre_close = df['close'].iloc[x]
            count = count + 1
            yesterdayIsZhangting = False
            if high == close and h_rate > 9.5 and o_rate > 3:
                yesterdayIsZhangting = True
            continue

        # ! 板后统计开盘溢价
        if yesterdayIsZhangting == True:
            if o_rate > 0:
                # 第一等级风险：虽然高开，但是一路低走，人气涣散
                if o_rate > 0 and (o_rate - c_rate) > 6:
                    riskcount = riskcount + (c_rate - o_rate) * 1000
                elif riskcount < 0:
                    riskcount = riskcount + o_rate * 1000
                else:
                    riskcount = riskcount + o_rate * 3
                print("板后统计开盘溢价: " + str(o_rate*1000))
            else:
                riskcount = riskcount + o_rate
                print("板后亏钱开盘: " + str(o_rate*1000))
            yesterdayIsZhangting = False


def getTrainX(dateArr):
    for date in dateArr:
        codeArr = getZhangTingCodeArr(date)
        for code in codeArr:
            m_isBelow3 = isBelow3(code, date)
            m_isAbove = isAbove5(code, date)
            m_isBetween3And5 = isBetween3And5(code, date)
            df = getHisDataFrame(code, date)
            m_isHasBigGoDownAfterZhangTingDay = isHasBigGoDownAfterZhangTingDay(df)



# codeArr = getZhangTingCodeArr('2018-05-25')
# print(codeArr)
df = getHisDataFrame('002806', '2018-05-25')
print(isHasBigGoDownAfterZhangTingDay(df))