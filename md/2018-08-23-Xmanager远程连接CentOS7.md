---
title: Xmanager远程连接CentOS7
tags:
  - xmanager
  - 运维工具
  - 基础运维
categories:
  - Linux
date: 2018-08-23 17:04:02
---

# 1 安装epel源
<!--more-->
``` sql
yum install -y epel-release
```
# 2 安装lightdm和xfce

``` ebnf
yum install -y lightdm 
yum groupinstall -y xfce
```

## 2.1 修改配置文件

``` vim
vim /etc/lightdm/lightdm.conf
```
内容如下

``` ini
[XDMCPServer]
enabled=true
port=177
```

## 2.2 将Display Manager切换为lightdm

``` bash
systemctl disable gdm && systemctl enable lightdm
```

## 2.3 启动lightdm

``` ebnf
systemctl start lightdm
```

## 2.4 关闭防火墙

``` vbscript
systemctl stop firewalld.service
```

# 3 登录

打开Xmanger客户端，选择XDMCP并输入服务器的ip，回车运行即可。
输入账号密码
然后就出现下图：（如果正常跳过这步）
![enter description here](1.jpg)
**或者出现黑屏提示无法建立连接**
这是因为刚开始安装的是Gnome，所以系统默认使用它，现在要改成Xfce，最简单的方法就是把xfce.desktopz之外的文件都干掉。

``` maxima
cd /usr/share/xsessions/
mkdir bak
mv gnome* bak
systemctl restart lightdm
```
重新连接	
一切正常操作之后就成功连接了。然后就可以快速便捷的工作了。
