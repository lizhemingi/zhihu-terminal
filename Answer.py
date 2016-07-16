#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: lizheming
@contact: nkdudu@126.com
@site: lizheming.top
@file: Answer.py
"""


from zhihu import zhihu, headers, clear, error, session, mul_get_request, mul_post_request
from bs4 import BeautifulSoup, NavigableString
import re
import json
import webbrowser
import termcolor


class Answer:
    url = None
    soup = None

    def __init__(self, url):
        self.url = url
        self.headers = headers.copy()
        self.headers["Referer"] = self.url

    def parse(self):
        #res = session.get(self.url, headers=self.headers)
        res = mul_get_request(session, self.url, headers=self.headers)
        if not res:
            return False
        #print res.content
        self.soup = BeautifulSoup(res.content, "html.parser")
        self._xsrf = re.findall(r'name="_xsrf" value="(\S+)"', res.content)[0]
        return True

    def check(self):
        if not self.soup:
            self.parse()

    def open_in_browser(self):
        webbrowser.open_new(self.url)

    def get_item(self):
        self.check()
        item = self.soup.find("div", class_="zm-item-answer  zm-item-expanded")
        return item

    def get_data_id(self):
        item = self.get_item()
        data_id = item.get("data-aid")
        return data_id

    def get_question(self):
        self.check()
        zm_title = self.soup.find("h2", class_="zm-item-title")
        return zm_title.find("a").get("href")

    def get_author_link(self):
        item = self.get_item()
        author_tag = item.find("a", class_="author-link")
        author_link = author_tag.get("href") if author_tag else None
        return author_link

    def get_full_answer(self):
        item = self.get_item()
        answer = item.find("div", class_="zm-editable-content clearfix")
        contents = answer.contents
        print "\n ",
        print_content(contents)
        print "\n",
        '''
        answer_content = item.find("div", class_="zm-editable-content clearfix").text.strip()
        return "    " + answer_content
        '''

    def vote_up(self):
        url = "https://www.zhihu.com/node/AnswerVoteBarV2"
        params = {
            "answer_id": self.get_data_id()
        }
        data = {
            "method": "vote_up",
            "_xsrf": self._xsrf,
            "params": json.dumps(params)
        }
        #res = session.post(url, data, headers=self.headers)
        res = mul_post_request(session, url, headers=self.headers, data=data)
        if not res:
            return
        #print res.content
        if not res.json()["r"]:
            print termcolor.colored("赞同成功", "blue")

    def vote_cancle(self):
        url = "https://www.zhihu.com/node/AnswerVoteBarV2"
        params = {
            "answer_id": self.get_data_id()
        }
        data = {
            "method": "vote_neutral",
            "_xsrf": self._xsrf,
            "params": json.dumps(params)
        }
        #res = session.post(url, data, headers=self.headers)
        res = mul_post_request(session, url, self.headers, data=data)
        if not res:
            return
        #print res.content
        if not res.json()["r"]:
            print termcolor.colored("取消成功", "blue")

    def vote_down(self):
        url = "https://www.zhihu.com/node/AnswerVoteBarV2"
        params = {
            "answer_id": self.get_data_id()
        }
        data = {
            "method": "vote_down",
            "_xsrf": self._xsrf,
            "params": json.dumps(params)
        }
        #res = session.post(url, data, headers=self.headers)
        res = mul_post_request(session, url, self.headers, data=data)
        if not res:
            return
        print res.content
        if not res.json()["r"]:
            print termcolor.colored("取消成功", "blue")

    def add_to_collections(self):
        '''
        暂不支持创建新的收藏夹
        '''
        url = "https://www.zhihu.com/collections/json?answer_id={}".format(self.get_data_id())
        #res = session.get(url, headers=self.headers)
        res = mul_get_request(session, url, headers)
        if not res:
            return
        collections = res.json()["msg"][0]
        print "\n",
        for i, m in enumerate(collections):
            print "{0}:{1}  {2}条答案  {3}人关注".format(i, m[1], m[3], m[4])
        print "\n",

        index = -1
        length = len(collections)
        while not (0 <= index < length):
            num = raw_input("请选择收藏夹序号(0-{}), 输入cancle取消操作\n".format(length-1))
            if num == "cancle":
                return
            try:
                index = int(num)
            except:
                print termcolor.colored("请输入正确的序号", "red")
        add_url = "https://www.zhihu.com/collection/add"
        data = {
            "answer_id": self.get_data_id(),
            "_xsrf": self._xsrf,
            "favlist_id": str(collections[index][0])
        }
        #res = session.post(add_url, data, headers=self.headers)
        res = mul_post_request(session, add_url, self.headers, data=data)
        if not res:
            return
        print "\n",
        if res.json()["r"] == 0:
            print termcolor.colored("收藏成功", "green")
        else:
            print termcolor.colored("您已经收藏过该答案", "green")

    def operate(self):
        if not self.parse():
            return True
        self.get_full_answer()
        while True:
            op = raw_input("Answer$ ")
            if op == "voteup":
                self.vote_up()
            elif op == "votedown":
                self.vote_down()
            elif op == "votecancle":
                self.vote_cancle()
            elif op == "collect":
                self.add_to_collections()
            elif op == "author":
                url = self.get_author_link()
                if not url:
                    print termcolor.colored("作者为匿名用户", "green")
                else:
                    from User import User
                    user = User(zhihu + url)
                    if user.operate():
                        return True
            elif op == "question":
                from Question import Question
                question = Question(zhihu + self.get_question())
                if question.operate():
                    return True
            elif op == "browser":
                self.open_in_browser()
            elif op == "pwd":
                self.get_full_answer()
            elif op == "clear":
                clear()
            elif op == "break":
                break
            elif op == "quit":
                return True
            elif op == "help":
                self.help()
            else:
                error()

    def help(self):
        info = "\n" \
           "**********************************************************\n" \
           "**\n" \
           "**  author:       查看作者\n" \
           "**  question:     查看问题\n" \
           "**  voteup:       赞同回答\n" \
           "**  votecancle:   取消赞同回答\n" \
           "**  votedown:     反对回答\n" \
           "**  collect:      收藏回答\n" \
           "**  pwd:          查看当前回答\n" \
           "**  browser:      在默认浏览器中查看\n" \
           "**  clear:        清屏\n" \
           "**  break:        返回上级操作目录\n" \
           "**  quit:         退出系统\n" \
           "**\n" \
           "**********************************************************\n"
        print termcolor.colored(info, "green")


def print_content(contents):
    for content in contents:
        name = content.name
        #if not isinstance(content, Tag):
        if isinstance(content, NavigableString):
            s = str(content)
            s = s.replace("\n","")
            print s.strip()
        else:
            if name == "img":
                '''
                img = content.find("img")
                if img:
                    print img.get("src")
                '''
                print "[图片]"
            elif name == "br":
                print ""
            elif name == "noscript":
                continue
            elif name == "li":
                print "•",
            print_content(content.contents)