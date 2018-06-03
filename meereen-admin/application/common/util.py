# -*- coding: utf-8 -*-
import time
import datetime
import pyDes
import rsa
from base64 import b64decode, b64encode

DES_KEY = 'DGxMSzs4'
DES_IV = 'SEM7LRfA'

def getDatetime(days=1, timeFormat=""):
    if not timeFormat:
        timeFormat = "%Y-%m-%d %H:%M:%S"
    now = datetime.datetime.now()
    target = now - datetime.timedelta(days=days)
    return time.strftime(timeFormat, target.timetuple())

def getTimestamp(dateTime, timeFormat=""):
    if not timeFormat:
        timeFormat = "%Y-%m-%d %H:%M:%S"
    datetuple = time.strptime(dateTime, timeFormat)
    return int(time.mktime(datetuple))

def getTimeDelta(first, second):
    first = getTimestamp(first)
    second = getTimestamp(second)
    return (second - first) / 86400

def getDatetoNowDelta(targetTime):
    today = getDatetime(0)
    timeD = getTimeDelta(targetTime, today)
    return timeD

def desEncrypt(message):
    p = pyDes.des(DES_KEY, pyDes.CBC, DES_IV, padmode=pyDes.PAD_PKCS5)
    enMessage = p.encrypt(message)
    return b64encode(enMessage)

def desDecrypt(enMessage):
    p = pyDes.des(DES_KEY, pyDes.CBC, DES_IV, padmode=pyDes.PAD_PKCS5)
    message = b64decode(enMessage)
    return p.decrypt(message)

def rsaDecrypt(privateK, enMessage):
    return rsa.decrypt(enMessage, privateK)    

def rsaEncrypt(publicK, message):
    message = str(message)
    return rsa.encrypt(message, publicK)

if __name__ == '__main__':
    print m
