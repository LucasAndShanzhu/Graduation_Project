# -*- coding: utf-8 -*-
# @Author: shanzhu
# @Date:   2018-02-09 10:01:56
# @Last Modified by:   shanzhu
# @Last Modified time: 2018-02-09 10:01:56

from . import loginBp, userRegBp, actionReocrdBp

def registerBp(app):
    app.register_blueprint(loginBp.loginBp)
    app.register_blueprint(userRegBp.userRegBp)
    app.register_blueprint(actionReocrdBp.actionReocrdBp)

