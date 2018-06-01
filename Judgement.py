from time import clock
from bs4 import BeautifulSoup
import os
import execjs
import LogUtil as lu
import time
from selenium import webdriver
import tushare as ts
import DateUtil as du
import GupiaoDataSource as gs
import Config

#大环境情绪氛围好还是不好
#codeArr: 昨日涨停；昨日成交量>500万；按昨日涨停时间升序排序前10
map_code_openrate_rel = {}
map_code_now_rel = {}
def startListenIsBigEmotionGood():
    queryWords = "非st；昨日涨停；昨日成交量>1000万；按昨日最终涨停时间升序排序前20；"
    w = execjs.eval("encodeURIComponent('" + queryWords + "')")
    url = 'https://www.iwencai.com/stockpick/search?typed=1&preParams=&ts=1&f=3&qs=pc_~soniu~stock~stock~history~query&selfsectsn=&querytype=stock&searchfilter=&tid=stockpick&w=' + w
    browser = None
    try:
        browser = webdriver.Chrome(os.path.abspath('.') + '\driver\chromedriver.exe')
        browser.get(url)
        time.sleep(4)
        browser.implicitly_wait(1)
        try:
            elem = browser.find_element_by_css_selector('#resultWrap #showPerpage select option[value="50"]')
            if elem is not None:
                elem.click()
        except:
            lu.log("get_html_forWencai Execption")
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


    while True:
        if du.getHMS() < '09:25:00':
            print("[" + du.getHMS() + "] startListenIsBigEmotionGood: tik tok...")
            time.sleep(3)
            continue
        riskCount = 0
        for code in codeArr:
            #记录开盘涨跌幅，只记录一次
            if map_code_openrate_rel.keys().__len__() == 0 and du.getHMS() > "09:25:30" and du.getHMS() < "09:30:00":
                df = gs.getDataFrame(code)
                rate = gs.getRate(df)
                map_code_openrate_rel[code] = rate
            #记录竞价涨跌幅
            if du.getHMS() > "09:30:00":
                df = gs.getDataFrame(code)
                rate = gs.getRate(df)
                map_code_now_rel[code] = rate
            #计算riskCount
            if map_code_openrate_rel.keys().__len__() > 0 and map_code_now_rel.keys().__len__() > 0:
                for code in map_code_now_rel.keys():
                    r_now = float(map_code_now_rel[code])
                    r_open = float(map_code_openrate_rel[code])
                    #现在涨跌幅<0
                    if r_now < 0:
                        riskCount = riskCount + 1
                    if (r_now - r_open) < 0:
                        riskCount = riskCount + 1

        if map_code_openrate_rel.keys().__len__() == 0 or map_code_now_rel.keys().__len__() == 0:
            Config.isBigEmotionGood = False
        if riskCount > 6:
            Config.isBigEmotionGood = False
        else:
            Config.isBigEmotionGood = True

        time.sleep(30)
        print("[" + du.getHMS() + "] startListenIsBigEmotionGood: after cal tik tok...")

#风险等级：板后高开大幅下挫 > 烂板 > 低开低走 > 低沉走势
def risk(code, startYMD = du.getPreDayYMD(1)):
    days_ForCaculating = 20
    today = startYMD
    preOneDay = du.getPreDayYMD(days_ForCaculating+10, startYMD)
    df = ts.get_k_data(code, preOneDay, today)
    pre_close = 0
    riskcount = 0
    yesterdayIsZhangting = False
    count = 0
    little_shangying_count = 0
    isHasPlus4PercentDay = False
    pre_o_rate = 0
    pre_h_rate = 0
    pre_c_rate = 0

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
        if count + days_ForCaculating < len(df.index):
            pre_close = df['close'].iloc[x]
            count = count + 1
            yesterdayIsZhangting = False
            if high == close and h_rate > 9.5 and o_rate > 3:
                yesterdayIsZhangting = True
            continue

        #! 板后统计开盘溢价
        if yesterdayIsZhangting == True:
            if o_rate > 0:
                #第一等级风险：虽然高开，但是一路低走，人气涣散
                if o_rate > 0 and (o_rate - c_rate) > 6:
                    riskcount = riskcount + (c_rate - o_rate) * 1000
                elif riskcount < 0:
                    riskcount = riskcount + o_rate*1000
                else:
                    riskcount = riskcount + o_rate*3
                #print("板后统计开盘溢价: " + date)
            else:
                riskcount = riskcount + o_rate
                #print("板后亏钱开盘: " + str(o_rate*1000))

            yesterdayIsZhangting = False
        #!第二等级风险：烂板天
        if h_rate > 9.5 and h_rate != c_rate and h_rate - c_rate > 5:
            #print("烂板: " + date)
            riskcount = riskcount + (c_rate - h_rate)*1000
            #a = 1
        else:
            # ! 高开统计（非烂板基础上）
            if c_rate > 2 and o_rate > 1 and h_rate < 8:
                riskcount = riskcount + o_rate
                #print("高开高走统计: " + date)

        # !第三等级风险：长上影+长阴实体
        if h_rate - o_rate > 4 and o_rate - c_rate > 4:
            riskcount = riskcount + (c_rate - h_rate) * 1000

        if h_rate - o_rate > 2:
            if little_shangying_count > 0.618 * days_ForCaculating:
                riskcount = riskcount - 1
            little_shangying_count = little_shangying_count + 1

        # 统计这么多天来，是否存在实体涨幅大于4
        if c_rate > 4 and c_rate - o_rate > 2:
            isHasPlus4PercentDay = True
        if h_rate > 9.5 and (h_rate - c_rate) < 1:
            yesterdayIsZhangting = True
        pre_close = df['close'].iloc[x]
        pre_o_rate = o_rate
        pre_h_rate = h_rate
        pre_c_rate = c_rate
        count = count + 1

    if riskcount < 1 and riskcount > -1:
        riskcount = 0
    if isHasPlus4PercentDay == False:
        riskcount = riskcount - 10
    return riskcount

def filterByRisk_GtE0(codeArr):
    arr = []
    for code in codeArr:
        r = risk(code)
        if r < 0:
            continue
        arr.append(code)
    return arr

def filterByRisk_Gt0(codeArr):
    arr = []
    for code in codeArr:
        r = risk(code)
        if r <= 0:
            print('判断' + code + '--->X')
            continue
        arr.append(code)
        print('判断' + code + '--->√')
    return arr

def genCodeRiskRel(codeArr):
    rel = {}
    for code in codeArr:
        r = risk(code)
        rel[code] = r
    return rel