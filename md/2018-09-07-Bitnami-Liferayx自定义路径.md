---
title: Bitnami_Liferay自定义路径
tags:
  - liferay
  - bitnami
categories:
  - Linux
copyright: true
date: 2018-09-07 14:17:46
---

# 1 修改文件存储路径
<!--more-->
#配置文件`portal-ext.properties`     修改文件存储路径

``` gradle
[root@htest2 classes]# vi   /opt/liferay-6.2-7/apache-tomcat/webapps/liferay/WEB-INF/classes/portal-ext.properties
```

移动存储目录`/opt/liferay-6.2-7/apps/liferay/data/document_library`到`/drbd`,修改`portal-ext.properties`内`dl.store.file.system.root.dir=`参数（没有这项手动添加参数）

``` stylus
dl.store.file.system.root.dir=/drbd/document_library
```

# 2 修改数据库路径

移动`/opt/liferay-6.2-7/mysql/data/`到`/home/mysql/data`

## 2.1 修改my.cnf参数

``` vim
[root@htest2 home]# vi   /opt/liferay-6.2-7/mysql/my.cnf
```

 修改my.cnf数据库路径参数

``` haskell
datadir=/opt/liferay-6.2-7/mysql/data

改为

datadir=/home/mysql/data
```



## 2.2 修改ctl.sh路径参数

``` vim
[root@htest2 drbd]# vi   /opt/liferay-6.2-7/mysql/scripts/ctl.sh
```



``` vim
MYSQL_PIDFILE=/   opt/liferay-6.2-7/mysql/data/mysqld.pid

MYSQL_START="/opt/liferay-6.2-7/mysql/bin/mysqld_safe   --defaults-file=/opt/lifer

ay-6.2-7/mysql/my.cnf --port=3306   --socket=/opt/liferay-6.2-7/mysql/tmp/mysql.so

ck    --datadir=/opt/liferay-6.2-7/mysql/data   --log-error=/opt/liferay-6.2-7/mysql

/data/mysqld.log  --pid-file=$MYSQL_PIDFILE   --lower-case-table-names=1 "

改为

MYSQL_PIDFILE=/home/mysql/data/mysqld.pid

MYSQL_START="/opt/liferay-6.2-7/mysql/bin/mysqld_safe   --defaults-file=/opt/lifer

ay-6.2-7/mysql/my.cnf --port=3306   --socket=/opt/liferay-6.2-7/mysql/tmp/mysql.so

ck    --datadir=/home/mysql/data --log-error=/home/mysql/data/mysqld.log  --pid-fi

le=$MYSQL_PIDFILE   --lower-case-table-names=1 "
```

# 3 修改插件目录路径(暂不修改)

## 3.1 修改catalina.bat参数

移动/opt/liferay-6.2-7/apache-tomcat/temp到/drbd,修改catalina.bat参数

``` groovy
[htest2@htest2 bin]$ vi /opt/liferay-6.2-7/apache-tomcat/bin/   catalina.bat
```



``` vbscript
if not "%CATALINA_TMPDIR%" ==   "" goto gotTmpdir

set "CATALINA_TMPDIR=%CATALINA_BASE%\temp"

:gotTmpdir

改为

if not "%CATALINA_TMPDIR%" ==   "" goto gotTmpdir

set "CATALINA_TMPDIR=\drbd\temp"

:gotTmpdir
```

## 3.2 修改ctl.sh

``` groovy
[htest1@htest1 ~]$ vi   /opt/liferay-6.2-7/apache-tomcat/scripts/ctl.sh
```

修改CATALINA_PID路径

``` makefile
CATALINA_PID=/opt/liferay-6.2-7/apache-tomcat/temp/catalina.pid

改为

CATALINA_PID=/drbd/temp/catalina.pid
```



