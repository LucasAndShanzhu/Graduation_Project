# -*- coding: utf-8 -*-
from pymongo import MongoClient
from sexceptions import MongoTimeoutException

class MongoUtil(object):
    """docstring for MongoDb"""
    def __init__(self, config):
        super(MongoUtil, self).__init__()
        self.user = config.MONGO_USERNAME
        self.password = config.MONGO_PASSWORD
        self.host = config.MONGO_HOST
        self.port = config.MONGO_PORT
        self.dbname = config.MONGO_DBNAME
        uri = "mongodb://{}:{}@{}:{}/{}".format(self.user, self.password, self.host, self.port, self.dbname)
        self.uri = uri
        self.db = None

    def link(self):
        self._link()
        if self.db is None:
            raise MongoTimeoutException()
        
    def _link(self):
        if self.db is None:
            try:
                mogno = MongoClient(self.uri, serverSelectionTimeoutMS=3)
                self.db = mongo[self.dbname]
                self.db.admin.command('ping')
            except Exception as e:
                self.db = None

    def getCollect(self, collect_name):
        return self.db[collect_name] if self.db is not None else None

    def close(self):
        if self.db:
            self.db.close()
            self.db = None