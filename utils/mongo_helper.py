# -*- coding: utf-8 -*-
# @时间 : 2020-02-21 12:24
# @作者 : 陈祥安
# @文件名 : mongo_helper.py
# @公众号: Python学习开发
from motor.motor_asyncio import AsyncIOMotorClient

from .singleton import Singleton
import asyncio
from loguru import logger as storage
from pymongo import UpdateOne
from dataclasses import dataclass
from collections import Iterable
from config import MongoConfig

try:
    import uvloop

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass


class MongoPool(AsyncIOMotorClient, Singleton):
    """
    全局mongo连接池
    """
    pass


@dataclass
class MotorOperation:

    def __post_init__(self):
        self.db_name = MongoConfig.get("db_name")

    async def save_data(self, pool, items, col="chat_list", key="_id"):
        """
        :param items:
        :param col:
        :param key:
        :return:
        """
        mb = pool()[self.db_name]
        if isinstance(items, Iterable):
            requests = list()
            r_a = requests.append
            for item in items:
                try:
                    r_a(UpdateOne({
                        key: item.get(key)},
                        {'$set': item},
                        upsert=True))
                except Exception as e:
                    storage.error(f"数据插入出错:{e.args}此时的item是:{item}")
            # bulk_write 只创建一次request即可插入多条数据
            await mb[col].bulk_write(requests, ordered=False, bypass_document_validation=True)
        elif isinstance(items, dict):
            try:
                await mb[col].update_one({
                    key: items.get(key)},
                    {'$set': items},
                    upsert=True)
            except Exception as e:
                storage.error(f"数据插入出错:{e.args}此时的item是:{items}")
