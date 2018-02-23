# -*- coding: utf-8 -*-
# @Author: shanzhu
# @Date:   2017-12-04 12:17:32
# @Last Modified by:   shanzhu
# @Last Modified time: 2018-01-22 19:50:04

import ConfigParser

class ConfigItem(object):
    def __init__(self, name):
        self.name = name

    def set(self, key, value):
        setattr(self, key, value)

    def get(self, key):
        if hasattr(self, key):
            return getattr(self, key)
        return None

class Config(object):
    def __init__(self, ini_filename):
        self.config = ConfigParser.ConfigParser()
        self.config.read(ini_filename)
        self._handle()

    def _handle(self):
        sections = self.config.sections()
        for section in sections:
            item = ConfigItem(section)
            options = self.config.options(section)
            for option in options:
                value = self.config.get(section, option)
                if value.find(',') != -1:
                    value = value.split(',')
                item.set(option, value)
            setattr(self, section, item)