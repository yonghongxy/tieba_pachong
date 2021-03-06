#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: yyh
@project: pachong
@file: pull.py
@time: 2019/7/9 9:48
@desc:
"""
import json
import os
import re
import requests
from bs4 import BeautifulSoup
from pprint import pprint
# 获取主贴列表
from post import Post, PostDetail, TieBa, PostComment


def if_int_none(var):
    if var is None:
        return 0
    else:
        return var


def if_str_none(var):
    if var is None:
        return ""
    else:
        return var


def get_dict_value(key, map):
    if key in map.keys():
        return map[key]
    return ''


# 获取帖子内容
def set_post_detail(_post=None):
    if _post.details is None:
        _post.details = []
    print(_post.get_url())
    r = requests.get(_post.get_url(), headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    if len(soup.select("div.pb_footer")) == 0:
        print('该帖已被删除')
        return

    if _post.thread_id is None:
        scripts = soup.find_all('script')
        for sc in scripts:
            bo = False
            if sc.text.find('thread_id') >= 0:
                thread_id_s = re.findall("thread_id(.+?),", sc.text)
                for _tis in thread_id_s:
                    thread_id = re.findall("\d+", _tis)[0]
                    if len(thread_id) > 5:
                        _post.thread_id = thread_id
                        bo = True
                        break
            if bo:
                break

    reply_num_spans = soup.select("div.pb_footer")[0].select('li.l_reply_num > span')
    _post.pageNum = reply_num_spans[1].text
    reply = soup.select("div.left_section")[0]
    post_content_list = reply.select("#j_p_postlist > div")
    i = 0
    for content in post_content_list:
        post_content = json.loads(content.attrs['data-field'])
        json_content = post_content['content']
        json_author = post_content['author']
        i = i + 1
        if i == 1 and _post.author_pic is not None:
            _post.author_pic = content.select("a.p_author_face > img")[0].attrs['src']
        post_detail = PostDetail()
        post_detail.content = get_dict_value('content', json_content)
        post_detail.post_id = get_dict_value('post_id', json_content)
        if post_detail.content == '':
            content_html = content.select('#post_content_%s' % (post_detail.post_id))
            if len(content_html) != 0:
                post_detail.content = content_html[0].text
                _imgs = content_html[0].find_all('img')
                img_paths = []
                for img in _imgs:
                    img_paths.append(img.attrs['src'])
                post_detail.imgs = img_paths
        else:
            post_detail.set_content_imgs()
        post_detail.post_no = get_dict_value('post_no', json_content)
        post_detail.thread_id = _post.thread_id
        post_detail.reply_num = get_dict_value('comment_num', json_content)
        post_detail.author_id = get_dict_value('user_id', json_author)
        post_detail.author_name = get_dict_value('user_name', json_author)
        if post_detail.author_name is None:
            post_detail.author_name = '该用户已不存在'
        post_detail.author_nickname = get_dict_value('user_nickname', json_author)
        post_detail.author_portrait = get_dict_value('portrait', json_author)
        post_detail.author_pic = content.select("a.p_author_face > img")[0].attrs['src']
        post_detail.floor = '%s%s' % (get_dict_value('post_no', json_content), '楼')
        post_detail.date = get_dict_value('date', json_content)
        # 添加评论
        if post_detail.reply_num > 0:
            set_post_comment(post_detail)
        _post.details.append(post_detail)
    if _post.currNum < int(_post.pageNum):
        _post.currNum = _post.currNum + 1
        set_post_detail(_post)


# 获取对应评论帖的所有回复
def set_post_comment(_post_detail):
    print(_post_detail.get_comment_url())
    if _post_detail.comments is None:
        _post_detail.comments = []
    r = requests.get(_post_detail.get_comment_url(), headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    comment_htmls = soup.select('li.lzl_single_post.j_lzl_s_p')
    if len(comment_htmls) == 0:
        return
    for comment_html in comment_htmls:
        comment = PostComment()
        comment.content = comment_html.select("span.lzl_content_main")[0].text.lstrip().rstrip()
        data_field = json.loads(comment_html.attrs['data-field'])
        comment.comment_id = data_field['spid']
        comment.username = data_field['user_name']
        comment.now_time = comment_html.select("span.lzl_time")[0].text
        _post_detail.comments.append(comment)
    if len(comment_htmls) == 10 and _post_detail.reply_num > 10:
        _post_detail.comment_curr_num = _post_detail.comment_curr_num + 1
        set_post_comment(_post_detail)


def set_post_list(tieba):
    print(tieba.get_url())
    if tieba.posts is None:
        tieba.posts = []
    r = requests.get(tieba.get_url())
    soup = BeautifulSoup(r.text, "lxml")
    if len(soup.select('.icon-attention')) != 0 and soup.select('.icon-attention')[0].text == '抱歉，根据相关法律法规和政策，本吧暂不开放。':
        tieba.isMiss = 0
        return
    lis = soup.select('li.j_thread_list.clearfix')
    if tieba.currNum == 1:
        if len(soup.select('.last.pagination-item')) > 0:
            tieba.pageNum = int(int(str(soup.select('.last.pagination-item')[0].attrs['href']).split("pn=")[1]) / 50) - 1
        tieba_title = soup.select(".card_top_wrap.clearfix.card_top_theme")[0]
        tieba.menNum = tieba_title.select(".card_num")[0].select('.card_menNum')[0].text
        tieba.infoNum = tieba_title.select(".card_num")[0].select('.card_infoNum')[0].text
        tieba.slogan = tieba_title.select("p.card_slogan")[0].text
        pprint(vars(tieba))
    for item in lis:
        post = Post()
        if 'data-field' not in item.attrs.keys():
            continue
        __df_text__ = item.attrs['data-field']
        __df_text_dict__ = json.loads(__df_text__)
        post.id = __df_text_dict__['id']
        post.author_name = __df_text_dict__['author_name']
        post.author_nickname = __df_text_dict__['author_nickname']
        post.author_portrait = __df_text_dict__['author_portrait']
        post.reply_num = __df_text_dict__['reply_num']
        post.is_top = __df_text_dict__['is_top']
        post.tieba_name = tieba.name
        post.source_page_num = tieba.currNum
        if len(item.select('div.j_th_tit ')) != 0:
            post.title = item.select('div.j_th_tit ')[0].a.text
        if len(item.select('.tb_icon_author')) > 0:
            post.author_id = json.loads(item.select('.tb_icon_author')[0]['data-field'])['user_id']
        if post.is_use():
            tieba.posts.append(post)
    if tieba.currNum < tieba.pageNum:
        if tieba.maxNum > 0 and tieba.currNum > tieba.maxNum:
            return
        else:
            tieba.currNum = tieba.currNum + 1
            set_post_list(tieba)


def save_post(_post):
    txt_name = _post.title
    p = re.compile(r'[\/:*?"<>|]')
    txt_name = re.sub(p, "#", txt_name)
    tieba_path = save_base_path + _post.tieba_name + "\\第" + str(_post.source_page_num) + "页\\"
    if not os.path.exists(tieba_path):
        os.makedirs(tieba_path)
    with open(tieba_path + txt_name + ".txt", 'w', encoding='utf-8') as post_file:
        post_str = '\t|标题：%s \t|作者： %s \t|回帖数: %s \n\n' % (_post.title, _post.author_name, _post.reply_num)
        post_file.write(post_str)
        for detail in _post.details:
            detail_str = '\t|回复:%s\n\t|回复人:%s\n\t|回复时间:%s\n\t|%s\n\t|评论数:%s' % (
                detail.get_content_text(), detail.author_name, detail.date, detail.floor, detail.reply_num)
            post_file.write(detail_str)
            if detail.reply_num > 0:
                for comment in detail.comments:
                    comment_str = '\n\t\t|%s\t\t|评论人:%s\t\t|评论时间:%s' % (
                        comment.content, comment.username, comment.now_time)
                    post_file.write(comment_str)
            post_file.write('\n\n')
            imgs = detail.imgs
            for img in imgs:
                save_img(img, tieba_path + '\\' + str(_post.id) + '\\' + str(detail.post_id) + '\\')


def save_img(url, file_path):
    # 保存图片到磁盘文件夹 file_path中，默认为当前脚本运行目录下的 book\img文件夹
    try:
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        # 获得图片后缀
        file_suffix = '.jpg'
        if file_path.find('.png'):
            file_suffix = '.png'
        elif file_path.find('.gif'):
            file_suffix = '.gif'
        elif file_path.find('.jpeg'):
            file_suffix = '.jpeg'
        file_name = url[url.rfind('/') + 1:url.rfind('.')]
        # 拼接图片名（包含路径）
        filename = '{}{}{}{}'.format(file_path, os.path.sep, file_name, file_suffix)
        # 下载图片，并保存到文件夹中
        response = requests.get(url)
        with open(filename, 'wb') as f:
            f.write(response.content)
        print('下载图片%s,完成！' % (url))
    except IOError as e:
        print('文件操作失败', e)
    except Exception as e:
        print('错误 ：', e)


if __name__ == '__main__':
    save_base_path = '.\\贴吧\\'
    headers = {
        'User - Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '
                        'like Gecko) Chrome/75.0.3770.100 Safari/537.36'}
    tieBa_name = input("请输入要爬取的贴吧名称:")
    maxNum = input("请输入要爬取的页数:")
    if maxNum is None or tieBa_name == '':
        -1
    else:
        maxNum = int(maxNum)
    if tieBa_name is None or tieBa_name == '':
        tieBa_name = "一蓑烟雨"
    tieba = TieBa(name=tieBa_name, maxNum=maxNum)
    set_post_list(tieba)
    if tieba.isMiss == 0:
        print('该吧不存在')
    else:
        _post_list = tieba.posts
        print(len(_post_list))
        for post in _post_list:
            set_post_detail(post)
            save_post(post)
