---
title: centos7进入单用户模式修改root密码
tags:
  - 基础运维
categories:
  - Linux
date: 2018-08-30 11:28:56
---

# init方法
<!--more-->
1、centos7的grub2界面会有两个入口，正常系统入口和救援模式；

2、修改grub2引导

在正常系统入口上按下”`e`“，会进入`edit模式`，搜寻`ro`那一行，以`linux16`开头的；

把`ro`更改成`rw`；（把只读更改成可写）

把`rhgb quiet`删除；（`quiet`模式没有代码行唰唰的走，可以删除）

增加`init=/bin/sh`；（或`init=/bin/bash`,指定shell环境)

按下`ctrl+x`来启动系统。

3、修改root密码

#passwd                       #修改密码

#touch /.autorelabel      #据说是selinux在重启后更新label

#exec /sbin/init              #正常启动init进程