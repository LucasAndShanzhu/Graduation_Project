# -*- coding: utf-8 -*-

from application import app

class RecordModel(object):

    @staticmethod
    def recordAction(userId, itemId, action):
        connect = app.mysql.connect()
        cursor = connect.cursor()
        success = True
        try:
            sql = "insert into user_action(user_id, item_id, action) values({}, %s, %s)".format(userId)
            cursor.execute(sql, (itemId, action))
            connect.commit()
            connect.close()
        except Exception as e:
            print e
            success = False
        return success

    @staticmethod
    def getUserRecord(userId):
        connect = app.mysql.connect()
        cursor = connect.cursor()
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
        connect.close()
        return recordList