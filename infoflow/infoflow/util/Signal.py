# -*- coding: utf-8 -*-
# @Author: shanzhu
# @Date:   2017-12-05 20:32:33
# @Last Modified by:   shanzhu
# @Last Modified time: 2017-12-11 11:07:34

import signal
import os

from app_email import MailSender

#当程序遇到特殊情况必须停止时，被调用。
class Signal(object):
    def __init__(self, *args):
        self.need_quit_object_list = [obt for obt in args if hasattr(obt, 'quit') and hasattr(getattr(obt, 'quit'), '__call__')]
        self.need_alarm_pbject_list = [obt for obt in args if hasattr(obt, 'alarm') and hasattr(getattr(obt, 'alarm'), '__call__')]
        signal.signal(signal.SIGTERM, self.quit)
        signal.signal(signal.SIGALRM, self.alarm)

    def add(self, sig, handler):
        signal.signal(sig, handler)

    def quit(self, *args):
        for obt in self.need_quit_object_list:
            obt.quit()
        os._exit(0)

    def alarm(self, *args):
        for obt in self.need_alarm_pbject_list:
            obt.alarm()

    @staticmethod
    def signal(sig, target=-1):
        if target < 0:
            target = os.getpid()
        os.kill(target, sig)

