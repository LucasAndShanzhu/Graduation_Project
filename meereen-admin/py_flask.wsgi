#!/usr/bin/python
# -*- coding: utf-8 -*-

from werkzeug.contrib.fixers import ProxyFix
from application import app as application

application.wsgi_app = ProxyFix(application.wsgi_app)