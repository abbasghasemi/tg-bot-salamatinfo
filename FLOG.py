from inspect import getframeinfo, stack
import datetime

GLOBAL_LOG_ENABLED = True

def LOG_INFO(message, toSingleLine = True):
    global GLOBAL_LOG_ENABLED
    if GLOBAL_LOG_ENABLED == False:
        return
    if type(message) is not str:
        message = str(message)
    if toSingleLine == True:
        message = message.replace("\r\n", "").replace("\n", "")
    caller = getframeinfo(stack()[1][0])
    error = "%s %s:%d - %s" % (datetime.datetime.now(), caller.filename, caller.lineno, message)
    f = open("log.txt", "a")
    f.write(error + "\n")
    f.close()