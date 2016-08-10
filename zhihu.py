#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: lizheming
@contact: nkdudu@126.com
@site: lizheming.top
@file: zhihu.py
"""

from login import islogin, login
#from logo import logo
import requests
import cookielib
from bs4 import BeautifulSoup
import re
import os
import json
import termcolor
import threading
import time
import random
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


logo = ''\
   '     $$'\
   '    $$$                                    &&&&$$$$ ##$$$$$$$$$$$$$$$$$$#$$$ \n'\
   '   $$$              $$$$$$$$$$$$$$$        ##$$$$$$$$$$$$$$$$$$o;       ;\n'\
   '  $$$$$$$$$$$$$$$  $$$$$$$$$$$$$$$                      *$$o           #\n'\
   ' $$$    $$$        $$$         $$$          $$$         *$$o        $$$$\n'\
   '$$*     $$$        $$$         $$$           $$$$       *$$o       $$$$\n'\
   '        $$$        $$$         $$$            $$$$      *$$o     $$$$\n'\
   '        $$o        $$$         $$$              $$$     *$$o    $$$o\n'\
   ';$$$$$$$$$$$$$$$$  $$$         $$$                      *$$o\n'\
   '$$$$$$$$$$$$$$$$$* $$$         $$$     ;$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\n'\
   '       $$$         $$$         $$$                      *$$o\n'\
   '       $$$         $$$         $$$                      *$$o\n'\
   '      $$$$$$$      $$$         $$$                      *$$o\n'\
   '     $$$;  $$$$    $$$         $$$                      *$$o\n'\
   '    $$$$     $$$   $$$$$ $$$$$$$$$                      *$$o\n'\
   '  $$$$!       $$      $$$$*                             $$$;\n'\
   '$$$$$                  ;                        $$$$$$$$$$$\n'\
                                                      '$$$$$$\n'



zhihu = "https://www.zhihu.com"
session = requests.Session()
session.cookies = cookielib.LWPCookieJar("cookies")
datas = []
tlitems = []
flag = True
op_stop = False
offset = 0
temp = 0
limit = 5
tid = None
_xsrf = None

headers = {
    'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0",
    'Host': "www.zhihu.com",
    #"Referer": "www.zhihu.com"
}


def mul_get_request(session, url, headers, timeout=10, n=5, **kwargs):
    t = 0
    while n:
        if t == 2:
           print termcolor.colored("网络缓慢,请稍后..", "red")
        try:
            res = session.get(url, headers=headers, timeout=timeout, **kwargs)
            return res
        except:
            n -= 1
            t += 1
    exit()
    return None


def mul_post_request(session, url, headers, timeout=10, n=5, **kwargs):
    t = 0
    while n:
        if t == 2:
           print termcolor.colored("网络缓慢,请稍后..", "red")
        try:
            res = session.post(url, headers=headers, timeout=timeout, **kwargs)
            return res
        except:
            n -= 1
            t += 1
    exit()
    return None


def loadsession():
    global session
    try:
        session.cookies.load(ignore_discard="true")
    except:
        termcolor.colored("加载异常", "red")
        pass


loadsession()
l, username = islogin()
if not l:
    if not login():
        sys.exit()
    loadsession()


def index():
    global tid
    global _xsrf
    global session

    #res = session.get(zhihu, headers=headers)
    res = mul_get_request(session=session, url=zhihu, headers=headers)
    if not res:
        sys.exit()
    #print res.content
    _xsrf = re.findall(r'name="_xsrf" value="(\S+)"', res.content)[0]

    soup = BeautifulSoup(res.content, "html.parser")
    items = soup.select(".feed-item.folding.feed-item-hook")
    for item in items:
        #tid, t, l = get_item_info_another(item)
        from TimeLine import TLItem
        iitem = TLItem(item, _xsrf)
        tid, t, l = iitem.get_item_info()
        datas.append([t, l, tid])
        tlitems.append(iitem)


def worker():
    global tid
    global datas
    global offset
    global session

    url = "https://www.zhihu.com/node/HomeFeedListV2"
    params = {
        "start": tid,
        "offset": 21
    }
    data = {
        "method":"next",
        "_xsrf":_xsrf,
        "params":json.dumps(params)
    }
    while flag:
        if len(datas) - offset > 10 * limit:
            time.sleep(1)
            continue
        try:
            res = session.post(url, data, headers=headers)
        except:
            continue
        msgs = None
        try:
            msgs = res.json()["msg"]
        except:
            #print res.content
            #print "link error 1326"
            continue
        for msg in msgs:
            soup = BeautifulSoup(msg, "html.parser")
            item = soup.select(".feed-item.folding.feed-item-hook")[0]
            from TimeLine import TLItem
            iitem = TLItem(item, _xsrf)
            tid, t, l = iitem.get_item_info()
            datas.append([t, l, tid])
            tlitems.append(iitem)
        params["start"] = tid
        params["offset"] += 21
        data["params"] = json.dumps(params)


def welcome():
    clear()
    print termcolor.colored(logo, "cyan")
    print termcolor.colored("Hello {}, 欢迎使用终端版知乎".format(username), "yellow")


def next_page(**kwargs):
    clear()
    global op_stop
    op_stop = True


def pre_page(**kwargs):
    clear()
    global offset
    global op_stop
    op_stop = True
    offset = max(0, offset - limit*2)


def pwd():
    global temp
    global offset

    clear()
    offset -= limit
    temp = offset
    for x in range(limit):
        data = datas[temp + x]
        print offset
        print "\n".join(i for i in data[0] if i) + "\n"
        offset += 1


def bye():
    global flag
    global op_stop
    flag = False
    op_stop = True
    print termcolor.colored("Bye", "cyan")
    print termcolor.colored("有任何建议欢迎与我联系: nkdudu@126.com", "cyan")


def clear():
    i = os.system("clear")


def help():
    info = "\n" \
           "**********************************************************\n" \
           "**\n" \
           "**  回车:    下一页\n" \
           "**  next:    下一页\n" \
           "**  pre:     上一页\n" \
           "**  pwd:     当前页\n" \
           "**  #Num.:   选中具体TL条目进行操作(只限当前页中的条目)\n" \
           "**  clear:   清屏\n" \
           "**  quit:    退出系统\n" \
           "**\n" \
           "**********************************************************\n"
    print termcolor.colored(info, "green")


def error():
    print termcolor.colored("输入错误, 可通过", "red") + termcolor.colored("help", "cyan") + termcolor.colored("查看", "red")


def exit():
    global flag
    global op_stop
    flag = False
    op_stop = True
    print termcolor.colored("因网络故障程序退出,请检查您的网络设置", "yellow")


main_ops = {
    "": next_page,
    "next": next_page,
    "pre": pre_page,
    "pwd": pwd,
    "clear": clear,
    "quit": bye,
    "exit": bye,
    "help": help
}


def main():
    global flag
    global offset
    global temp
    global op_stop
    global thread

    ithread = threading.Thread(target=index)
    ithread.start()
    welcome()
    ithread.join()

    thread = threading.Thread(target=worker)
    thread.start()
    mode = re.compile(r"^\d+$")
    while flag:
        temp = offset
        x = 0
        while x < limit:
            if (temp + x) >= len(datas):
                termcolor.colored("访问速度过快，请稍候", "magenta")
                continue
            data = datas[temp + x]
            print offset
            print "\n".join(i for i in data[0] if i) + "\n"
            offset += 1
            x += 1
        x = 0

        op_stop = False
        while not op_stop:
            op = raw_input("Time Line$ ")
            if not re.match(mode, op):
                main_ops.get(op, error)()
            else:
                opn = int(op)
                if temp <= opn < offset:
                    item = tlitems[opn]
                    if item.operate():
                        bye()
                        flag = False
                        break
                else:
                    print termcolor.colored("请输入正确的序号", "red")
    thread.join()


if __name__ == "__main__":
    main()