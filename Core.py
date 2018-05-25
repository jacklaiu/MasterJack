#! /usr/bin/evn python
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
import Judgement
import Postmaster

class StockWatcher:

    def __init__(self, QUERY_WORDS, START_TIME_LIMIT, END_TIME_LIMIT, threadLocal):
        self.START_TIME_LIMIT = START_TIME_LIMIT
        self.END_TIME_LIMIT = END_TIME_LIMIT
        self.QUERY_WORDS = QUERY_WORDS
        self.ds = GupiaoDataSource
        self.threadLocal = threadLocal

    def get_html(self, url):
        browser = None
        try:
            browser = webdriver.Chrome(os.path.abspath('.') + '\driver\chromedriver.exe')
            browser.get(url)
            time.sleep(2)
            browser.implicitly_wait(1)
            html = browser.execute_script("return document.documentElement.outerHTML")
            browser.quit()  # 关闭浏览器。当出现异常时记得在任务浏览器中关闭PhantomJS，因为会有多个PhantomJS在运行状态，影响电脑性能
            return html
        except Exception as e:
            browser.quit()
            return None

    def get_html_forWencai(self, url):
        browser = None
        try:
            browser = webdriver.Chrome(os.path.abspath('.') + '\driver\chromedriver.exe')
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
                lu.log("get_html_forWencai Execption")
            html = browser.execute_script("return document.documentElement.outerHTML")
            browser.quit()  # 关闭浏览器。当出现异常时记得在任务浏览器中关闭PhantomJS，因为会有多个PhantomJS在运行状态，影响电脑性能
            return html
        except Exception as e:
            browser.quit()
            return None

    def get_html_innerIframe(self, url, iframeID):
        browser = None
        try:
            browser = webdriver.Chrome(os.path.abspath('.') + '\driver\chromedriver.exe')
            browser.get(url)
            time.sleep(3)
            browser.implicitly_wait(1)
            browser.switch_to.frame(iframeID)
            html = browser.execute_script("return document.documentElement.outerHTML")
            browser.quit()  # 关闭浏览器。当出现异常时记得在任务浏览器中关闭PhantomJS，因为会有多个PhantomJS在运行状态，影响电脑性能
            return html
        except Exception as e:
            browser.quit()
            return None

    def get_soup(self, url):
        try:
            soup = BeautifulSoup(self.get_html(url), "html.parser")
        except Exception as e:
            return None
        return soup

    def get_soup_forWencai(self, url):
        try:
            html = self.get_html_forWencai(url)
            soup = BeautifulSoup(html, "html.parser")
        except Exception as e:
            return None
        return soup

    def get_soup_innerIframe(self, url, iframeID):
        if not url:
            return None
        try:
            soup = BeautifulSoup(self.get_html_innerIframe(url, iframeID), "html.parser")
        except Exception as e:
            return None
        return soup

    def get_ele(self, soup, selector):
        try:
            ele = soup.select(selector)
            return ele
        except Exception as e:
            return None

    def getCodeArrayFromWencai(self, w):
        url = 'https://www.iwencai.com/stockpick/search?typed=1&preParams=&ts=1&f=3&qs=pc_~soniu~stock~stock~history~query&selfsectsn=&querytype=stock&searchfilter=&tid=stockpick&w=' + w
        soup = self.get_soup_forWencai(url)
        eles = self.get_ele(soup, '#resultWrap .static_con_outer .tbody_table tr td.item div.em')
        index = 0
        arr = []
        while index < eles.__len__():
            o_str = eles[index].text.strip()
            if (o_str.isdigit()):
                arr.append(o_str)
            index = index + 1
        return arr

    def getCodeArray(self, queryWords):
        codeArr = []
        for w in queryWords:
            arr = self.getCodeArrayFromWencai(execjs.eval("encodeURIComponent('" + w + "')"))
            for code in arr:
                codeArr.append(code)
        return codeArr

    def clearConfig(self):
        f_config = open('C:/auto/BuyAction.txt', 'w')
        f_config.write("")
        f_config.close()

    def isShouldBuy(self):
        return time.strftime("%H:%M:%S", time.localtime()) > self.START_TIME_LIMIT

    def isTime2Exit(self):
        return time.strftime("%H:%M:%S", time.localtime()) > self.END_TIME_LIMIT

    def startListen(self):
        self.clearConfig()
        codeArr = self.getCodeArray(self.QUERY_WORDS)
        print("Risk过滤前：" + str(codeArr.__len__()))
        codeArr = Judgement.filterByRisk_Gt0(codeArr)
        print("Risk过滤后：" + str(codeArr.__len__()))
        Postmaster.sendCodeArr(codeArr)
        self.listenZhangting(codeArr)
        self.clearConfig()

    def listenZhangting(self, codeArr):
        isEnd = False
        line = ''
        forbidden_line = ''
        forbidden_control_msg = {}
        forbidden_control_msg['count'] = 0
        forbidden_control_msg['limit'] = 3
        loopCount = 0
        rate_underZero_codes = []

        while True:
            obj = Action.getForbiddenCodeString(forbidden_line, forbidden_control_msg)
            forbidden_control_msg = obj['msg']
            forbidden_line = obj['line']
            # if self.threadLocal.buyCount == Config.positions.__len__():
            #     isEnd = True
            #     lu.log("----------------->仓位数组已使用完")
            if codeArr.__len__() == 0:
                isEnd = True
                lu.log("----------------->无监听标的")
            if self.isTime2Exit():
                isEnd = True
                lu.log("----------------->不在设置的交易时间内")
                time.sleep(3)
            if isEnd is True:
                break
            begintime = clock()
            i = 0
            if loopCount == 0 or loopCount % Config.LOOPCOUNT_2_REFRESH_NONEEDTOCHECKISZHANGTING == 0:
                print('重新分配监听优化数组，放弃监听')
                rate_underZero_codes = []
            while i < codeArr.__len__():
                code = codeArr[i]
                if code in line or code in forbidden_line:
                    i = i + 1
                    continue
                i = i + 1
                # 涨跌幅过滤
                if code in rate_underZero_codes:
                    continue
                dataFrame = self.ds.getDataFrame(code)
                if dataFrame is None:
                    continue
                if loopCount == 0 or loopCount % Config.LOOPCOUNT_2_REFRESH_NONEEDTOCHECKISZHANGTING == 0:
                    rate = self.ds.getRate(dataFrame)
                    if rate < Config.RATE_2_Listen:
                        print('统计入涨跌幅优化数组，放弃监听->' + code + ":" + str(rate))
                        rate_underZero_codes.append(code)
                    else:
                        print('进入监听名单->' + code + ":" + str(rate))
                # 涨跌幅过滤
                if code in rate_underZero_codes:
                    continue
                if self.ds.isZhangting(dataFrame) is False:
                    continue
                #Test
                # if loopCount >= 0:
                #     continue
                name = self.ds.getStockName(dataFrame)
                zhangtingprice = self.ds.getZhangtingPrice(dataFrame)
                if self.isShouldBuy():
                    #posi = Config.positions[self.threadLocal.buyCount]
                    posi = '100'
                    if posi != '0':
                        Action.buyAction(code, name, zhangtingprice, posi)
                        self.threadLocal.buyCount = self.threadLocal.buyCount + 1
                        isEnd = True
                        break
                    else:
                        lu.log('------------------------------------->posi == "0" 放弃买入')
                else:
                    lu.log('------------------------------------->未达到条件放弃买入')

                line = line + code + '~'
                break

            print('$$$$$$$$$$$$zhangtingcodes: ' + line + ' - zhangtingcount: ' + str(line.count('~')))
            print('$$$$$$$$$$$$spend------------------------------------------------>' + str(clock() - begintime))
            time.sleep(1)
            loopCount = loopCount + 1
            print('$$$$$$$$$$$$loopC------------------------------------------------>' + str(loopCount) + "->" + str(Config.LOOPCOUNT_2_REFRESH_NONEEDTOCHECKISZHANGTING))