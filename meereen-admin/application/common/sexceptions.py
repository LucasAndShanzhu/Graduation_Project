# -*- coding: utf-8 -*-

class BaseSelfException(Exception):
    def __init__(self, *args):
        message = args[0]
        super(BaseSelfException, self).__init__(*args)
        self.message = message

class MongoTimeoutException(BaseSelfException):
    def __init__(self):
        message = 'the mongo server has gone'
        super(MongoTimeoutException, self).__init__(message)

class MysqlTimeoutException(Exception):
    def __init__(self):
        message = 'the mysql server has gone'
        super(MysqlTimeoutException, self).__init__(message)
