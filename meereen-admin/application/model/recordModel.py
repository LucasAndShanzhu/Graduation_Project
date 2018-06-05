# -*- coding: utf-8 -*-

from application import app

class RecordModel(object):

    @staticmethod
    def recordAction(userId, itemId, action):
        app.mysql.connect()
        cursor = app.mysql.getCursor()
        success = True
        try:
            sql = "insert into user_action(user_id, item_id, action) values({}, %s, %s)".format(userId)
            cursor.execute(sql, (itemId, action))
        except Exception as e:
            print e
            success = False
        app.mysql.close()
        return success

    @staticmethod
    def getUserRecord(userId):
        app.mysql.connect()
        cursor = app.mysql.getCursor()
        recordList = []
        try:
            sql = "select * from user_action where user_id=%d"
            cursor.execute(sql, userId)
        except Exception as e:
            print e
        else:
            output = cursor.fetchall()
            if output and output[0]:
                recordList = output
        app.mysql.close()
        return recordList