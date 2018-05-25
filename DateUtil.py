import time
import datetime

def getYMDHMS():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

def getYMD():
    return time.strftime("%Y-%m-%d", time.localtime())

def getHMS():
    return time.strftime("%H:%M:%S", time.localtime())

def getTimeStamp():
    millis = int(round(time.time() * 1000))
    return millis

def getFormatToday():
    return time.strftime("%Y-%m-%d", time.localtime())

def getPreDayYMD(num=1, startdate=None):
    today=datetime.date.today()
    if startdate is not None:
        arr = startdate.split("-")
        today = datetime.date(int(arr[0]), int(arr[1]), int(arr[2]))
    oneday=datetime.timedelta(days=num)
    d=today-oneday
    return str(d)