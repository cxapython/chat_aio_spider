# -*- coding: utf-8 -*-
# @时间 : 2020-03-05 00:08
# @作者 : 陈祥安
# @文件名 : __init__.py
# @公众号: Python学习开发
from config.config import config

c = config()
MongoConfig = c.get("mongo")
SpiderConfig = c.get("spider")
__all__ = ["MongoConfig", "SpiderConfig"]
