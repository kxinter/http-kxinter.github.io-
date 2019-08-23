---
title: Liferay+keepalive+sersync+rsync主从同步
tags:
  - liferay
  - keepalived
  - rsync
  - 同步
categories:
  - Linux
copyright: true
date: 2018-09-11 09:32:28
---

# 1 环境
<!--more-->
| 服务器                  | 系统    | 软件                      | JAVA     | MYSQL  | IP           |
| ----------------------- | ------- | ------------------------- | -------- | ------ | ------------ |
| Liferay-a               | Centos7 | Liferay+keepalive+sersync | 1.7.0_80 | 5.5.42 | 172.20.20.59 |
| Liferay-b               | Centos7 | Liferay+keepalive+rsync   | 1.7.0_80 | 5.5.42 | 172.20.20.60 |
| 虚拟IP:    172.20.20.58 | 

# 2 安装liferay

安装liferay官方版本`6.2-ce4`,方法自行度娘。恢复数据参考《liferay备份还原文档》

# 3 安装keepalive

``` ebnf
Yum install keepalive
```
## 3.1 编辑配置文件

``` ebnf
Yum install keepalive
```
**Liferay-a:**

![1](1.png)

**Liferay-b:**

![2](2.png)

启动keepalive，建立虚拟IP，主服务器当机，从服务器获得Ip.

# 4 mysql主从同步

下载`mysql-5.5.42-linux2.6-x86_64.tar.gz`

解压到`/usr/local`,重命名为`mysql`

## 4.1 编辑配置文件

``` nginx
Vi /etc/my.cnf
```


**Liferay-a:**
![3](3.png)


**Liferay-b**
![4](4.png)


## 4.2 建立mysql主从同步

1.    查看`liferay-a`(主服务器)，查看`mysql`（主）信息，并建立同步帐号：

``` sql
mysql> GRANT ALL PRIVILEGES ON bitnami_liferay.* TO 'tongbu'@'%' IDENTIFIED BY 'De123456' WITH GRANT OPTION;
```
![5](5.png)



2.    进入`liferay-b`（从服务器），在`mysql`中输入命令，建立连接

``` sql
mysql> CHANGE MASTER TO MASTER_HOST='172.20.20.59',  MASTER_USER='tongbu', MASTER_PASSWORD='De123456', MASTER_LOG_FILE='mysql-bin.000022',MASTER_LOG_POS=151424110;
```


输入命令，查看备服务器信息

``` sql
mysql> SHOW SLAVE STATUS\G
```
![6](6.png)



## 	

通过`mysql`命令恢复`bitnami_liferay`数据库备份到`lifreay-a`(主服务器)，自动实时同步数据到从服务器。

# 5 目录同步

## 5.1 安装rsync(liferay-b)

只需在`liferay-b`服务器上安装`rsync`。

`Liferay-b`作为`rsync`服务器，`lifray-a`作为客户端，实时同步目录数据到`liferay-b`

``` ebnf
Yum install rsync
```

### 5.1.1 编辑配置文件

``` vim
vi /etc/rsyncd.conf
```


**liferay-b:**

![7](7.png)

### 5.1.2 新建rsyncd.pass1密码文件在/etc/目录

**文件格式**  `帐号:密码`

**设置文件权限为600（必须）**
![8](8.png)


## 5.2 安装sersync（liferay-a）

`Liferay-a`安装实时同步工具`sersync2.5.4_64bit_binary_stable_final.tar.gz`

下载`sersync2.5.4_64bit_binary_stable_final.tar.gz`

解压到`/usr/local`

### 5.2.1 编辑confxml.xml

``` css
vi confxml.xml
```
![9](9.png)



### 5.2.2 在/etc/目录创建密码文件rsyncd.pass1

文件格式只填写密码（注意和同步服务器的密码文件内的密码一样）
![10](10.png)


### 5.2.3 启动sersync，开启实时同步

``` groovy
/usr/local/sersync/sersync2 -d -r -o /usr/local/sersync/confxml.xml
```


