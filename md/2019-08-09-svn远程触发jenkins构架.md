---
title: svn远程触发jenkins构架
tags:
  - jenkins
  - svn
categories:
  - Linux
copyright: true
date: 2019-08-09 16:00:24
---
# 1 jenkins 配置
在jenkins平台上配置job，开启`远程触发构建`
<!--more-->
![1](1.jpg)
# 2 svn配置仓库触发
在仓库/hook/目录创建post-commit文件，写入脚本

``` bash

#!/bin/sh
# 设置默认字符集，否则post信息到钉钉时中文乱码
export LANG=en_US.UTF-8

# svn中变量1为仓库路径，2为提交版本号
REPOS="$1"
REV="$2"

# 下方svnlook命令获取相应的结果
#mailer.py commit "$REPOS" "$REV" /path/to/mailer.conf
time=$(date +%F/%T)
AUTHOR=$(/usr/bin/svnlook author -r ${REV} ${REPOS})
CHANGEDDIRS=$(/usr/bin/svnlook dirs-changed $REPOS)
MESSAGE=$(/usr/bin/svnlook log -r $REV $REPOS)

# 设置CONTENT的结果
CONTENT=提交时间：${time}\\n提交版本：${REV}\\n作者：${AUTHOR}\\n提交备注：${MESSAGE}\\n修改目录：${CHANGEDDIRS}

# 进入程序目录执行命令，发送提交结果到钉钉群
cd /home/
/usr/bin/java Request 130883d5c8dc420d8deaa5cdabe2c95adf9b780dbd36b7e0597277f13d1ddace $CONTENT

# 上面都是发送svn更新到钉钉通知的设置，与发送触发到jenkins无关，下方配置jenkins触发
# jenkins触发命令
curl -u svnjenkins:svnjenkins http://192.168.0.120/jenkins/job/PU2017001_%E6%B4%9E%E8%A7%81_CI.CD_1.222/build?token=dongjian
```
{%note info%}**命令格式**
`svnjenkins:svnjenkins`   # jenkins用户及密码
`http://192.168.0.120/jenkins/`    # jenkins访问url
`job/PU2017001_%E6%B4%9E%E8%A7%81_CI.CD_1.222/build?token=`  # job地址，看图一绿色框内地址
`dongjian`   # token的值，jenkins设置的token名字
{%endnote%}
# 3 svn远程触发jenkins，增加筛选

``` bash
#! /bin/bash
export LANG=en_US.UTF-8
REPOS="$1"
REV="$2"

#mailer.py commit "$REPOS" "$REV" /path/to/mailer.conf
time=$(date +%F/%T)
AUTHOR=$(/usr/bin/svnlook author -r ${REV} ${REPOS})
CHANGEDDIRS=$(/usr/bin/svnlook dirs-changed $REPOS)
MESSAGE=$(/usr/bin/svnlook log -r $REV $REPOS)
CONTENT=提交时间：${time}\\n提交版本：${REV}\\n作者：${AUTHOR}\\n提交备注：${MESSAGE}\\n修改目录：${CHANGEDDIRS}
cd /home/
/usr/bin/java Request 130883d5c8dc420d8deaa5cdabe2c95adf9b780dbd36b7e0597277f13d1ddace $CONTENT

# 筛选规则
b=$(echo ${MESSAGE} | grep build)
if [[ "$b" != "" ]]
then
  curl -u svnjenkins:svnjenkins http://192.168.0.120/jenkins/job/PU2017001_%E6%B4%9E%E8%A7%81_CI.CD_1.222/build?token=dongjian
  sleep 5
  curl -u svnjenkins:svnjenkins http://192.168.0.120/jenkins/view/%E5%AE%A1%E6%9F%A5js/job/PU2017001_dongjian_js/build?token=dongjian
fi
```
{%note info%}**脚本说明**
根据`${MESSAGE}`的结果，筛选是否包含`build`字符，如果包含，触发远程构建，如果不包含，不做任何操作。
{%endnote%}