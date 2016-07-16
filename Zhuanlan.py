#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: lizheming
@contact: nkdudu@126.com
@site: lizheming.top
@file: Zhuanlan.py
"""

from zhihu import headers, clear, error, session
from bs4 import BeautifulSoup
import re
import webbrowser
import termcolor
import requests
import json
import sys


class Zhuanlan:
    url = None
    zhuanlan = None
    soup = None
    originalurl = None

    def __init__(self, url):
        #https://zhuanlan.zhihu.com/p/20825292
        self.originalurl = url
        number = re.findall(r"(\d+)",url)[0]
        self.url = "http://zhuanlan.zhihu.com/api/posts/" + str(number)

        self.headers = headers.copy()
        self.headers["Host"] = "zhuanlan.zhihu.com"

    def parse(self):
        self.se = requests.Session()
        for cookie in session.cookies:
            self.se.cookies.set_cookie(cookie)
        n = 3
        res = None
        while n > 0:
            try:
                res = self.se.get(self.url, headers=self.headers, timeout=30)
                break
            except:
                n -= 1
                return False
        if not res:
            print termcolor.colored("网络故障,请检查您的网络设置", "red")
            sys.exit()
        self.zhuanlan = dict(res.json())
        self.soup = BeautifulSoup(self.zhuanlan["content"], "html.parser")
        return True

    def open_in_browser(self):
        webbrowser.open_new(self.originalurl)

    def check(self):
        if not self.soup:
            self.parse()

    def get_title(self):
        self.check()
        return termcolor.colored(self.zhuanlan["title"], "blue")

    def get_content(self):
        self.check()
        from Answer import print_content
        print_content(self.soup.contents)

    def get_author_info(self):
        self.check()
        author = dict(self.zhuanlan["author"])
        return author["profileUrl"]

    def vote(self, type=1):
        self.check()
        url = self.url + "/rating"
        data = {}
        if type == 1:
            data["value"] = "none"
            try:
                self.se.put(url, json.dumps(data), headers=self.headers, timeout=15)
            except:
                print termcolor.colored("网络故障,请检查您的网络设置", "yellow")
                return
            data["value"] = "like"
        else:
            data["value"] = "none"
        self.headers['Content-Type'] = "application/json;charset=UTF-8"
        self.headers["Referer"] = self.originalurl
        self.headers["Origin"] = "https://zhuanlan.zhihu.com"
        self.headers['X-XSRF-TOKEN'] = self.se.cookies['XSRF-TOKEN']
        try:
            res = self.se.put(url, json.dumps(data), headers=self.headers, timeout=15)
        except:
            print termcolor.colored("网络故障,请检查您的网络设置", "yellow")
            return
        if res.status_code == 204:
            s = "取消赞同成功" if data["value"] == "none" else "赞同成功"
            print termcolor.colored(s, "blue")
        elif res.status_code == 404:
            s = "还没有赞同过" if data["value"] == "none" else "已经赞同过了"
            print termcolor.colored(s, "blue")

    def operate(self):
        if not self.parse():
            return True
        print self.get_title()
        while True:
            op = raw_input("zhuanlan$ ")
            if op == "content":
                self.get_content()
            elif op == "author":
                url = self.get_author_info()
                if not url:
                    print termcolor.colored("当前用户为匿名用户", "red")
                else:
                    from User import User
                    user = User(url)
                    if user.operate():
                        return True
            elif op == "voteup":
                self.vote(type=1)
            elif op == "votecancle":
                self.vote(type=2)
            elif op == "pwd":
                print self.get_title()
            elif op == "browser":
                self.open_in_browser()
            elif op == "clear":
                clear()
            elif op == "break":
                break
            elif op == "help":
                self.help()
            elif op == "quit":
                return True
            else:
                error()

    def help(self):
        info = "\n" \
           "**********************************************************\n" \
           "**\n" \
           "**  content:     查看内容\n" \
           "**  author:      查看作者\n" \
           "**  voteup:      赞同\n" \
           "**  votecancle:  取消赞同\n" \
           "**  pwd:         显示当前专栏\n" \
           "**  browser:     在默认浏览器中查看\n" \
           "**  break:       返回上级操作目录\n" \
           "**  clear:       清屏\n" \
           "**  quit:        退出系统\n" \
           "**\n" \
           "**********************************************************\n"
        print termcolor.colored(info, "green")