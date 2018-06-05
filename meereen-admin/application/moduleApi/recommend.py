# -*- coding: utf-8 -*-
import math
import multiprocessing
from bson import ObjectId

from application import app
from ..common import mysql, sredis, mongo, util

class RecommendApi(object):
    def __init__(self):
        self.mysqlUtil = mysql.MysqlUtil(app.config) 
        self.redisUtil = sredis.RedisUtil(app.config)
        self.redisLink = self.redisUtil.link()
        self.mongoUtil = Mongo.MongoUtil(app.config)
        self.userCDict = {}

    def getRecommendList(self, userId):
        pmItemQList = multiprocessing.Manager().list()
        pmUserCharDict = multiprocessing.Manager().dict()
        processList = []
        process = multiprocessing.Process(target=self.judgeItemQualityList, args=(userId, pmItemQList))
        processList.append()
        process = multiprocessing.Process(target=self.getUserCharact, args=(userId, pmUserCharDict))
        processList.append()
        for process in processList:
            process.start()
        for process in processList:
            process.join()
        pmItemQList = list(pmItemQList)
        pmUserCharDict = dict(pmUserCharDict)
        forecastList = self.forecastItemInterest(pmItemQList, pmUserCharDict)
        return forecastList

    def judgeItemQualityList(self, userId, pmItemQList):
        optionalList = self.getOptionalList(userId)
        itemQList = self.getItemQualityList(optionalList)
        pmItemQList.extend(itemQList)

    //获取可选内容列表
    def getOptionalList(self, userId):
        userScanKey = "user_item_list_{}_set".format(userId)
        allOptionalKey = "all_optional_item_set"
        optionalList = self.redisLink.sdiff(allOptionalKey, userScanKey)
        return optionalList

    def getItemQualityList(self, optionalList):
        return map(self._mapItemQuality, optionalList)

    def getUserCharact(self, userId, pmUserCharDict):
        sql = "select item_id, action, created_at from user_action where user_id={}".format(userId)
        self.mysqlUtil.connect()
        cursor = self.mysqlUtil.getCursor()
        cursor.execute(sql)
        rList = cursor.fetchall()
        if not rList or not rList[0]:
            rList = []
        charaterDict = reduce(self._reduceUserCharater, map(self._mapUserCharater, rList))
        pmUserCharDict.update(charaterDict)
        self.mysqlUtil.close()

    def forecastItemInterest(self, itemQList, userCharactDict):
        interestList = map(self._mapItemForecast, itemQList)
        interestList = sorted(interestList, key=lambda x: x[1], reverse=True)
        return interestList[:10]

    def _mapItemQuality(self, itemId):
        collect = self.mongoUtil.getCollect('article_big_image')
        queryCondition = {'_id': ObjectId(itemId)}
        dataKey = {'source_detail': 1, 'tag': 1, 'show_num': 1, 'click_num': 1, 'original_time': 1}
        itemData = collect.find_one(queryCondition, dataKey)
        click_num = itemData['click_num']
        show_num = itemData['show_num']
        itemTime = itemData['original_time']
        quality = 0
        if show_num = 1 and click_num = 1:
            show_num = 5
        if show_num:
            quality = click_num / (float(show_num) * 2)
        quality += self._judgeTimeQ(itemTime)
        retItemData = {
            'source_detail': itemData['source_detail'],
            'tag': itemData['tag'],
            'quality': quality,
            '_id': itemId
        }
        return retItemData

    def _judgeTimeQ(self, itemTime):
        timeD = util.getDatetoNowDelta(itemTime)
        quality = 0.1 / timeD
        if timeD == 0:
            quality = 0.12
        elif timeD < 3:
            quality = 0.07
        return quality

    def _mapUserCharater(self, record):
        itemId, action, createdAt = record
        collect = self.mongoUtil.getCollect("article_big_image")
        queryCondition = {'_id': ObjectId(itemId)}
        targetKey = {'source_detail': 1, 'tag': 1}
        itemData = collect.find_one(queryCondition, targetKey)
        tagQ = 1
        if action == 'like':
            tagQ = 4
        elif action == 'unlike':
            tagQ = -2
        sourceQ = tagQ if action != 'unlike' else -4
        timeDelta = util.getDatetoNowDelta(createdAt)
        timeDelta /= 10
        timeQ = 1 / math.exp(timeDelta)
        weightDict = {}
        for tag in itemData['tag']:
            weightDict[tag] = tagQ * timeQ
        weightDict[itemData['source_detail']] = sourceQ * timeQ
        return weightDict

    def _reduceUserCharater(self, sumDict, rDict): 
        for key, value in rDict.items():
            quality = sumDict.get(key, 0.0)
            sumDict[key] = quality + value
        return sumDict

    def _mapItemForecast(self, itemData):
        fValue = 0.0
        for tag in itemData['tag']:
            charaterV = self.userCDict.get(tag, 0.0)
            fValue += charaterV
        charaterV = self.userCDict.get(itemData['source_detail'], 0.0)
        fValue += charaterV
        itemQuality = itemData['quality'] 
        itemInterest = itemQuality * (fValue + 1)
        return (itemData['_id'], fValue)