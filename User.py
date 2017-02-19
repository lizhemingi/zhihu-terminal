#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: lizheming
@contact: nkdudu@126.com
@site: lizheming.top
@file: User.py
"""

from zhihu import zhihu, headers, clear, error, limit, session, mul_post_request, mul_get_request
import webbrowser
from bs4 import BeautifulSoup
import re
import termcolor
import json


class User:
    url = None
    soup = None

    def __init__(self, url, _xsrf=None):
        self.url = url
        self.headers = headers.copy()
        self._xsrf = _xsrf
        #self.headers["Referer"] = self.url

    def parse(self):
        url = self.url
        #res = session.get(url, headers=self.headers)
        res = mul_get_request(session, url, headers)
        if not res:
            return False
        self.soup = BeautifulSoup(res.content, "html.parser")
        self.profile_header = self.soup.find("div", class_="zm-profile-header ProfileCard")
        # self._xsrf = re.findall(r'name="_xsrf" value="(\S+)"', res.content)[0]
        return True

    def check(self):
        if not self.soup:
            self.parse()

    def open_in_browser(self):
        webbrowser.open_new(self.url)

    def get_title_tag(self):
        self.check()
        title = self.soup.find("h1", class_="ProfileHeader-title")
        return title

    def get_name(self):
        title = self.get_title_tag()
        return title.find("span", class_="ProfileHeader-name").text.strip()

    def get_title(self):
        title = self.get_title_tag()
        name = self.get_name()
        des = title.find("span", class_="RichText ProfileHeader-headline").text.strip()
        return name + des

    def get_weibo(self):
        self.check()
        weibo_header = self.profile_header.find("a", class_="zm-profile-header-user-weibo")
        weibo = weibo_header.get("href") if weibo_header else None
        return weibo

    def open_weibo(self):
        weibo = self.get_weibo()
        if weibo:
            webbrowser.open_new(weibo)
        else:
            print termcolor.colored("该用户没有绑定微博", "magenta")

    def get_education(self):
        self.check()
        education_item = self.profile_header.find("span", class_="education item")
        education = education_item.get("title") if education_item else None
        return education

    def get_employment(self):
        self.check()
        employment_item = self.profile_header.find("span", class_="employment item")
        employment = employment_item.get("title") if employment_item else None
        return employment

    def get_agrees(self):
        self.check()
        agrees = re.findall(r"(\d+)", self.soup.find("div", class_="IconGraf").text)[0]
        return agrees

    def get_thanks(self):
        self.check()
        thanks = re.findall(r"(\d+)", self.soup.find("div", class_="Profile-sideColumnItemValue").text)[0]
        return thanks

    def get_behavior_numbers(self):
        self.check()
        numbers = self.profile_header.find_all("span", class_="num")
        return [int(number.text) for number in numbers]

    def get_following_numbers(self):
        self.check()
        follow_numbers = self.soup.find_all("div", class_="NumberBoard-value")
        return [int(number.text) for number in follow_numbers]

    def show_base_info(self):
        infos = list()
        title = self.get_title()
        infos.append(termcolor.colored(title, "magenta"))
        # education = self.get_education()
        # infos.append(termcolor.colored("教育经历:" + education, "magenta") if education else education)
        # employment = self.get_employment()
        # infos.append(termcolor.colored("工作经历:" + employment, "magenta") if employment else employment)
        # thanks = self.get_thanks()
        # agrees = self.get_agrees()
        # infos.append(termcolor.colored("获得{0}赞同  {1}感谢".format(agrees, thanks), "magenta"))
        following_numbers = self.get_following_numbers()
        infos.append(termcolor.colored("关注了{0}  关注者{1}".format(*following_numbers), "magenta"))
        # numbers = self.get_behavior_numbers()
        # infos.append(termcolor.colored("提问{0}  回答{1}  文章{2}  收藏{3}  公共编辑{4}".format(*numbers), "magenta"))
        info = "\n".join(x for x in infos if x)
        print info

    def get_answers(self):
        self.check()
        answer_num = int(self.soup.find("span", class_="Tabs-meta").text)
        for page in range(answer_num / 20 + 1):
            url = self.url + "/answers"
            params = {
                "order_by": "vote_num",
                "page": page + 1
            }
            #res = session.get(url, params=params, headers=self.headers)
            res = mul_get_request(session, url, headers, params=params)
            if not res:
                return
            soup = BeautifulSoup(res.content, "html.parser")
            zmitems = soup.select("div[class=zm-item]")
            for item in zmitems:
                yield UAItem(item, self._xsrf, self.get_name())

    def follow_member(self):
        self.parse()
        username = self.get_name()
        #follow_button = self.soup.find("button", class_="zg-btn zg-btn-follow zm-rich-follow-btn with-icon")
        follow_button = self.soup.find("button", class_="Button FollowButton Button--primary Button--blue")
        unfollow_button = self.soup.find("button", class_="Button FollowButton Button--primary Button--grey")
        if not follow_button and unfollow_button:
            print termcolor.colored("您已经关注了用户{}".format(username), "red")
            return
        data_id = str(follow_button.get("data-id"))
        url = "https://www.zhihu.com/node/MemberFollowBaseV2"
        params = {
            "hash_id": data_id
        }
        data = {
            "method": "follow_member",
            "params": json.dumps(params),
            "_xsrf": self._xsrf
        }
        #res = session.post(url, data=data, headers=self.headers)
        res = mul_post_request(session, url, headers, data=data)
        if not res:
            return
        if not res.json()["r"]:
            print termcolor.colored("关注用户{}成功".format(username), "blue")

    def unfollow_member(self):
        self.parse()
        username = self.get_title().split("，")[0].strip() #中文的逗号
        #unfollow_button = self.soup.find("button", class_="zg-btn zg-btn-unfollow zm-rich-follow-btn with-icon")
        follow_button = self.soup.find("button", class_="Button FollowButton Button--primary Button--blue")
        unfollow_button = self.soup.find("button", class_="Button FollowButton Button--primary Button--grey")
        if not unfollow_button and follow_button:
            print termcolor.colored("您还没有关注用户{0}".format(username), "red")
            return
        data_id = str(unfollow_button.get("data-id"))
        url = "https://www.zhihu.com/node/MemberFollowBaseV2"
        params = {
            "hash_id": data_id
        }
        data = {
            "method": "unfollow_member",
            "params": json.dumps(params),
            "_xsrf": self._xsrf
        }
        #res = session.post(url, data=data, headers=self.headers)
        res = mul_post_request(session, url, headers, data=data)
        if not res:
            return
        if not res.json()["r"]:
            print termcolor.colored("取消关注用户{}成功".format(username), "blue")

    def answer_operate(self):
        print "\n",
        answers = self.get_answers()
        answer_num = int(self.soup.find("span", class_="Tabs-meta").text)
        i = 0
        count = 0
        answerlist = []
        mode = re.compile(r"^\d+$")
        for answer in answers:
            if i < limit and count != answer_num:
                print count
                answer.show_item_info()
                answerlist.append(answer)
                i += 1
                count += 1
            if i == limit or count == answer_num:
                while True:
                    op = raw_input("{}\'s All Answers$ ".format(self.get_name()))
                    if op == "":
                        if count == answer_num:
                            print termcolor.colored("没有更多回答", "red")
                        else:
                            clear()
                            i = 0
                            break
                    elif re.match(mode, op.strip()):
                        opn = int(op)
                        if opn < len(answerlist):
                            if answerlist[opn].operate():
                                return True
                        else:
                            print termcolor.colored("请输入正确的序号", "red")
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
        if not self.parse():
            return True
        self.show_base_info()
        while True:
            op = raw_input("User$ ")
            if op == "follow":
                self.follow_member()
            elif op == "unfollow":
                self.unfollow_member()
            elif op == "answers":
                if self.answer_operate():
                    return True
            elif op == "pwd":
                self.show_base_info()
            elif op == "browser":
                self.open_in_browser()
            elif op == "break":
                break
            elif op == "help":
                self.help()
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
           "**  follow:     关注用户\n" \
           "**  unfollow:   取消关注用户\n" \
           "**  answers:    查看用户的回答\n" \
           "**  pwd:        查看用户\n" \
           "**  browser:    在默认浏览器中查看用户\n" \
           "**  break:      返回上级操作目录\n" \
           "**  clear:      清屏\n" \
           "**  quit:       退出系统\n" \
           "**\n" \
           "**********************************************************\n"
        print termcolor.colored(info, "green")

    def help2(self):
        info = "\n" \
           "**********************************************************\n" \
           "**\n" \
           "**  #Num.:      选中具体用户回答条目查看(仅限从0到当前最后一条)\n" \
           "**  回车:        下一页\n" \
           "**  pwd:        当前页\n" \
           "**  browser:    在默认浏览器中查看用户回答\n" \
           "**  break:      返回上级操作目录\n" \
           "**  clear:      清屏\n" \
           "**  quit:       退出系统\n" \
           "**\n" \
           "**********************************************************\n"
        print termcolor.colored(info, "green")


class UAItem:
    item = None

    def __init__(self, item, _xsrf, username):
        self.item = item
        self._xsrf = _xsrf
        self.username = username

    def get_vote_up_count(self):
        vote_up_count = self.item.find("a", class_="zm-item-vote-count js-expand js-vote-count").text
        return vote_up_count

    def get_question_content(self):
        question = self.item.find("a", class_="question_link")
        question_content = question.text.strip()
        return question_content

    def get_answer_link(self):
        question = self.item.find("a", class_="question_link")
        answer_link = str(question.get("href"))
        return answer_link

    def get_question_link(self):
        answer_link = self.get_answer_link()
        question_link = answer_link[:answer_link.find("answer")]
        return question_link

    def get_summary(self):
        summary = ""
        zhsummary = self.item.find("div", class_="zh-summary summary clearfix")
        if zhsummary:
            summary = zhsummary.text.strip()
        return summary

    def show_item_info(self):
        question_content = self.get_question_content()
        print termcolor.colored(question_content, "blue") + termcolor.colored("({}赞)".format(self.get_vote_up_count()), "white")
        print "    " + self.get_summary()
        print "\n",

    def get_data_id(self):
        item_answer = self.item.find("div", class_="zm-item-answer")
        return str(item_answer.get("data-aid"))

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
        #res = session.post(url, data)
        res = mul_post_request(session, url, headers, data=data)
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
        #res = session.post(url, data)
        res = mul_post_request(session, url, headers, data=data)
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
        #res = session.post(url, data)
        res = mul_post_request(session, url, headers, data=data)
        if not res:
            return
        #print res.content
        if not res.json()["r"]:
            print termcolor.colored("反对成功", "blue")

    def operate(self):
        self.show_item_info()
        while True:
            op = raw_input("{}\'s Answer Item$ ".format(self.username))
            if op == "voteup":
                self.vote_up()
            elif op =="votecancle":
                self.vote_cancle()
            elif op == "votedown":
                self.vote_down()
            elif op == "answer":
                answer_link = self.get_answer_link()
                from Answer import Answer
                answer = Answer(zhihu + answer_link)
                if answer.operate():
                    return True
            elif op == "question":
                from Question import Question
                question = Question(zhihu + self.get_question_link())
                if question.operate():
                    return True
            elif op == "pwd":
                self.show_item_info()
            elif op == "quit":
                return True
            elif op == "help":
                self.help()
            elif op == "clear":
                clear()
            elif op == "break":
                break
            else:
                error()

    def help(self):
        info = "\n" \
           "**********************************************************\n" \
           "**\n" \
           "**  answer:       查看回答\n" \
           "**  question:     查看问题\n" \
           "**  voteup:       赞同回答\n" \
           "**  votecancle:   取消赞同回答\n" \
           "**  votedown:     反对回答\n" \
           "**  pwd:          当前用户回答条目\n" \
           "**  clear:        清屏\n" \
           "**  break:        返回上级操作目录\n" \
           "**  quit:         退出系统\n" \
           "**\n" \
           "**********************************************************\n"
        print termcolor.colored(info, "green")