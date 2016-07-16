#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: lizheming
@contact: nkdudu@126.com
@site: lizheming.top
@file: Question.py
"""

from zhihu import zhihu, headers, clear, error, limit, session, mul_get_request, mul_post_request
from User import User
import webbrowser
import re
from bs4 import BeautifulSoup
import termcolor
import json


class Question:
    url = None
    soup = None
    flag = True

    def __init__(self, url):
        self.url = url
        self.headers = headers.copy()

    def parse(self):
        #res = session.get(self.url, headers=self.headers)
        res = mul_get_request(session, self.url, headers)
        if not res:
            return False
        self.soup = BeautifulSoup(res.content, "html.parser")
        #print res.content
        self._xsrf = re.findall(r'name="_xsrf" value="(\S+)"', res.content)[0]
        return True

    def check(self):
        if not self.soup:
            self.parse()

    def open_in_browser(self):
        webbrowser.open_new(self.url)

    def get_title(self):
        self.check()
        #title = self.soup.find("h2", class_="zm-item-title zm-editable-content").text.strip()
        title = self.soup.find("h2", class_="zm-item-title")
        title_content = title.find("span", class_="zm-editable-content").text.strip()
        return title_content

    def show_detail(self):
        self.check()
        detail = self.soup.find("div", id="zh-question-detail")
        from Answer import print_content
        if detail.find("div", class_="zm-editable-content"):
            detail = detail.find("div", class_="zm-editable-content")
        elif detail.find("div", class_="zh-summary summary clearfix"):
            detail = detail.find("div", class_="zh-summary summary clearfix")
        print_content(detail.contents)
        #content = detail.text.strip()
        #content = self.soup.find("div", class_="zm-editable-content").text.strip()
        #print content

    def get_data_resourceid(self):
        self.check()
        detail = self.soup.find("div", id="zh-question-detail")
        resource_id = str(detail.get("data-resourceid"))
        return resource_id

    def get_topics(self):
        self.check()
        tags = self.soup.select("a[class=zm-item-tag]")
        return [tag.text.strip() for tag in tags]

    def get_answer_num(self):
        self.check()
        answer_num_tag = self.soup.find("h3", id="zh-question-answer-num")
        answer_num = int(answer_num_tag.get("data-num")) if answer_num_tag else 0
        return answer_num

    def get_follower_num(self):
        self.check()
        follow_num = self.soup.find("div", class_="zg-gray-normal").strong.text
        return int(follow_num)

    def show_base_info(self):
        #title = self.get_title()
        topics = self.get_topics()
        answer_num = self.get_answer_num()
        follower_num = self.get_follower_num()
        #print termcolor.colored(title, "blue")
        print termcolor.colored("话题：" + " ".join(topics), "blue")
        print termcolor.colored("回答：{0}  关注{1}".format(answer_num, follower_num), "blue")

    def follow_question(self):
        self.parse()
        button = self.soup.find("button", class_="follow-button zg-follow zg-btn-green")
        if not button:
            print termcolor.colored("您已经关注了问题:{}".format(self.get_title()), "red")
            return
        url = "https://www.zhihu.com/node/QuestionFollowBaseV2"
        params = {
            "question_id": self.get_data_resourceid()
        }
        data = {
            "method": "follow_question",
            "_xsrf": self._xsrf,
            "params": json.dumps(params)
        }
        #res = session.post(url, data, headers=self.headers)
        res = mul_post_request(session, url, headers, data=data)
        if not res:
            return
        if res.json()["r"] == 0:
            print termcolor.colored("关注问题:{}成功".format(self.get_title()), "blue")

    def unfollow_question(self):
        self.parse()
        button = self.soup.find("button", class_="follow-button zg-unfollow zg-btn-white")
        if not button:
            print termcolor.colored("您还没有关注问题:{}".format(self.get_title()), "red")
            return
        url = "https://www.zhihu.com/node/QuestionFollowBaseV2"
        params = {
            "question_id": self.get_data_resourceid()
        }
        data = {
            "method": "unfollow_question",
            "_xsrf": self._xsrf,
            "params": json.dumps(params)
        }
        #res = session.post(url, data, headers=self.headers)
        res = mul_post_request(session, url, headers, data=data)
        if not res:
            return
        if res.json()["r"] == 0:
            print termcolor.colored("取消关注问题:{}成功".format(self.get_title()), "blue")

    def get_answers(self):
        self.check()
        answer_num = self.get_answer_num()
        if not answer_num:
            print termcolor.colored("该问题还没有回答", "magenta")
            return
        items = self.soup.find_all("div", class_="zm-item-answer  zm-item-expanded")
        answer_wrap = self.soup.find("div", id="zh-question-answer-wrap")
        summarys = answer_wrap.find_all("div", class_="zh-summary summary clearfix")
        #mode = re.compile(r"^zm-item-vote-info")
        #items = sorted(items, lambda x, y: int(y.find("div", class_=mode).get("data-votecount")) - int(x.find("div", class_=mode).get("data-votecount")))
        count = 0
        iter = 0
        times = 0
        for item in items:
            count += 1
            summary = summarys[iter]
            iter += 1
            qaitem = QAItem(item, self._xsrf, summary)
            yield qaitem
        while count <= answer_num:
            url_token = re.findall(r"(\d+)", self.url)[0]
            url = "https://www.zhihu.com/node/QuestionAnswerListV2"
            pagesize = 10
            offset = pagesize * times + 10
            params = {
                "url_token": url_token,
                "pagesize": pagesize,
                "offset": offset
            }
            data = {
                "method": "next",
                "params": json.dumps(params),
                "_xsrf": self._xsrf
            }
            #res = session.post(url, data, headers=self.headers)
            res = mul_post_request(session, url, headers, data=data)
            if not res:
                return
            #print res.content
            items = res.json()["msg"]
            #print items
            for item in items:
                count += 1
                iitem = BeautifulSoup(item, "html.parser")
                qaitem = QAItem(iitem, self._xsrf)
                yield qaitem
            times += 1

    def answer_operate(self):
        answers = self.get_answers()
        answer_num = self.get_answer_num()
        i = 0
        count = 0
        answerlist = []
        mode = re.compile(r"\d+")
        for answer in answers:
            if i < limit and count < answer_num:
                print count
                answer.show_item_info()
                answerlist.append(answer)
                i += 1
                count += 1
            if i == limit or count == answer_num:
                while True:
                    op = raw_input("All Answers of Question$ ")
                    if op == "":
                        if count == answer_num:
                            print termcolor.colored("没有更多回答", "red")
                        else:
                            i = 0
                            clear()
                            break
                    elif re.match(mode, op):
                        opn = int(op)
                        if opn < len(answerlist):
                            if answerlist[opn].operate():
                                return True
                    elif op == "pwd":
                        clear()
                        start = max(0, count - limit)
                        for x in xrange(start, count):
                            print x
                            answerlist[x].show_item_info()
                    elif op == "browser":
                        self.open_in_browser()
                    elif op == "break":
                        return False
                    elif op == "help":
                        self.help2()
                    elif op == "quit":
                        return True
                    elif op == "clear":
                        clear()
                    else:
                        error()

    def operate(self):
        #self.show_base_info()
        if not self.parse():
            return True
        print termcolor.colored(self.get_title(), "blue")
        while True:
            op = raw_input("Question$ ")
            if op == "follow":
                self.follow_question()
            elif op == "unfollow":
                self.unfollow_question()
            elif op == "answers":
                if self.answer_operate():
                    return True
            elif op == "pwd":
                print termcolor.colored(self.get_title(), "blue")
            elif op == "info":
                self.show_base_info()
            elif op == "detail":
                self.show_detail()
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
        return False

    def help(self):
        info = "\n" \
           "**********************************************************\n" \
           "**\n" \
           "**  info:      问题的基本信息\n" \
           "**  detail:    问题的描述\n" \
           "**  follow:    关注问题\n" \
           "**  unfollow:  取消关注问题\n" \
           "**  answers:   查看问题的所有回答\n" \
           "**  pwd:       显示当前问题\n" \
           "**  browser:   在默认浏览器中查看\n" \
           "**  clear:     清屏\n" \
           "**  break:     返回上级操作目录\n" \
           "**  quit:      退出系统\n" \
           "**\n" \
           "**********************************************************\n"
        print termcolor.colored(info, "green")

    def help2(self):
        info = "\n" \
           "**********************************************************\n" \
           "**\n" \
           "**  回车:      下一页\n" \
           "**  #Num.:     选中具体回答条目进行操作(仅限从0到当前最后一条)\n" \
           "**  pwd:       显示当前回答页\n" \
           "**  browser:   在默认浏览器中查看\n" \
           "**  clear:     清屏\n" \
           "**  break:     返回上级操作目录\n" \
           "**  quit:      退出系统\n" \
           "**\n" \
           "**********************************************************\n"
        print termcolor.colored(info, "green")


class QAItem:
    item = None

    def __init__(self, item, _xsrf, summary=None):
        self.item = item
        self._xsrf = _xsrf
        self.headers = headers.copy()
        self.summary = summary

    def get_author_info(self):
        author_info = self.item.find("div", class_="zm-item-answer-author-info").text.strip()
        author_info = author_info.replace("\n","")
        return author_info

    def get_author_link(self):
        author_link_tag = self.item.find("a", class_="author-link")
        author_link = author_link_tag.get("href") if author_link_tag else None
        return author_link

    def get_item_vote_info(self):
        mode = re.compile(r"^zm-item-vote-info")
        vote_info_tag = self.item.find("div", class_=mode)
        vote_info = vote_info_tag.text.strip()
        #a = re.findall(r'[ , \n]+', vote_info)[0]
        a = re.findall(r'\s+', vote_info)
        if a:
            vote_info = vote_info.replace(a[0], "")
        vote_info = re.sub(r'[\s+\n\t]', '', vote_info)
        vote_count = str(vote_info_tag.get("data-votecount"))
        if not vote_info:
            vote_info += "{}人赞同".format(vote_count)
        return vote_info

    def get_answer_summary(self):
        if self.summary:
            return self.summary.text.strip()
        answer_summary = self.item.find("div", class_="zh-summary summary clearfix")
        if answer_summary:
            return answer_summary.text.strip()
        return ""

    def get_answer_link(self):
        #answer_link = self.item.find("div", class_="zm-item-rich-text expandable js-collapse-body").get("data-entry-url")
        #return answer_link
        url = self.item.find("link",itemprop="url")
        return url.get("href")

    def get_data_id(self):
        data_aid = self.item.get("data-aid")
        return str(data_aid)

    def show_item_info(self):
        author_info = self.get_author_info()
        vote_info = self.get_item_vote_info()
        answer_summary = "  " + self.get_answer_summary()
        #answer_summary = answer_summary.replace("\S+","")
        print termcolor.colored(author_info, "green"),
        print termcolor.colored("({})".format(vote_info), "white")
        print answer_summary
        print "\n",

    def vote_up_answer(self):
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
        res = mul_post_request(session, url, headers, data=data)
        if not res:
            return
        #print res.content
        if res.json()["r"] == 0:
            print termcolor.colored("赞同成功", "blue")

    def vote_down_answer(self):
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
        res = mul_post_request(session, url, headers, data=data)
        if not res:
            return
        #print res.content
        if res.json()["r"] == 0:
            print termcolor.colored("取消赞同成功", "blue")

    def vote_cancle_answer(self):
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
        res = mul_post_request(session, url, headers, data=data)
        if not res:
            return
        #print res.content
        if res.json()["r"] == 0:
            print termcolor.colored("取消赞同成功", "blue")

    def operate(self):
        self.show_item_info()
        while True:
            op = raw_input("Question Answer Item$ ")
            if op == "voteup":
                self.vote_up_answer()
            elif op == "votedown":
                self.vote_down_answer()
            elif op == "votecancle":
                self.vote_cancle_answer()
            elif op == "answer":
                from Answer import Answer
                answer = Answer(zhihu + self.get_answer_link())
                if answer.operate():
                    return True
            elif op == "author":
                author_link = self.get_author_link()
                if author_link:
                    user = User(zhihu + self.get_author_link())
                    if user.operate():
                        return True
                else:
                    print termcolor.colored("回答者为匿名用户", "red")
            elif op == "pwd":
                self.show_item_info()
            elif op == "help":
                self.help()
            elif op == "break":
                break
            elif op == "clear":
                clear()
            elif op == "quit":
                return True
            else:
                error()

    def help(self):
        info = "\n" \
           "**********************************************************\n" \
           "**\n" \
           "**  answer:       查看回答\n" \
           "**  author:       查看作者\n" \
           "**  voteup:       赞同回答\n" \
           "**  votecancle:   取消赞同回答\n" \
           "**  votedown:     反对回答\n" \
           "**  pwd:          当前问题回答条目\n" \
           "**  clear:        清屏\n" \
           "**  break:        返回上级操作目录\n" \
           "**  quit:         退出系统\n" \
           "**\n" \
           "**********************************************************\n"
        print termcolor.colored(info, "green")