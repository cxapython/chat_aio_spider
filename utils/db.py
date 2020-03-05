# -*- coding: utf-8 -*-
# @时间 : 2020-03-04 22:30
# @作者 : 陈祥安
# @文件名 : db.py
# @公众号: Python学习开发
from dataclasses import dataclass
from typing import Optional


@dataclass
class SaveData:
    _id: int  # chat的id
    title: str  # 标题
    description: str  # 描述
    author: str  # 作者
    price: float  # 价格
    tags: Optional[str]  # 分类


if __name__ == '__main__':
    s = SaveData(
        _id=1,title = 2,description = "233",author = "cxa",price = 1.23,tags = "233"
    )
    # s._id = 1
    # s.title = 2
    # s.description = "233"
    # s.author = "cxa"
    # s.price = 1.23
    # s.tags = "233"
    print(s.__dict__)
