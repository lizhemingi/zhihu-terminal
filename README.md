zhihu-terminal：终端版知乎
===============================

##Author:

* [lizheming](http://lizheming.top)

* <nkdudu@126.com>

##介绍

zhihu-terminal 采用 python2.7编写，通过在命令行中执行python程序运行知乎客户端，就可以用类似bash命令的方式来刷TL、来关注问题和给别人点赞啦。

更重要的是以后在实验开着命令行就不会被老板和同学发现我是在刷知乎了哦。。

本项目部分代码参考借鉴项目：[zhihu-python](<https://github.com/egrcc/zhihu-python>) , 感谢@[egrcc](https://github.com/egrcc)的分享。


**本项目代码在Mac OSX 10.10.5上开发及测试，尚未兼容其他系统。**

##快速开始

### 准备

**Tips** :

建议新建一个虚拟python环境并确保安装的python版本为2.7，以免与系统原有的依赖库出现版本冲突等问题。具体安装虚拟环境的步骤这里不再赘述。


**克隆本项目**

	git clone git@github.com:duduainankai/zhihu-terminal.git
	cd zhihu-terminal


**依赖**

本项目依赖于:

* [Beautiful Soup 4](http://www.crummy.com/software/BeautifulSoup/)
* [requests](https://github.com/kennethreitz/requests)
* [termcolor](https://pypi.python.org/pypi/termcolor)

准备好虚拟环境并激活，执行以下命令可直接安装依赖：


	pip install -r requirements.txt
  
  
ps. 可以执行以下命令查看是否正确安装


	pip list

  
 
### 开启终端知乎


**填写账号密码**
 
找到文件夹下的config.ini文件，填写登录帐号的邮箱和密码。

**测试登录**

	python login.py
  
login.py的代码实现参考的就是[zhihu-python](https://github.com/egrcc/zhihu-python)。

如果不出意外的话应该就可以得到下面的结果了。

![](/img/login.png)

**体验终端版知乎**


	python zhihu.py
  
正确登录之后执行上面的命令，应该就可以看到你自己的TL了(下面这图是我的)。

![](/img/TimeLine.png)

**操作目录**

我所定义的操作目录类似于linux下的工作目录(可以通过pwd查看)，操作目录可以分为Time Line、Question、Answer、User等，可以看到在输入命令的前面提示的就是当前所属的操作目录，同样也可以通过pwd查看更详细的信息。

**用命令来点赞**

在每一个操作目录下都可以执行特定的操作，比如给一个答案点赞、关注一个用户或问题等等，当然你不需要像背shell命令一样记下所有的操作，在每个操作目录下输入help就可以查看当前可以执行的命令及其解释了。

![](/img/help.png)

然后我就可以用"voteup"给这位仁兄的答案点赞了。

![](/img/zan.png)

查看一下知乎的动态 

![](/img/zhihu.png)

现在提供的功能还比较基本，可以先尝试着玩一下。有时间的话应该还会扩展的。

**轮带逛系列**

当然有些回答精华都在图片中(就像轮子哥带我们逛过的那些)，但是终端中目前还没找到太好的显示方法(有哪位大神有办法的话还望不吝赐教)，因此为了不扫大家的兴可以用"browser"命令在默认的浏览器中打开知乎，查看当前所在操作目录的内容。当然还是希望尽量多用这个终端版的知乎咯，毕竟开着命令行可以掩人耳目，让老板以为是在认真学习而不会想到是在刷知乎。

**欢迎使用**

欢迎克隆使用终端版知乎，能给个star当然就更好咯。

有任何问题、建议或者bug也希望能联系我，谢谢。

联系我
----------

- email: nkdudu@126.com
- github: https://github.com/duduainankai
- zhihu: https://www.zhihu.com/people/du-du-76-75