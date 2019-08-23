---
title: postgresql部署
tags:
  - postgresql
  - 部署
categories:
  - Linux
copyright: true
date: 2019-03-01 16:12:25
---

# 1 Postgres部署手册

## 1.1 安装
<!--more-->
### 1.1.1安装软件库

``` bash
yum install https://download.postgresql.org/pub/repos/yum/10/redhat/rhel-7-x86_64/pgdg-centos10-10-2.noarch.rpm
yum install epel-release               #安装postgis时提示部分依赖无法安装
```

### 1.1.2 安装软件

``` bash
yum install postgresql10 && yum install postgresql10-server
```

### 1.1.3 初始化及开机启动

``` bash
/usr/pgsql-10/bin/postgresql-10-setup initdb
systemctl enable postgresql-10
systemctl start postgresql-10
```

### 1.1.4 设置postgres密码

``` bash
Sudo –u postgres psql
postgres=# ALTER USER postgres WITH PASSWORD 'zhjx123'
```

### 1.1.5 开启远程访问

``` bash
vim /var/lib/pgsql/10/data/postgresql.conf 
# 修改#listen_addresses = 'localhost' 为 listen_addresses='*' 当然，此处‘*’也可以改为任何你想开放的服务器IP


vim /var/lib/pgsql/10/data/pg_hba.conf
   修改如下内容，信任指定服务器连接
# IPv4 local connections:
host    all            all      192.168.0.0/23（需要连接的服务器IP）  md5
```

## 1.2 安装postgis插件（补充）

``` bash
yum install postgis25_10 
```

# 2	greenplum部署手册

## 2.1修改Linux内核参数

``` bash
# vi /etc/sysctl.conf

net.ipv4.ip_forward = 0
net.ipv4.conf.default.accept_source_route = 0
kernel.sysrq = 1
kernel.core_uses_pid = 1
net.ipv4.tcp_syncookies = 1
kernel.msgmnb = 65536
kernel.msgmax = 65536
kernel.sem = 250 64000 100 512
kernel.shmmax = 500000000
kernel.shmmni = 4096
kernel.shmall = 4000000000
net.ipv4.tcp_tw_recycle = 1
net.ipv4.tcp_max_syn_backlog = 4096
net.core.netdev_max_backlog = 10000
vm.overcommit_memory = 2
net.ipv4.conf.all.arp_filter = 1
```

## 2.2 修改Linux最大限制

``` bash
# vi /etc/security/limits.conf

#greenplum configs
* soft nofile 65536
* hard nofile 65536
* soft nproc 131072 
* hard nproc 131072
```

## 2.3 关闭selinux

``` bash
# vim /etc/selinux/conf
修改如下：
SELINUX=disabled

# setenforce 0   # 临时关闭，重启恢复。    
```

## 2.4 greenplum安装

### 2.4.1 创建数据库用户

``` shell
# groupadd -g 530 gpadmin
# useradd -g 530 -u530 -m -d /home/gpadmin -s /bin/bash gpadmin
# passwd gpadmin
```

### 2.4.2 修改hosts

设置集群解析

``` shell
# vim /etc/hosts
192.168.0.174 mdw sdw
```

### 2.4.3 下载安装包

官网https://network.pivotal.io/products/pivotal-gpdb#/releases/1683
 ![1](1.png)
 ![2](2.png)

### 2.4.3 赋权及安装

``` shell
# unzip greenplum-db-5.9.0-rhel7-x86_64.zip
# chmod +x greenplum-db-5.9.0-rhel7-x86_64.bin
# ./ greenplum-db-5.9.0-rhel7-x86_64.bin
一路yes,安装完成
```

默认目录/usr/loca/greenplum-db

### 2.4.4 设置gpadmin用户环境

``` shell
# cd /home/gpadmin
# vi .bashrc

# vi .bash_profile

.bashrc和.bash_profile最后都添加下面两行
source /usr/local/greenplum-db/greenplum_path.sh
export MASTER_DATA_DIRECTORY=/home/gpadmin/gpdata/gpmaster/gpseg-1
export PGPORT=5433   # 应为本机有postsql，端口占用，所以使用5433端口
#export PGDATABASE=testDB
```

### 2.4.4 准备节点服务器信息文件

后面的批量安装会用到这两个文件，如果all_host和all_segment内容一样，可以只创建一个文件

``` shell
[root@mdw ~]# cd /home/gp
[root@mdw~ ]# touch all_host
[root@mdw ~]# touch all_segment
all_host和all_segment内容：
mdw
sdw
```

### 2.4.5 建立节点服务器间的信任

``` bash
gpssh-exkeys -f /opt/gpinit/all_host
```

### 2.4.6 批量安装

``` stylus
gpseginstall -f /home/gpadmin/all_host -u gpadmin -p gpadmin
```

### 2.4.7 检查批量安装情况

``` bash
gpssh -f /usr/local/greenplum-db/all_host -e ls -l $GPHOME #检查安装情况
```

### 2.4.8 创建存储目录

``` shell
[gpadmin@mdw conf]$ gpssh -f /home/gpadmin/all_host
=> mkdir gpdata
[sdw3]
[ mdw]
[sdw2]
[sdw1]
=> cd gpdata
[sdw3]
[ mdw]
[sdw2]
[sdw1]
=> mkdir gpmaster gpdatap1 gpdatap2 gpdatam1 gpdatam2
[sdw3]
[ mdw]
[sdw2]
[sdw1]
=> ll
[sdw3] 总用量 20
[sdw3] drwxrwxr-x 2 gpadmin gpadmin 4096 7月  18 19:46 gpdatam1
[sdw3] drwxrwxr-x 2 gpadmin gpadmin 4096 7月  18 19:46 gpdatam2
[sdw3] drwxrwxr-x 2 gpadmin gpadmin 4096 7月  18 19:46 gpdatap1
[sdw3] drwxrwxr-x 2 gpadmin gpadmin 4096 7月  18 19:46 gpdatap2
[sdw3] drwxrwxr-x 2 gpadmin gpadmin 4096 7月  18 19:46 gpmaster
[ mdw] 总用量 20
[ mdw] drwxrwxr-x 2 gpadmin gpadmin 4096 7月  18 19:46 gpdatam1
[ mdw] drwxrwxr-x 2 gpadmin gpadmin 4096 7月  18 19:46 gpdatam2
[ mdw] drwxrwxr-x 2 gpadmin gpadmin 4096 7月  18 19:46 gpdatap1
[ mdw] drwxrwxr-x 2 gpadmin gpadmin 4096 7月  18 19:46 gpdatap2
[ mdw] drwxrwxr-x 2 gpadmin gpadmin 4096 7月  18 19:46 gpmaster
[sdw2] 总用量 20
[sdw2] drwxrwxr-x 2 gpadmin gpadmin 4096 7月  18 19:46 gpdatam1
[sdw2] drwxrwxr-x 2 gpadmin gpadmin 4096 7月  18 19:46 gpdatam2
[sdw2] drwxrwxr-x 2 gpadmin gpadmin 4096 7月  18 19:46 gpdatap1
[sdw2] drwxrwxr-x 2 gpadmin gpadmin 4096 7月  18 19:46 gpdatap2
[sdw2] drwxrwxr-x 2 gpadmin gpadmin 4096 7月  18 19:46 gpmaster
[sdw1] 总用量 20
[sdw1] drwxrwxr-x 2 gpadmin gpadmin 4096 7月  18 19:46 gpdatam1
[sdw1] drwxrwxr-x 2 gpadmin gpadmin 4096 7月  18 19:46 gpdatam2
[sdw1] drwxrwxr-x 2 gpadmin gpadmin 4096 7月  18 19:46 gpdatap1
[sdw1] drwxrwxr-x 2 gpadmin gpadmin 4096 7月  18 19:46 gpdatap2
[sdw1] drwxrwxr-x 2 gpadmin gpadmin 4096 7月  18 19:46 gpmaster
=> exit
```

### 2.4.9 配置.bash_profile环境变量

``` shell
[gpadmin@mdw ~]$ vim /home/gpadmin/.bash_profile

source /opt/greenplum/greenplum-db/greenplum_path.sh
export MASTER_DATA_DIRECTORY=/home/gpadmin/gpdata/gpmaster/gpseg-1
export PGPORT=5433
# export PGDATABASE=testDB
[gpadmin@mdw ~]$ source .bash_profile(让环境变量生效)
```

### 2.4.10 创建初始化配置文件

``` makefile
[gpadmin@mdw ~]$ vim /home/gpadmin/gpinitsystem_config
ARRAY_NAME="Greenplum"
SEG_PREFIX=gpseg
PORT_BASE=33000
declare -a DATA_DIRECTORY=(/home/gpadmin/gpdata/gpdatap1  /home/gpadmin/gpdata/gpdatap2)
MASTER_HOSTNAME=mdw
MASTER_DIRECTORY=/home/gpadmin/gpdata/gpmaster
MASTER_PORT=5433
TRUSTED_SHELL=/usr/bin/ssh
MIRROR_PORT_BASE=43000
REPLICATION_PORT_BASE=34000
MIRROR_REPLICATION_PORT_BASE=44000
declare -a MIRROR_DATA_DIRECTORY=(/home/gpadmin/gpdata/gpdatam1 /home/gpadmin/gpdata/gpdatam2)
MACHINE_LIST_FILE=/home/gpadmin/seg_hosts
```

### 2.4.11 初始化数据库

``` elixir
[gpadmin@mdw ~]$ gpinitsystem -c /home/gpadmin/gpinitsystem_config -s mdw
```

### 2.4.12 启动/关闭/状态

``` groovy
Gpadmin用户执行命令gpstart/gpstop/gpstate
```

# 3	安装postgis插件

``` css
gppkg -i postgis-2.1.5+pivotal.1-gp5-rhel7-x86_64.gppkg
```

