# -*- coding: utf-8 -*-
# @时间 : 2020-03-06 01:09
# @作者 : 陈祥安
# @文件名 : crawler.py
# @公众号: Python学习开发
from dataclasses import dataclass
from loguru import logger as crawler
from typing import Optional, Type, AsyncIterator, Dict, Any
from types import TracebackType
from config import MongoConfig
import aiohttp
from utils import aio_retry, MongoPool
import async_timeout
from contextlib import asynccontextmanager


@dataclass(frozen=True)
class Response:
    status: int
    source: str


@dataclass
class HTTPClient:
    def __post_init__(self):
        self.session = aiohttp.ClientSession()

    async def close(self):
        crawler.info("close session")
        await self.session.close()

    async def __aenter__(self) -> "HTTPClient":
        return self

    async def __aexit__(self,
                        exc_type: Optional[Type[BaseException]],
                        exc_val: Optional[BaseException],
                        exc_tb: Optional[TracebackType], ) -> Optional[bool]:
        await self.close()
        return None

    @aio_retry()
    async def get(self, url: str, headers: Optional[Dict[str, Any]] = None,
                  proxy: Optional[str] = None,
                  source_type: str = "text",
                  ssl_flag=False,
                  status_code: int = 200, timeout: int = 5) -> Response:
        """

        :param url: url
        :param headers: headers
        :param source_type: source type:text or buff
        :param status_code: successful code
        :param timeout: default 5s
        :param proxy: default No
        :param ssl_flag: default False
        :return:
        """
        if headers is None:
            headers = {
                "User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 "
                               "(KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36")}

        params = {"headers": headers, "ssl": ssl_flag}
        if proxy:
            params["proxy"] = proxy
        with async_timeout.timeout(timeout):
            async with self.session.get(url,**params) as req:
                status = req.status
                if status in [status_code, 201]:
                    if source_type == "text":
                        source = await req.text()
                    elif source_type == "buff":
                        source = await req.read()

        crawler.info(f"get url:{url},status:{status}")
        res = Response(status=status, source=source)
        return res


@dataclass
class Crawler:

    def __post_init__(self):
        self.mongo_config = MongoConfig
        self.mongo_pool = MongoPool

    @asynccontextmanager
    async def http_client(cls) -> AsyncIterator[HTTPClient]:
        client = HTTPClient()
        try:
            yield client
        finally:
            await client.close()

    async def init_all(self, init_mongo=True) -> None:
        """
        :return:
        """

        if init_mongo:
            crawler.info("init mongo")
            self.mongo_pool(
                host=self.mongo_config["host"],
                port=self.mongo_config["port"],
                maxPoolSize=self.mongo_config["max_pool_size"],
                minPoolSize=self.mongo_config["min_pool_size"]
            )
