import time
import DateUtil as du
import Config

BASE_FILENAME = ""
if Config.IS_TEST:
    BASE_FILENAME = time.strftime("%Y%m%d_%H%M%S", time.localtime()) + ".txt"
else:
    BASE_FILENAME = time.strftime("%Y%m%d_%H%M%S", time.localtime()) + ".txt"

def _getFilename(logtype):
    return logtype + "_" + BASE_FILENAME

def log(string):
    filename = _getFilename("LOG")
    try:
        if Config.IS_PRINT_CONSOLE == True:
            print(string)
        if Config.IS_PRINT_FILE == True:
            f = open('log/' + filename, 'a')
            f.write('['+du.getYMDHMS() + "]: " + string + "\n")
            f.close()
    except:
        return