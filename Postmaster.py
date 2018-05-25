import requests
import threading
import Config as conf
import DateUtil as du
import Judgement
import requests
import GupiaoDataSource as gs

default_receivers = 'jacklaiu@qq.com'  # 收邮件人

class Async_req(threading.Thread):
    def __init__(self, url):
        threading.Thread.__init__(self)
        self.url = url
    def run(self):
        requests.get(self.url)

def sendListenStartEmail(receivers=default_receivers):
    if conf.IS_SEND_MAIL == False:
        return
    Async_req('http://95.163.200.245:11251/sendListenStartEmail/'+conf.hostname+'/'+du.getYMD()+'/'+receivers).start()

def sendBuyDoneEmail(code="002197", receivers=default_receivers):
    if conf.IS_SEND_MAIL == False:
        return
    Async_req('http://95.163.200.245:11251/sendSellDoneEmail/'+code+'/'+conf.hostname+'/'+du.getYMD()+'/'+receivers).start()

def sendSellDoneEmail(code="002197", receivers=default_receivers):
    if conf.IS_SEND_MAIL == False:
        return
    Async_req('http://95.163.200.245:11251/sendSellDoneEmail/'+code+'/'+conf.hostname+'/'+du.getYMD()+'/'+receivers).start()

def sendCodeArr(codeArr):
    content = "_".join(codeArr) + "_共" + str(codeArr.__len__()) + "个"
    title = str(codeArr.__len__())+"个"
    try:
        requests.get('http://95.163.200.245:11251/sendEmail/['+du.getYMD()+':'+conf.hostname+']：盘前选股_'+title+'/候选：'+content+'/'+default_receivers)
    except Exception as e:
        print("ERROR Send Check Mail!")

def sendContent(title, content):
    try:
        requests.get('http://95.163.200.245:11251/sendEmail/['+du.getYMD()+':'+conf.hostname+']：'+title+'/'+content+'/'+default_receivers)
    except Exception as e:
        print("ERROR Send Check Mail!")

#sendBuyDoneEmail('002901')

