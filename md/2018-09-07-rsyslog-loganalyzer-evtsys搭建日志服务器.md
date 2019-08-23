---
title: rsyslog+loganalyzer+evtsys搭建日志服务器
tags:
  - rsyslog
categories:
  - Linux
copyright: true
date: 2018-09-07 15:01:32
---

# 1 环境要求
<!--more-->
将所有的服务器的日志都集中保存在一台rsyslog日志服务器中，mysql作为数据库，loganalyzer将服务器的日志数据进行分析展现，evtsys是windows服务器提交日志的客户端软件。

实验环境如下：

| 节点           | OS             | IP              | 网络   |
| -------------- | -------------- | --------------- | ------ |
| rsyslog Server | Centos6.4      | 192.168.200.106 | 单网卡 |
| Linux Client   | Centos6.4      | 192.168.200.106 | 单网卡 |
| Windows Client | Windows2008x64 | 192.168.200.31  | 单网卡 |

<!--more-->

 

# 2 rsyslog+loganalyzer日志服务器的部署

 

## 2.1 配置rsyslog日志服务器

因为`rsyslog`要把日志存到`mysql`中，所以要有`mysql`服务器，还要有`rsyslog`配置文件加载。

 

### 2.1.1 连接mysql的模块

``` elixir
[iyunv@rsyslog ~]# yum -y install rsyslog mysql-server   rsyslog-mysql
```

 

### 2.1.2 配置数据库

``` sql
[iyunv@rsyslog ~]#   rpm -ql rsyslog-mysql            #首先查看rsyslog-mysql安装生成了那些文件
/lib64/rsyslog/ommysql.so
/usr/share/doc/rsyslog-mysql-5.8.10
/usr/share/doc/rsyslog-mysql-5.8.10/createDB.sql   #此sql文件就是需要导入到数据库中的数据文件
#
[iyunv@rsyslog ~]# service mysqld start               #启动mysqld服务
[iyunv@rsyslog ~]# mysql                              #连接mysql
Welcome to the MySQL monitor.  Commands end with ; or g.
Your MySQL connection id is 2
Server version: 5.1.73 Source distribution
Copyright (c) 2000, 2013, Oracle and/or its affiliates. All rights reserved.

Oracle is a registered trademark of Oracle Corporation and/or its
affiliates. Other names may be trademarks of their respective
owners.

Type 'help;' or 'h' for help. Type 'c' to clear the current input statement.

mysql>
mysql>
mysql> show databases;
+--------------------+
| Database           |
+--------------------+
| information_schema |
| mysql              |
| test               |
+--------------------+
3 rows in set (0.00 sec)  #此时，只有3个库
#
mysql> source /usr/share/doc/rsyslog-mysql-5.8.10/createDB.sql;     #导入rsyslog的数据文件
mysql> show databases;
+--------------------+
| Database           |
+--------------------+
| information_schema |
| Syslog             |
| mysql              |
| test               |
+--------------------+
4 rows in set (0.01 sec)
mysql> use Syslog;                #Syslog即是记录日志文件的数据库
Reading table information for completion of table and column names
You can turn off this feature to get a quicker startup with -A
Database changed
mysql> show tables;
+------------------------+
| Tables_in_Syslog       |
+------------------------+
| SystemEvents           |
| SystemEventsProperties |
+------------------------+
2 rows in set (0.00 sec)
#
#接下来，即是为rsyslog服务器授权。此处一定是rsyslog服务器的IP
#如果写成各服务器的IP，那就错了
mysql> grant all on Syslog.* to 'syslogroot'@'127.0.0.1' identified by   'syslogpass';
Query OK, 0 rows affected (0.00 sec)
mysql> grant all on Syslog.* to 'syslogroot'@'192.168.200.106' identified   by 'syslogpass';
Query OK, 0 rows affected (0.04 sec)
mysql> flush privileges;
Query OK, 0 rows affected (0.00 sec)
mysql> q
Bye
```



### 2.1.3 修改rsyslog日志服务器配置文件

``` gams
[iyunv@rsyslog ~]#   grep -v "^$" /etc/rsyslog.conf | grep -v "^#"
$ModLoad imuxsock
$ModLoad imklog
$ModLoad imudp            #加载udp的模块
$UDPServerRun 514         #允许接收udp 514的端口传来的日志
$ModLoad imtcp            #加载tcp的模块
$InputTCPServerRun 514    #允许接收tcp 514的端口传来的日志
$ModLoad ommysql          #加载mysql的模块
$ActionFileDefaultTemplateRSYSLOG_TraditionalFileFormat
$IncludeConfig /etc/rsyslog.d/*.conf
*.*         :ommysql:192.168.200.106,Syslog,syslogroot,syslogpass        #添加此行，所有设施的所有日志都记录到此数据库服务器的Syslog数据库中，以syslogroot用户，syslogpass密码访问数据库
local7.*                            /var/log/boot.log
$template SpiceTmpl,"%TIMESTAMP%.%TIMESTAMP:::date-subseconds%   %syslogtag%   %syslogseverity-text%:%msg:::sp-if-no-1st-sp%%msg:::drop-last-lf%"
:programname, startswith, "spice-vdagent"     /var/log/spice-vdagent.log;SpiceTmpl
```

 

### 2.1.4 修改完成后，重启rsyslog服务

``` perl
[iyunv@rsyslog ~]#   service rsyslog restart
Shutting down system logger:                                   [  OK  ]
Starting system logger:                                        [  OK  ]
```

## 2.2 配置rsyslog客户端

### 2.2.1 修改配置文件

``` gams
[iyunv@mariadb ~]#   grep -v "^$" /etc/rsyslog.conf | grep -v "^#"
$ModLoad imuxsock # provides support for local system logging (e.g. via   logger command)
$ModLoad imklog   # provides kernel logging support (previously   done by rklogd)
$ActionFileDefaultTemplate RSYSLOG_TraditionalFileFormat
$IncludeConfig /etc/rsyslog.d/*.conf
*.*       @192.168.200.106
*.*         :ommysql:192.168.200.106,Syslog,syslogroot,syslogpass
$template SpiceTmpl,"%TIMESTAMP%.%TIMESTAMP:::date-subseconds%   %syslogtag%   %syslogseverity-text%:%msg:::sp-if-no-1st-sp%%msg:::drop-last-lf%"
:programname, startswith, "spice-vdagent"     /var/log/spice-vdagent.log;SpiceTmpl
```

 

### 2.2.2 修改完成后，重启rsyslog服务

``` perl
[iyunv@rsyslog ~]#   service rsyslog restart
Shutting down system logger:                                   [  OK  ]
Starting system logger:                                            [  OK  ]
 
```

## 2.3 验证客户端日志文件的存放


### 2.3.1 使用logger生成一条日志信息

``` elixir
[iyunv@mariadb ~]#   logger -p info "I'm mariadb"
```


### 2.3.2 在rsyslog服务器上验证

``` yaml
[iyunv@rsyslog   ~]# mysql
mysql> use Syslog;
mysql> select * from SystemEventsG
*************************** 279. row ***************************
ID: 279
CustomerID: NULL
ReceivedAt: 2014-08-13 20:07:39
DeviceReportedTime: 2014-08-13 20:07:40
Facility: 1
Priority: 6
FromHost: mariadb
Message:  I'm   mariadb        #我在做的时候，就是因为第二部的1的（2）中mysql授权时，写的是客户端IP，导致这里获取不到数据。
NTSeverity: NULL                  #因此，在数据库授权的时候，要授权的是rsyslog日志服务器的IP
Importance: NULL
EventSource: NULL
EventUser: NULL
EventCategory: NULL
EventID: NULL
EventBinaryData: NULL
MaxAvailable: NULL
CurrUsage: NULL
MinUsage: NULL
MaxUsage: NULL
InfoUnitID: 1
SysLogTag: root:
EventLogType: NULL
GenericFileName: NULL
SystemID: NULL
processid:
checksum: 0
279 rows in set (0.00 sec)
```


到这里，`rsyslog`日志服务器就部署完成了，但此时日志处于`rsyslog`日志服务器的`mysql`数据库中，并不方便查看与管理，所以我们再部署一个`loganalyzer`日志分析器，来减小日志管理的复杂度。

 

## 2.4 部署loganalyzer日志分析器

### 2.4.1 安装LAMP环境

``` golo
[iyunv@rsyslog ~]#   yum -y install httpd php php-mysql php-gd
[iyunv@rsyslog ~]# mkdir /var/www/html/loganalyzer/
mkdir: created directory `/var/www/html/loganalyzer/'
```

 

### 2.4.2 解压loganalyzer源码包

``` elixir
[iyunv@rsyslog   ~]# tar xf loganalyzer-3.6.5.tar.gz
[iyunv@rsyslog ~]# cd loganalyzer-3.6.5
[iyunv@rsyslog loganalyzer-3.6.5]#
[iyunv@rsyslog loganalyzer-3.6.5]# ls
ChangeLog  contrib  COPYING  doc  INSTALL  src
[iyunv@rsyslog loganalyzer-3.6.5]# mv src/* /var/www/html/loganalyzer/            #src下是php的网页文件
[iyunv@rsyslog loganalyzer-3.6.5]# ls contrib/
configure.sh  secure.sh
[iyunv@rsyslog loganalyzer-3.6.5]# mv contrib/*   /var/www/html/loganalyzer/      #contrib目录下的两个脚本，可以打开看看
#
[iyunv@rsyslog loganalyzer-3.6.5]# cd /var/www/html/loganalyzer/
[iyunv@rsyslog loganalyzer]# sh configure.sh                                        #执行脚本
```

 

### 2.4.3 配置httpd

修改DocumentRoot网页根目录

``` elixir
[iyunv@rsyslog ~]#   vim /etc/httpd/conf/httpd.conf
DocumentRoot "/var/www/html/loganalyzer"
#
[iyunv@rsyslog ~]# service httpd start
```

 

### 2.4.4 配置httpd和mysql开机启动

``` elixir
[iyunv@rsyslog ~]#   chkconfig mysqld on

[iyunv@rsyslog ~]# chkconfig httpd on
```

 

### 2.4.5 创建loganalyzer数据库，并授权

``` css
[iyunv@rsyslog   ~]# mysql
Enter password:
mysql> create database loganalyzer;
Query OK, 1 row affected (0.04 sec)
mysql> grant all on loganalyzer.* to dianyi@'192.168.200.106' identified   by 'dianyi123';
Query OK, 0 rows affected (0.00 sec)
mysql> flush privileges;
Query OK, 0 rows affected (0.00 sec)
```

### 2.4.6 安装loganalyzer

#### 2.4.6.1 安装界面

![Step 1](1.png)

![Step 2](2.png)


![Step 3](3.png)

![Step 4](4.png)

![Step 5](5.png)

![Step 6](6.png)

![Step 7](7.png)

![Step 8](8.png)

![enter description here](9.png)
安装完成，enjoy it
![enter description here](10.png)

## 2.5 Windows客户端的安装配置

 

### 2.5.1 安装Syslog日志客户端

``` css
下载Evtsys软件，分32位和64位安装方法一样。解压后将evtsys.dll、evtsys.exe复制到c:\windows\system32\下。

 

cd   c:\windows\system32

evtsys.exe -i -h   192.168.200.31 -p 514

net start evtsys
```


### 2.2.2 开启系统相关审计

打开`windows组策略编辑器` (开始->运行 输入 `gpedit.msc`) 在**windows 设置－> 安全设置 －> 本地策略－>审核策略**中，打开你需要记录的`windows日志`。`evtsys`会实时的判断是否有新的windows日志产生，然后把新产生的日志转换成`syslogd`可识别的格式,通过`UDP `端口发送给`syslogd`服务器。

 ![enter description here](11.png)



# 3 Mysql数据库的优化的一些想法


随着mysql数据库中的记录越来越多，查询的速度会越来越慢。我们可以定期到数据表中删除较早以前的记录来减少数据量从而起到优化的作用。可以定期执行如下SQL语句：

``` sql
delete from SystemEvents(数据表名) where ReceivedAt(日期字段名)<curdate() - interval 3 month;
```

//表示删除” `SystemEvents`”数据表” `ReceivedAt`”日期字段大于3个月的记录

也可以考虑使用其他数据库，比如具有循环功能的`sqllite`数据库，不过这样的话就要进行二次开发了。





