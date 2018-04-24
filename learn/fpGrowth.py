# -*- coding: utf-8 -*-
# @Author: shanzhu
# @Date:   2018-02-26 14:44:21
# @Last Modified by:   shanzhu
# @Last Modified time: 2018-02-26 19:48:09

def TreeNode(object):
    def __init__(self, name, parent=None, childrens=None, next=None):
        self.name = name
        self.