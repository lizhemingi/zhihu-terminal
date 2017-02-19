#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: lizheming
@contact: nkdudu@126.com
@site: lizheming.top
@file: TimeLine.py
"""

import re
import termcolor
from zhihu import zhihu, error, clear


class TLItem:
    item = None

    def __init__(self, item, _xsrf):
        self.item = item
        self._xsrf = _xsrf

    def get_id(self):
        item = self.item
        tid = item.get("id")
        tid = tid[tid.find("-")+1:]
        return tid

    def get_feed_type(self):
        item = self.item
        feedtype = item.get("data-feedtype")
        return feedtype

    def get_source(self):
        source = self.item.find("div", class_="feed-source")
        return source

    def get_content(self):
        content = self.item.find("div", class_="feed-content")
        return content

    def get_rich_text(self):
        item = self.item
        item_rich_text = item.find("div", class_="zm-item-rich-text expandable js-collapse-body")
        return item_rich_text

    def get_resource_id(self):
        item_rich_text = self.get_rich_text()
        tid = self.get_id()
        resource_id = item_rich_text.get("data-resourceid") if item_rich_text else tid[1:tid.find("_")]
        return resource_id

    def get_titles(self):
        source = self.get_source()
        title = source.text.strip()
        title = title.replace("\n", " ")
        titles = re.split(r'\s+', title)
        return titles

    def get_create_time(self):
        titles = self.get_titles()
        create_time = ''.join(titles[-2:])
        return create_time

    def get_vote_number(self):
        item = self.item
        vote = item.find("span", class_="count")
        vote_number = "(" + vote.text + "赞)" if vote else None
        return vote_number

    def get_feed_title(self):
        feedtype = self.get_feed_type()
        source = self.get_source()
        titles = self.get_titles()
        vote_number = self.get_vote_number()
        links = source.find_all("a", class_="zg-link author-link")
        member = links[0].text + ''.join(("、" + a.text) for a in links[1:])
        create_time = self.get_create_time()
        source_type = titles[-3] + vote_number if vote_number else titles[-3]
        if feedtype.find("ARTICLE_VOTE_UP") != -1:
            zone = source.find("a", class_="question_link")
            zl = ""
            if zone:
                zl = "赞了{}".format(zone.text)
            feed_title = termcolor.colored(member + "  ", "red") + termcolor.colored(zl + source_type + ":\t" + create_time, "white")
        elif feedtype.find("ARTICLE_CREATE") != -1:
            zone = source.find("a", class_="question_link")
            zl = ""
            if zone:
                zl = "在{}".format(zone.text)
            feed_title = termcolor.colored(member + "  ", "red") + termcolor.colored(zl + source_type + ":\t" + create_time, "white")
        else:
            feed_title = termcolor.colored(member + "  ", "red") + termcolor.colored(source_type + ":\t" + create_time, "white")
        return feed_title

    def get_feed_title_another(self):
        source = self.get_source().text
        feed_title = source.replace("\n", "")
        feed_title = feed_title.replace("\s+"," ")
        return feed_title

    def get_question_info(self):
        content = self.get_content()
        question = content.select("a")[0]
        question_link = zhihu + question.get("href")
        question_content = termcolor.colored(question.text, "cyan")
        question_content = question_content.replace("\n", "")
        return question_link, question_content

    def get_answer_link(self):
        item_rich_text = self.get_rich_text()
        url = None
        if item_rich_text:
            url = zhihu + item_rich_text.get("data-entry-url")
        return url

    def get_answer_info(self):
        content = self.get_content()
        zhsummary = content.findAll("div", class_="zh-summary summary clearfix")
        answer_summary = "  " + ''.join(a.text.strip() for a in zhsummary) if zhsummary else None
        ahref = zhsummary[0].find("a", class_="toggle-expand") if zhsummary else None
        answer_link = None
        if ahref:
            answer_link = ahref["href"]
            if answer_link.find("zhuanlan") == -1:
                answer_link = zhihu + answer_link
        return answer_link, answer_summary

    def get_author_info(self):
        content = self.get_content()
        feedtype = self.get_feed_type()
        author_link = None
        author_name = None
        if feedtype == "ANSWER_VOTE_UP":
            author_tag = content.find("div", class_="zm-item-answer-author-info")
            if author_tag:
                author = author_tag.find("a", class_="author-link")
                if author:
                    author_link = zhihu + author.get("href")
                    author_name = author.text
                else:
                    author_name = "匿名用户"
        elif feedtype == "ANSWER_CREATE":
            source = self.get_source()
            author = source.find("a")
            author_link = author.get("href")
            author_name = author.text
        return author_link, author_name

    def get_zhuanlan_link(self):
        content = self.get_content()
        zhuanlan_link = content.find("a", class_="post-link").get("href")
        return zhuanlan_link

    def get_item_info(self):
        tid = self.get_id()
        resource_id = self.get_resource_id()
        feed_title = self.get_feed_title()
        question_link, question_content = self.get_question_info()
        answer_link, answer_summary = self.get_answer_info()
        author_link, author_name = self.get_author_info()
        answer_link = self.get_answer_link()
        if author_name:
            question_content += termcolor.colored("(" + author_name + ")", "green")
        return tid, [feed_title, question_content, answer_summary], [question_link, answer_link, author_link, resource_id]

    def operate(self):
        d = self.get_item_info()
        ftype = self.get_feed_type()
        print "\n".join(i for i in d[1] if i) + "\n"
        while True:
            global flag
            op = raw_input("Time Line Item$ ")
            if op == "answer":
                if ftype.startswith("ANSWER"):
                    #print d[2][1]
                    from Answer import Answer
                    answer = Answer(d[2][1])
                    #print answer.get_full_answer()
                    if answer.operate():
                        flag = False
                        return True
                else:
                    error()
            elif op == "question":
                if ftype.startswith("ANSWER") or ftype.startswith("QUESTION"):
                    #print d[2][0]
                    from Question import Question
                    question = Question(d[2][0])
                    if question.operate():
                        flag = False
                        return True
                else:
                    error()
            elif op == "author":
                if d[2][2]:
                    #print d[2][2]
                    from User import User
                    user = User(d[2][2], self._xsrf)
                    if user.operate():
                        flag = False
                        return True
                else:
                    error()
            elif op == "zhuanlan":
                if ftype.find("ARTICLE") != -1:
                    url = self.get_zhuanlan_link()
                    from Zhuanlan import Zhuanlan
                    zhuanlan = Zhuanlan(url)
                    if zhuanlan.operate():
                        flag = False
                        return True
                else:
                    error()
            elif op == "pwd":
                print "\n".join(i for i in d[1] if i) + "\n"
            elif op == "help":
                self.help()
            elif op == "break":
                break
            elif op == "clear":
                clear()
            elif op == "quit":
                flag = False
                return True
            else:
                error()

    def help(self):
        info = "\n" \
           "*************************************************************************\n" \
           "**\n" \
           "**  answer:     查看回答(仅当TL条目与回答相关时)\n" \
           "**  author:     查看回答的作者(仅当TL条目与回答相关时)\n" \
           "**  question:   查看问题(仅当TL条目与回答或问题相关时)\n" \
           "**  zhuanlan:   查看专栏(仅当TL条目与专栏相关时)\n" \
           "**  pwd:        查看当前TL条目内容\n" \
           "**  clear:      清屏\n" \
           "**  break:      返回上级操作目录\n" \
           "**  quit:       退出系统\n" \
           "**\n" \
           "************************************************************************\n"
        print termcolor.colored(info, "green")