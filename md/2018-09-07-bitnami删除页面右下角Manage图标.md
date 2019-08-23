---
title: bitnami删除页面右下角Manage图标
tags:
  - bitnami
categories:
  - Linux
date: 2018-09-07 15:38:02
---

# Bitnami info page
<!--more-->
![1](1.png)

![2](2.png)
**How to remove the banner(如何删除旗帜)**

如果你想删除的旗帜，你只需要使用工具`bnconfig`,执行下面命令。

**Linux and OS X Systems**

``` jboss-cli
sudo /opt/bitnami/apps/软件目录/bnconfig --disable_banner 1
```

然后重启APache:

``` vim
$ sudo /opt/bitnami/ctlscript.sh restart apache
```

**Windows Systems**

进入算计路径：:

`cd apps\`软件目录

``` mipsasm
bnconfig.exe --disable_banner 1
```

 

