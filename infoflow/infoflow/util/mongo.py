# -*- coding: utf-8 -*-
# @Author: shanzhu
# @Date:   2017-12-11 21:03:38
# @Last Modified by:   shanzhu
# @Last Modified time: 2018-02-08 21:04:23
import pymongo
from bson.objectid import ObjectId
import time

from sexceptions import MongoFieldWrongException, MongoSortAttributeWrongException
from app_email import MailSender

class Mongo(object):

    ASC = pymongo.ASCENDING
    DESC = pymongo.DESCENDING

    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.link()

    def link(self):
        user = self.config.mongo.user
        passwd = self.config.mongo.passwd
        host = self.config.mongo.host if self.config.mongo.get('host') else '127.0.0.1'
        port = int(self.config.mongo.port) if self.config.mongo.get('port') else 27017 
        database = self.config.mongo.database
        mongo_uri = "mongodb://{}:{}@{}:{}/{}".format(user, passwd, host, port, database)
        retry_num = 0
        while True:
            try:
                self.mongo = pymongo.MongoClient(mongo_uri, serverSelectionTimeoutMS=3)
                self.database = self.mongo[database]
                self.mongo.admin.command('ping')
                break
            except pymongo.errors.ServerSelectionTimeoutError:
                if retry_num > 2:
                    self.logger.error()
                    MailSender.send(u'mongo is timeout, please check', subject='mongo')
                    exit(-2)
                retry_num += 1

    def close(self):
        self.mongo.close()
        self.mongo = None

    def get_collection(self, db=None, collection=None):
        if db is None:
            return self.database[collection]
        else:
            return self.mongo[db][collection]

    def find(self, collection, conditions=None, fields=None, options=None):
        if conditions is None:
            conditions = {}
        if not fields:
            fields = None
        _id = conditions.get('_id', None)
        if _id is not None:
            conditions['_id'] = ObjectId(_id)
        try:
            result = collection.find(conditions, fields)
            for key, value in fields.items():
                if key == 'sort':
                    if isinstance(value, tuple):
                        result = result.sort(*value)
                    elif isinstance(value, list):
                        result = result.sort(value)
                    else:
                        raise MongoSortAttributeWrongException()
                elif key == 'limit':
                    result = result.limit(value)
                elif key == 'count':
                    result = result.count()
                    return result
        except (pymongo.errors.OperationFailure, pymongo.errors.ServerSelectionTimeoutError):
            self.logger.error()
            exit(-2)
        except Exception as e:
            self.logger.error()
            exit(-2)
        else:
            output = []
            for data in result:
                if data.get('_id', None) is not None:
                    _id = str(data['_id'])
                    data['_id'] = _id
                output.append(data)
            return output

    def find_one(self, collection, conditions=None, fields=None):
        if conditions is None:
            conditions = {}
        _id = conditions.get('_id', None)
        if _id is not None:
            conditions['_id'] = ObjectId(_id)
        try:
            result = collection.find_one(conditions, fields)
        except (pymongo.errors.OperationFailure, pymongo.errors.ServerSelectionTimeoutError):
            self.logger.error()
            raise
        else:
            if result is None:
                return {}
            if result.get('_id', None) is not None:
                result['_id'] = str(result['_id'])
            return result

    def insert(self, collection, data):
        _id = None
        for times in range(5):
            try:
                _id = collection.insert_one(data)
            except (pymongo.errors.OperationFailure, pymongo.errors.ServerSelectionTimeoutError):
                self.logger.error()
                _id = None
            if _id:
                break
            time.sleep(1)
        return _id

    def update(self, collection, option, conditions=None):
        if conditions is None:
            conditions = {}
        _id = conditions.get('_id', None)
        if _id is not None:
            conditions['_id'] = ObjectId(_id)
        try:
            collection.update(conditions, option)
            return True
        except (pymongo.errors.OperationFailure, pymongo.errors.ServerSelectionTimeoutError):
            self.logger.error()
            return False

    def find_and_modify(self, collection, query, update_data):
        if query is None:
            query = {}
        _id = query.get("_id", None)
        if _id is not None:
            query["_id"] = ObjectId(_id)
        try:
            result = collection.find_and_modify(query, update_data)
            if result and '_id' in result:
                result['_id'] = str(result['_id'])
            return result
        except Exception:
            self.logger.error()
            raise

    def remove(self, collection, conditions=None):
        if conditions is None:
            conditions = {}
        _id = conditions.get('_id', None)
        if _id is not None:
            conditions['_id'] = ObjectId(_id)
        try:
            collection.remove(conditions)
            return True
        except (pymongo.errors.OperationFailure, pymongo.errors.ServerSelectionTimeoutError):
            self.logger.error()
            return False