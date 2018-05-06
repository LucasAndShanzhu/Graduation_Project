# -*- coding: utf-8 -*-
# @Author: shanzhu
# @Date:   2018-02-26 10:48:39
# @Last Modified by:   shanzhu
# @Last Modified time: 2018-02-26 14:44:25

#生成元素个数为1的项集
#dataSet = [[1,2,3], [2,3], [1,3,4]]
#return [[1], [2], [3], [4]]
def createC1(dataSet):
    C1 = []
    for transaction in dataSet:
        for item in transaction:
            if not [item] in C1:
                C1.append([item])
    C1.sort()
    return map(frozenset, C1)

#其中D为全部数据集，Ck为大小为k（包含k个元素）的候选项集，minSupport为设定的最小支持度。
#返回值中retList为在Ck中找出的频繁项集（支持度大于minSupport的），supportData记录各频繁项集的支持度。
def scanD(D, Ck, minSupport):
    ssCnt = {}
    for tid in D:
        for can in Ck:
            if can.issubset(tid):
                ssCnt[can] = ssCnt.get(can, 0) + 1
    numItems = float(len(D))
    retList = []
    supportData = {}
    for key in ssCnt:
        support = ssCnt[key] / numItems
        if support >= minSupport:
            retList.insert(0, key)
        supportData[key] = support
    return retList, supportData

#依靠原始数据集，分别求出项数为1，2，3，4等的数据集，并获得其中的频繁集
#然后根据频繁集找出满足最小可信度的规则。
#思路：每次循环时寻找项数为1，2，3。。的头部推到规则.

