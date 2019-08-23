---
title: zabbix监控VMware
tags:
  - zabbix
  - vmware
categories:
  - 自动化运维
date: 2018-08-30 11:54:59
---

# 1 环境
<!--more-->
Centos 7.2

Zabbix 3.0

VMware 5.5/6.0

# 2 步骤

## 2.1 修改配置文件

1. 修改zabbix server配置文件

``` vim
vim /etc/zabbix/zabbix_server.conf
```

添加如下内容

``` makefile
StartVMwareCollectors=5

VMwareFrequency=60

VMwareCacheSize=8M
```

> StartVMwareCollectors=5  #预启动的VMware数据采集线程数量，值范围：0~250
> 
> VMwareFrequency=60     #VMware的数据检测缓存大小，值范围：256K~2G
> 
> VMwareCacheSize=8M     #数据采集的频率，值范围：10~86400

2. 重启zabbix—server服务

``` vbscript
service zabbix-server restart
```

## 2.2 添加VM主机监控

1. 添加主机
网上很多教程都说端口改为80,但我改成80后无法获取到数据，但使用10050端口可以获取到（默认VMware无需安装agent）



2. 添加模版


3. 添加宏

``` bash
{$PASSWORD}                  #连接VMware的用户密码

{$URL}


#固定格式：`https://IP/sdk `    网页访问地址错误，`curl -I -k https://192.168.0.19/sdk `测试 没问题

{$USERNAME}                #连接VMware的用户，默认root或administrator
```


过一会就可以看到自动检测到的虚拟主机了，自动匹配监控项，`**图形需要自行创建**`。