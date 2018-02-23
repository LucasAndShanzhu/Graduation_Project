# -*- coding: utf-8 -*-
# @Author: shanzhu
# @Date:   2017-12-05 14:38:19
# @Last Modified by:   shanzhu
# @Last Modified time: 2017-12-12 10:13:54

class SelfException(Exception):
    def __str__(self):
        return self.message

class ProxyIpNotEnoughException(SelfException):
    def __init__(self):
        super(ProxyIpNotEnough, self).__init__()
        self.message = "(proxy is not enough)"

class LabelAttrTypeWrongException(SelfException):
    def __init__(self):
        super(ProxyIpNotEnough, self).__init__()
        self.message = "(the type of label which is need to filtered is wrong)"

class HtmlPaeserException(Exception):
    pass

class MongoFieldWrongException(SelfException):
    def __init__(self):
        super(MongoFieldWrongException, self).__init__()
        self.message = "the field of mongo just is sort, limit, count"

class MongoSortAttributeWrongException(SelfException):
    def __init__(self):
        super(MongoSortAttributeWrongException, self).__init__()
        self.message = "the sort attribute must be a tuple or list"