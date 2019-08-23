---
title: centos同步yum源到本地
tags:
  - 私有仓库
  - yum
categories:
  - Linux
copyright: true
date: 2018-08-16 18:12:05
---

# 一、环境
<!--more-->
os:centos 7.3 1611

应用：yum-utils

互联网源：阿里云

# 二、步骤

删除/etc/yum.repos.d下所有源文件

## 1、下载源repo到本地

``` bash
$ wget -O /etc/yum.repos.d/aliyun.repo https://mirrors.aliyun.com/repo/Centos-7.repo
```
## 2、安装yum-utils提供reporsync服务

``` stata
$ yum install yum-utils -y
```

## 3、查看yum源仓库标识

``` bash
[root@localhost yum.repos.d]# yum repolist
已加载插件：fastestmirror
Loading mirror speeds from cached hostfile
 * base: mirrors.aliyun.com
 * extras: mirrors.aliyun.com
 * updates: mirrors.aliyun.com
源标识 源名称 状态
base/7/x86_64 CentOS-7 - Base - mirrors.aliyun.com 9,591
extras/7/x86_64 CentOS-7 - Extras - mirrors.aliyun.com 196
updates/7/x86_64 CentOS-7 - Updates - mirrors.aliyun.com 657
repolist: 10,444
```

## 4、根据源标识同步源到本地目录

``` bash
[root@localhost ~]# reposync -r base -p /var/www/html/     #这里同步base目录到本地
```

> 注意： 部分互联网yum源不支持同步

参考资料
http://www.cnblogs.com/chengd/articles/6912938.html

https://www.2cto.com/net/201512/455901.html