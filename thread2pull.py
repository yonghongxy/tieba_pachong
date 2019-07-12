#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: yyh
@project: pachong
@file: thread2pull.py
@time: 2019/7/11 16:59
@desc:
"""
import json
import queue
import threading
import time

from post import Post


class Crawl(threading.Thread):
    # 初始化

    def __init__(self, number, data_list=None):
        # 调用Thread 父类方法
        super(Crawl, self).__init__()
        # 初始化子类属性
        self.number = number
        self.data_list = data_list

    # 线程启动的时候调用
    def start(self):
        # 输出启动线程信息
        print('启动采集线程%d号' % self.number)
        # 如果请求队列不为空，则无限循环，从请求队列里拿请求url
        while self.req_list.qsize() > 0:
            # print(json.dumps(self.req_list.get(), default=lambda obj: obj.__dict__))
            print(vars(self.req_list.get()))


if __name__ == '__main__':
    # 生成请求队列
    req_list = queue.Queue()
    for i in range(1000):
        post = Post(title="第" + str(i) + "贴")
        # 生成数据队列 ，请求以后，响应内容放到数据队列里
        req_list.put(post)

    req_thread = []
    start_time = time.time()
    for i in range(3):
        t = Crawl(i + 1, req_list)  # 创造线程
        t.start()
        req_thread.append(t)

    try:
        for t in req_thread:
            t.join()
    except RuntimeError:
        pass
    print('完成时间:', time.time() - start_time)
