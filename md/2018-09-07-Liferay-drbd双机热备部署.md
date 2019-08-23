---
title: Liferay+drbd双机热备部署
tags:
  - liferay
  - drbd
  - 双机
categories:
  - Linux
copyright: true
date: 2018-09-07 15:42:19
---

# 1 主节点配置
<!--more-->
## 1.1 添加硬盘

为主服务器添加一块硬盘50G。

## 1.2 创建分区

``` nginx
fdisk /dev/sdb
```

为新硬盘创建分区`sdb1`,大小`50G`.分区格式`lvm`

## 1.3 创建物理卷

``` nginx
pvcreate /dev/sdb1
```

## 1.4 将物理卷添加入卷组

``` nginx
vgextend vg_cosliferay /dev/sdb1
```

卷组名通过`vgdisplay`查看。`vg_cosliferay`是卷组名。

## 1.5 创建逻辑卷

``` lsl
lvcreate -L 50G -n drbdlv vg_cosliferay
```

创建大小为`50G`，名字为`drbdlv`的逻辑卷。

## 1.6 安装drbd

``` nginx
yum -y install drbd84-utils kmod-drbd84
```

### 1.6.1 配置global_common.conf

编辑全局配置：

``` vim
vi  /etc/drbd.d/global_common.conf
```

确保文件中包含有下内容：

  

``` dts
global {  

    usage-count yes;  
  }  

  common {  
    net {  

      protocol C;  # 使用协议C.表示收到远程主机的写入确认后,则认为写入完成.
    }  

  }
```


 

当然，还可以有其它配置，这是最基本的。

### 1.6.2 配置r0资源：

**创建r0资源**：

> 注：r0可以随便命名。

``` vim
vi  /etc/drbd.d/r0.res  
```

写入文件内容：

``` q
resource r0{ 

        on masterNode{ 

                  device          /dev/drbd1; #逻辑设备的路径 

                  disk            /dev/sda3;  #物理设备 

                  address           192.168.58.128:7788; 

                  meta-disk       internal; 

        } 

        on backupNode{ 

                  device          /dev/drbd1; 

                  disk            /dev/sda3; 

                  address           192.168.58.129:7788; 

                  meta-disk       internal; 

        } 

}
```

  

需要把上面用到的防火墙7788端口打开，这个端口是自定义的，如果嫌麻烦可以直接关掉防火墙。

> 注：masterNode/ backupNode是主机名字，根据实际情况书写。

说明：

``` mipsasm
device  是自定义的物理设备的逻辑路径

disk        是磁盘设备，或者是逻辑分区

address   是机器监听地址和端口

meta-disk   这个还没弄明白，看到的资料都是设为：internal（局域网）
```

### 1.6.3 建立resource

 

``` gradle
modprobe drbd                               //载入 drbd 模块  

lsmod | grep drbd                                            //确认 drbd 模块是否载入  
```
![1](1.png)


``` dsconfig
dd if=/dev/zero of=/dev/sda2 bs=1M count=100    //把一些资料塞到 sda3 內 (否则 create-md 时会报错)  

drbdadm create-md r0                                     //建立 drbd resource  

drbdadm up r0                    //   #启用资源
```

# 2 备节点配置

把以上主节点的操作在备节点上操作一次，操作过程完全一样。

## 2.1 设置Primary Node

将`masterNode`设为主服务器(`primary node`)，在`masterNode`上执行：

``` elixir
[root@backupNode /]# drbdadm primary --force r0  
```

**查看drbd状态：**

``` less
[root@backupNode /]# cat /proc/drbd  

version: 8.4.1 (api:1/proto:86-100)  

 GIT-hash: 91b4c048c1a0e06777b5f65d312b38d47abaea80 build by root@masterNode, 2012-05-27 18:34:27  

       1: cs:Connected ro:Primary/Secondary ds:UpToDate/UpToDate C r-----  

     ns:4 nr:9504584 dw:9504588 dr:1017 al:1 bm:576 lo:0 pe:0 ua:0 ap:0 ep:1 wo:b oos:0 
```

 已经变成了主服务器。

 

 

 

 

## 2.2 创建DRBD文件系统

上面已经完成了`/dev/drbd1`的初始化，现在来把`/dev/drbd1`格式化成`ext4`格式的文件系统,在`masterNode`上执行：

``` elixir
 [root@masterNode /]# mkfs.ext3 /dev/drbd1  
```

# 3 安装配置keepalived

## 3.1 YUM安装keepalived

``` elixir
[root@drbd1 rc3.d]# yum install -y keepalived
```

## 3.2 配置keepalived.conf

``` groovy
[root@drbd1 /]# vi /etc/keepalived/keepalived.conf
```

### 3.2.1 主服务器配置

``` lsl
! Configuration File for keepalived

global_defs {

   notification_email {

     acassen@firewall.loc

     failover@firewall.loc

     sysadmin@firewall.loc

   }

   notification_email_from Alexandre.Cassen@firewall.loc

   smtp_server 192.168.200.1

   smtp_connect_timeout 30

   router_id LVS_DEVEL

}

 

vrrp_instance VI_1 {          //定义vrrp实例

    state MASTER              //主节点 ，备用节点为BACKUP             

    interface enp2s0          //绑定的网卡

    virtual_router_id 51     //ID,默认就行 .同一实例下virtual_router_id必须相同

    priority 100             //优先级，备用节点设置为比100小的值

    advert_int 1             //MASTER与BACKUP负载均衡器之间同步检查的时间间隔，单位是秒

    authentication {

        auth_type PASS       //验证类型和密码 

        auth_pass 1111

    }

    virtual_ipaddress {

        172.20.20.237                  //设置虚拟IP地址，可以多个

    }

}
```


### 3.2.2 备服务器配置

``` lsl
! Configuration File for keepalived

global_defs {

   notification_email {

     acassen@firewall.loc

     failover@firewall.loc

     sysadmin@firewall.loc

   }

   notification_email_from Alexandre.Cassen@firewall.loc

   smtp_server 192.168.200.1

   smtp_connect_timeout 30

   router_id LVS_DEVEL

}

 

vrrp_instance VI_1 {          //定义vrrp实例

    state BACKUP             //备节点 ，主用节点为MASTER             

    interface ens192          //绑定的网卡

    virtual_router_id 51     //ID,默认就行 .同一实例下virtual_router_id必须相同

    priority 50             //优先级，备用节点设置为比100小的值

    advert_int 1             //MASTER与BACKUP负载均衡器之间同步检查的时间间隔，单位是秒

    authentication {

        auth_type PASS       //验证类型和密码 

        auth_pass 1111

    }

    virtual_ipaddress {

        172.20.20.237                  //设置虚拟IP地址，可以多个

    }

}
```


## 3.3 启动服务

``` elixir
[root@drbd1 /]# systemctl start keepalived
```

# 4 问题

`Liferay`配置`drbd`双击热备中，在备机启动程序时，遇到以下问题。问题根本原因是原主机是32位系统安装32位程序，在备机64位系统运行32位程序没有运行库而报错。

## 4.1 问题1：

``` awk
[09:55:50][root@liferay-backup opt]#   /opt/liferay-6.2-7/ctlscript.sh start

[09:55:50]/opt/liferay-6.2-7/mysql/bin/my_print_defaults:   /opt/liferay-6.2-7/mysql/bin/my_print_defaults.bin:   /lib/ld-linux.so.2: bad ELF interpreter: 没有那个文件或目录

[09:55:50]/opt/liferay-6.2-7/mysql/bin/my_print_defaults:行12: /opt/liferay-6.2-7/mysql/bin/my_print_defaults.bin: 成功

[09:55:50]/opt/liferay-6.2-7/mysql/bin/my_print_defaults:   /opt/liferay-6.2-7/mysql/bin/my_print_defaults.bin: /lib/ld-linux.so.2: bad   ELF interpreter: 没有那个文件或目录

[09:55:50]/opt/liferay-6.2-7/mysql/bin/my_print_defaults:行12: /opt/liferay-6.2-7/mysql/bin/my_print_defaults.bin: 成功

[09:55:50]161221 09:55:53 mysqld_safe   Logging to '/opt/liferay-6.2-7/mysql/data/mysqld.log'.

[09:55:50]161221 09:55:53 mysqld_safe   Starting mysqld daemon with databases from /opt/liferay-6.2-7/mysql/data

[09:55:50]161221 09:55:53 mysqld_safe   mysqld from pid file /opt/liferay-6.2-7/mysql/data/mysqld.pid ended
```

**解决办法：**

``` elixir
[root@liferay-backup opt]#  yum install   glibc.i686
```

安装后**又报错**：

``` awk
[root@liferay-backup data]#   /opt/liferay-6.2-7/ctlscript.sh start

[10:30:47]libgcc_s.so.1 must be installed   for pthread_cancel to work

[10:30:47]libgcc_s.so.1 must be installed   for pthread_cancel to work

[10:30:47]161221 10:30:50 mysqld_safe   Logging to '/opt/liferay-6.2-7/mysql/data/mysqld.log'.

[10:30:47]161221 10:30:50 mysqld_safe   Starting mysqld daemon with databases from /opt/liferay-6.2-7/mysql/data

[10:30:48]libgcc_s.so.1   must be installed for pthread_cancel to work

[10:30:48]/opt/liferay-6.2-7/mysql/bin/mysqld_safe:   行 165: 19283 已放弃               (吐核)LD_LIBRARY_PATH=/opt/liferay-6.2-7/mysql/lib\:/opt/liferay-6.2-7/mysql/lib\:/opt/liferay-6.2-7/sqlite/lib\:/opt/liferay-6.2-7/apache2/lib\:/opt/liferay-6.2-7/common/lib\:   nohup /opt/liferay-6.2-7/mysql/bin/mysqld   --defaults-file=/opt/liferay-6.2-7/mysql/my.cnf   --basedir=/opt/liferay-6.2-7/mysql --datadir=/opt/liferay-6.2-7/mysql/data   --plugin-dir=/opt/liferay-6.2-7/mysql/lib/plugin --user=mysql   --lower-case-table-names=1   --log-error=/opt/liferay-6.2-7/mysql/data/mysqld.log   --pid-file=/opt/liferay-6.2-7/mysql/data/mysqld.pid   --socket=/opt/liferay-6.2-7/mysql/tmp/mysql.sock --port=3306 < /dev/null   >> /opt/liferay-6.2-7/mysql/data/mysqld.log 2>&1

[10:30:48]161221 10:30:51 mysqld_safe   mysqld from pid file /opt/liferay-6.2-7/mysql/data/mysqld.pid ended
```

> 没有安装32位运行库

直接安装`yum install glibc.i686`无法成功，系统已安装64位运行库，无法在安装。需要

``` sql
Linux的有些软件需要32位运行库才能运行，如Dr.com客户端等



yum在线安装： sudo yum install   xulrunner.i686

或者： sudo yum install   ia32-libs.i686

ubuntu下： sudo apt-get install ia32-libs
```

最终没有采用此方法，使用的方法为本博客内的
**[Rsync+sersync实时双向同步](https://kxinter.github.io/kxinter.gitub.io/2018/09/04/rsync-sersync%E5%AE%9E%E6%97%B6%E5%8F%8C%E5%90%91%E5%90%8C%E6%AD%A5/)**

 

参考资料1：http://blog.csdn.net/tmy257/article/details/41013985

参考资料2：http://blog.csdn.net/attagain/article/details/17026433


