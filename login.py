#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: lizheming
@contact: nkdudu@126.com
@site: lizheming.top
@file: login.py

登录文件,参考
"""

import requests
import termcolor
import cookielib
import ConfigParser
import re
import sys
import os
import platform
import time


headers = {
    'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0",
    'Host': "www.zhihu.com",
    #"Referer": "www.zhihu.com"
}

session = requests.session()
session.cookies = cookielib.LWPCookieJar("cookies")
try:
    session.cookies.load()
except:
    pass


def read_from_config():
    cf = ConfigParser.ConfigParser()
    cf.read("config.ini")
    mail = cf.get("account","mail")
    password = cf.get("account","password")
    return mail, password


def getxsrf(content):
    return re.findall(r'name="_xsrf" value="(\S+)"', content)[0]


def download_captcha():
    url = "http://www.zhihu.com/captcha.gif?type=login"
    r = session.get(url, params={"r": int(time.time())}, headers=headers)
    if int(r.status_code) != 200:
        print "验证码请求失败"
        sys.exit()
    image_name = "verify." + r.headers['content-type'].split("/")[1]
    open( image_name, "wb").write(r.content)
    """
        System platform: https://docs.python.org/2/library/platform.html
    """
    termcolor.colored("正在调用外部程序渲染验证码 ... ", "magenta")
    if platform.system() == "Linux":
        termcolor.colored("Command: xdg-open %s &" % image_name , "magenta")
        os.system("xdg-open %s &" % image_name)
    elif platform.system() == "Darwin":
        termcolor.colored("Command: open %s &" % image_name , "magenta")
        os.system("open %s &" % image_name)
    elif platform.system() == "SunOS":
        os.system("open %s &" % image_name)
    elif platform.system() == "FreeBSD":
        os.system("open %s &" % image_name)
    elif platform.system() == "Unix":
        os.system("open %s &" % image_name)
    elif platform.system() == "OpenBSD":
        os.system("open %s &" % image_name)
    elif platform.system() == "NetBSD":
        os.system("open %s &" % image_name)
    elif platform.system() == "Windows":
        os.system("%s" % image_name)
    else:
        termcolor.colored("我们无法探测你的作业系统，请自行打开验证码 %s 文件，并输入验证码。" % os.path.join(os.getcwd(), image_name) )

    print termcolor.colored("请输入验证码: ", "cyan")
    captcha_code = raw_input()
    return captcha_code


def login(debug=False):
    email, password = read_from_config()
    try:
        res = session.get("https://www.zhihu.com", headers=headers)
    except:
        sys.exit()
    _xsrf = getxsrf(res.content)
    captcha = download_captcha()
    data = {
        "email": email,
        "password": password,
        "remember_me": "true",
        "_xsrf": _xsrf,
        "captcha": captcha
    }
    url = "https://www.zhihu.com/login/email"
    res = session.post(url, data=data, headers=headers)
    if res.json()["r"] == 0:
        print termcolor.colored("登录成功", "green")
        if debug:
            print termcolor.colored("执行python zhihu.py, 可以体验在终端中刷知乎咯.^_^", "cyan")
        session.cookies.save()
        return True
    else:
        print termcolor.colored("登录失败", "red")
        print termcolor.colored(res.json()["msg"], "red")
        #print res.json()["errcode"]
        return False


def islogin(debug=False):
    #index = mul_get_request(session, zhihu, headers=headers)
    try:
        index = session.get("https://www.zhihu.com", headers=headers)
    except:
        print termcolor.colored("网络故障,请检查您的网络设置", "yellow")
        sys.exit()
    if index.content.find("最新动态") != -1:
        if debug:
            print termcolor.colored("已经登录过啦", "magenta")
        username = re.findall(r'<span class="name">(.*)</span>', index.content)[0]
        return True, username
    else:
        print termcolor.colored("正在为您登录...", "magenta")
        return False, None


if __name__ == "__main__":
    flag, username = islogin(True)
    if not flag:
        login(True)
