#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: 袁永宏
@project: tieba_pachong
@file: xs.py
@time: 2019/8/2 14:34
@desc:
"""
from ebooklib import epub
import requests
from bs4 import BeautifulSoup
from ebooklib.epub import Link

if __name__ == '__main__':
    proxies = ['']
    proxies = {
        "http": "http://localhost:1080",
    }
    baseUrl = 'http://www.xyyuedu.com'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                             '(KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'}

    res = requests.get(baseUrl + '/gdmz/sidamingzhu/sgyy/', proxies=proxies, headers=headers)
    res.encoding = 'GBK'
    soup = BeautifulSoup(res.text, "lxml")
    i = 0
    book = epub.EpubBook()
    # set metadata
    book.set_identifier('id1234568')
    book.set_title('沧海')
    book.set_language('zh')
    book.add_author('凤歌')
    links = []
    cs = []
    for li in soup.select('.zhangjie2 > li'):
        i = i + 1
        # if i == 1:
        #     continue
        title = li.find('a').attrs['title']
        print('下载 # %s' %(title, ))
        res_con = requests.get(baseUrl + li.find('a').attrs['href'], proxies=proxies, headers=headers)
        res_con.encoding = 'GBK'
        soup_con = BeautifulSoup(res_con.text, 'lxml')
        content = u'<h1>{}</h1> {}'
        ps = ''
        for p in soup_con.select('.onearcxsbd > p'):
            ps = ps + str(p)
        content = content.format(title, ps)
        c1 = epub.EpubHtml(title=title, file_name='chap_0%s.xhtml' % (i,))
        c1.content = content
        book.add_item(c1)
        cs.append(c1)
        links.append(Link('chap_0%s.xhtml' % (i,), title, 'chap_0%s' % (i,)))
    book.toc = (links)
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    # add default NCX and Nav file

    # define CSS style
    style = 'p{text-indent:2em; }'
    nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)
    # add CSS file
    book.add_item(nav_css)
    # basic spine
    book.spine = ['nav']
    book.spine.extend(cs)
    # write to the file
    epub.write_epub('sgyy.epub', book, {})
