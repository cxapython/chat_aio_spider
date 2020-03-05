# -*- coding: utf-8 -*-
# @时间 : 2020-03-06 01:19
# @作者 : 陈祥安
# @文件名 : chat_spider.py
# @公众号: Python学习开发
from common.crawler import Crawler, Response
from contextvars import ContextVar
import asyncio
from dataclasses import dataclass
from loguru import logger as crawler
import ujson
from utils import Motor
from config import SpiderConfig
import datetime

CONCURRENCY_NUM = SpiderConfig.get("CONCURRENCY_NUM")
MAX_RETRY_TIMES = SpiderConfig.get("MAX_RETRY_TIMES")
USE_PROXY = SpiderConfig.get("USE_PROXY")
TIME_INTERVAL = SpiderConfig.get("TIME_INTERVAL")
sem_count = ContextVar("asyncio.Semaphore")


@dataclass
class ChatSpider(Crawler):
    async def fetch(self, url):
        async with self.http_client() as session:
            response = await session.get(url)
            return response

    async def main(self, url):
        async with sem_count.get():
            result = await self.fetch(url)
            await self.parse_json(result)
            if TIME_INTERVAL:
                await asyncio.sleep(TIME_INTERVAL)

    async def parse_json(self, result: Response):
        code = result.status
        if code != 200:
            crawler.warning("访问出错")
        json_data = ujson.loads(result.source)
        data_list = json_data.get("data")
        tasks = []
        t_a = tasks.append
        for data in data_list:
            item = dict()
            item["_id"] = data.get("_id")
            item["title"] = data.get("title")
            item["description"] = data.get("description")
            item["author"] = data.get("authorId").get("customerName")
            item["price"] = data.get("price", 0)
            item["tags"] = data.get("tags")
            item["update_time"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            t_a(item)

        await Motor.save_data(self.mongo_pool, tasks, key="_id")

    def _make_url(self, page_id):
        return f"https://gitbook.cn/activities?page={page_id}&type=new&isSelected=false"

    async def start(self):
        sem = asyncio.Semaphore(2)
        sem_count.set(sem)
        await self.init_all()
        tasks = [asyncio.create_task(self.main(self._make_url(i))) for i in range(1, 21)]
        await asyncio.wait(tasks)


if __name__ == '__main__':
    c = ChatSpider()
    asyncio.run(c.start())
