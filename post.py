#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: yyh
@project: pachong
@file: post.py
@time: 2019/7/10 9:50
@desc: 帖子信息类
"""
import re

from bs4 import BeautifulSoup


class TieBa(object):
    def __init__(self, name=None, pageNum=1, maxNum=None,
                 isMiss=1):
        self.name = name
        self.pageNum = pageNum
        self.currNum = 1
        self.menNum = 0
        self.infoNum = 0
        self.slogan = ''
        self.maxNum = maxNum
        self.posts = None
        self.isMiss = isMiss

    def get_url(self):
        return "https://tieba.baidu.com/" + self.name + "?pn=" + str((self.currNum - 1) * 50)


class Post(object):
    def __init__(self, title=None, is_top=None, id=None, reply_num=None, author_name=None, author_id=None,
                 author_portrait=None,
                 author_nickname=None, author_pic=None, details=None, thread_id=None, forum_id=None, pageNum=1):
        self.title = title
        self.is_top = is_top
        self.id = id
        self.reply_num = reply_num
        self.author_name = author_name
        self.author_id = author_id
        self.author_portrait = author_portrait
        self.author_nickname = author_nickname
        self.author_pic = author_pic
        self.details = details
        self.thread_id = thread_id
        self.forum_id = forum_id
        self.pageNum = pageNum
        self.currNum = 1
        self.source_page_num = 1
        self.tieba_name = None

    def get_url(self):
        return "https://tieba.baidu.com/p/" + str(self.id) + "?pn=" + str(self.currNum)

    def is_use(self):
        if self.title is None:
            return False
        return True


class PostDetail(object):

    def __init__(self, content=None, author_name=None, author_id=None, author_portrait=None, thread_id=None,
                 author_nickname=None, author_pic=None, post_no=None, post_id=None, reply_num=0, comments=None
                 , imgs=None):
        self.content = content
        self.content_text = None
        self.author_name = author_name
        self.author_id = author_id
        self.author_portrait = author_portrait
        self.author_nickname = author_nickname
        self.author_pic = author_pic
        self.post_no = post_no
        self.post_id = post_id
        self.thread_id = thread_id
        self.reply_num = reply_num
        self.comments = comments
        self.floor = ''
        self.date = None
        self.comment_curr_num = 1
        self.imgs = imgs

    def get_comment_url(self):
        return "https://tieba.baidu.com/p/comment?tid=" + str(self.thread_id) + "&pid=" + str(
            self.post_id) + "&pn=" + str(
            self.comment_curr_num)

    def get_content_text(self):
        if self.content is None:
            return ""
        else:
            return BeautifulSoup(self.content, "lxml").text

    def set_content_imgs(self):
        if self.content is None:
            self.imgs = []
        else:
            soup = BeautifulSoup(self.content, "lxml")
            _imgs = soup.find_all('img')
            img_paths = []
            for img in _imgs:
                img_paths.append(img.attrs['src'])
            self.imgs = img_paths


class PostComment(object):
    def __init__(self):
        self.thread_id = None
        self.post_id = None
        self.comment_id = None
        self.username = None
        self.user_id = None
        self.now_time = None
        self.content = None
        self.ptype = None
        self.come_from = None
        self.during_time = None


if __name__ == '__main__':
    with open('C:\\Users\\Administrator\\Desktop\\script.txt', 'r', encoding='utf-8') as f:
        str = f.read()
        # print(re.findall(r"\"thread_id\":\"(.+?)\",", str))
        print(re.findall("thread_id(.+?),", str))
        print(str)
        print(re.findall('\d+','":"5466413161"'))

