# -*- coding: utf-8 -*-
# @Author: shanzhu
# @Date:   2017-12-04 11:15:43
# @Last Modified by:   shanzhu
# @Last Modified time: 2018-03-22 20:17:39
import logging
import traceback

class LoggerLevelNotSupportException(Exception):
    def __init__(self):
        super(LoggerLevelNotSupportException, self).__init__()
        self.message = 'sorry, the level of logging is not supported now'

    def __str__(self):
        return self.message

class Logger(object):

    def __init__(self, logger_name, file):
        handler = logging.FileHandler(file, mode='a')
        handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
        self.logger = logging.getLogger(logger_name)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.DEBUG)

    def write(self, message, level='info', **kwds):
        try:
            if level == 'debug':
                self.logger.debug(message, **kwds)
            elif level == 'info':
                self.logger.info(message, **kwds)
            elif level == 'warn':
                self.logger.warn(message, **kwds)
            else:
                raise LoggerLevelNotSupportException()
        except Exception as e:
            if isinstance(e, LoggerLevelNotSupportException):
                raise

    def error(self, message=''):
        message = traceback.format_exc() if message == '' else message
        try:
            self.logger.error(message)
        except:
            pass

    def __str__(self):
        return str(vars(self))