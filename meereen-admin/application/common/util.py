# -*- coding: utf-8 -*-
import time
import datetime

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