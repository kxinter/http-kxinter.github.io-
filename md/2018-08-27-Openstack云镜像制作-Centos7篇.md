---
title: Openstack云镜像制作-Centos7篇
tags:
  - openstack
categories:
  - Openstack
copyright: true
date: 2018-08-27 11:31:29
---

# 一、制作步骤
<!--more-->
## 1、安装kvm

参考centos 7系统安装配置kvm软件步骤

**1、创建虚拟硬盘大小10G     名称：centos7-dis.qcow2**

**2、安装系统**

> 注意一：分区，分区的时候只给"/" 根目录分一个区即可，其他都不要。格式ext4
> 注意二：网络设置方面，确保你的网卡eth0是DHCP状态的，而且请务必勾上"auto connect"的对勾

## 2、进入虚拟机系统操作

关于CentOS镜像制作需要注意以下几点：

**(1) 修改网络信息 /etc/sysconfig/network-scripts/ifcfg-eth0 （删掉mac信息)，如下：**

``` ini
TYPE=Ethernet  
DEVICE=eth0  
ONBOOT=yes  
BOOTPROTO=dhcp  
NM_CONTROLLED=no 
```
**(2) 删除已生成的网络设备规则，否则制作的镜像不能上网**
``` stata
$ rm -rf /etc/udev/rules.d/70-persistent-net.rules
```
**(3)增加一行到/etc/sysconfig/network**

``` ini
NOZERCONF=yes
```

**(4)安装cloud-init（可选），cloud-init可以在开机时进行密钥注入以及修改hostname等，关于cloud-init，陈沙克的一篇博文有介绍：http://www.chenshake.com/about-openstack-centos-mirror/**

``` vala
$ yum install -y cloud-utils cloud-init parted
```

修改配置文件/etc/cloud/cloud.cfg ，在cloud_init_modules 下面增加:

``` ldif
- resolv-conf
```

**(5)设置系统能自动获取openstack指定的hostname和ssh-key（可选）**
编辑/etc/rc.local文件，该文件在开机后会执行，加入以下代码：

``` smali
if [ ! -d /root/.ssh ]; then
mkdir -p /root/.ssh
chmod 700 /root/.ssh
fi
# Fetch public key using HTTP
ATTEMPTS=30
FAILED=0

 

while [ ! -f /root/.ssh/authorized_keys ]; do
curl -f http://169.254.169.254/latest/meta-data/public-keys/0/openssh-key > /tmp/metadata-key 2>/dev/null
if [ $? -eq 0 ]; then
cat /tmp/metadata-key >> /root/.ssh/authorized_keys
chmod 0600 /root/.ssh/authorized_keys
restorecon /root/.ssh/authorized_keys
rm -f /tmp/metadata-key
echo “Successfully retrieved public key from instance metadata”
echo “*****************”
echo “AUTHORIZED KEYS”
echo “*****************”
cat /root/.ssh/authorized_keys
echo “*****************”

curl -f http://169.254.169.254/latest/meta-data/hostname > /tmp/metadata-hostname 2>/dev/null
if [ $? -eq 0 ]; then
TEMP_HOST=`cat /tmp/metadata-hostname`
sed -i “s/^HOSTNAME=.*$/HOSTNAME=$TEMP_HOST/g” /etc/sysconfig/network
/bin/hostname $TEMP_HOST
echo “Successfully retrieved hostname from instance metadata”
echo “*****************”
echo “HOSTNAME CONFIG”
echo “*****************”
cat /etc/sysconfig/network
echo “*****************”

else
echo “Failed to retrieve hostname from instance metadata. This is a soft error so we’ll continue”
fi
rm -f /tmp/metadata-hostname
else
FAILED=$(($FAILED + 1))
if [ $FAILED -ge $ATTEMPTS ]; then
echo “Failed to retrieve public key from instance metadata after $FAILED attempts, quitting”
break
fi
echo “Could not retrieve public key from instance metadata (attempt #$FAILED/$ATTEMPTS), retrying in 5 seconds…”
sleep 5
fi
done
```

或者

``` bash
# set a random pass on first boot
if [ -f /root/firstrun ]; then
  dd if=/dev/urandom count=50|md5sum|passwd --stdin root
  passwd -l root
  rm /root/firstrun
fi

if [ ! -d /root/.ssh ]; then
  mkdir -m 0700 -p /root/.ssh
  restorecon /root/.ssh
fi
# Get the root ssh key setup
# Get the root ssh key setup
ReTry=0
while [ ! -f /root/.ssh/authorized_keys ] && [ $ReTry -lt 10 ]; do
  sleep 2
  curl -f http://169.254.169.254/latest/meta-data/public-keys/0/openssh-key > /root/.ssh/pubkey
  if [ 0 -eq 0 ]; then
    mv /root/.ssh/pubkey /root/.ssh/authorized_keys
  fi
  ReTry=$[Retry+1]
done
chmod 600 /root/.ssh/authorized_keys && restorecon /root/.ssh/authorized_keys
```
主要目的就是获取hostname和公钥

**(6)其他**

route命令查看一下路由表

查看/etc/ssh/sshd_conf中PermitRootLogin是不是为yes

清除操作记录

``` elixir
清除登陆系统成功的记录
[root@localhost root]# echo > /var/log/wtmp //此文件默认打开时乱码，可查到ip等信息
[root@localhost root]# last //此时即查不到用户登录信息

清除登陆系统失败的记录
[root@localhost root]# echo > /var/log/btmp //此文件默认打开时乱码，可查到登陆失败信息
[root@localhost root]# lastb //查不到登陆失败信息
 
清除历史执行命令
[root@localhost root]# history -c //清空历史执行命令
[root@localhost root]# echo > ./.bash_history //或清空用户目录下的这个文件即可
 
导入空历史记录
[root@localhost root]# vi /root/history //新建记录文件
[root@localhost root]# history -c //清除记录 
[root@localhost root]# history -r /root/history.txt //导入记录 
[root@localhost root]# history //查询导入结果

example 
[root@localhost root]# vi /root/history
[root@localhost root]# history -c 
[root@localhost root]# history -r /root/history.txt 
[root@localhost root]# history 
[root@localhost root]# echo > /var/log/wtmp  
[root@localhost root]# last
[root@localhost root]# echo > /var/log/btmp
[root@localhost root]# lastb 
[root@localhost root]# history -c 
[root@localhost root]# echo > ./.bash_history
[root@localhost root]# history
```
关闭虚拟机

## 3、宿主机操作

资料：[KVM镜像管理利器-guestfish使用详解](https://www.cnblogs.com/BuildingHome/p/4834859.html)

1）安装guestfish套件安装

``` ebnf
$ yum install libguestfs-tools
```

2）压缩镜像文件

``` stata
$ virt-sparsify --compress centos7-dis.qcow2 centos7-dis-cloud.qcow2
```

![enter description here](1.png)
镜像制作完成

上传openstack

# 二、参考文档：

[penStack镜像制作-CentOS](http://www.cnblogs.com/gorlf/p/4140740.html)

[openstack镜像制作思路、指导及问题总结](http://www.aboutyun.com/thread-6617-1-1.html)

[openstack制作centos6](http://blog.csdn.net/xiegh2014/article/details/53248403).5镜像

[制作OpenStack上使用的CentOS系统镜像](http://www.linuxidc.com/Linux/2012-10/72483.htm)

[KVM镜像管理利器-guestfish使用详解](https://www.cnblogs.com/BuildingHome/p/4834859.html)

[CentOS清除用户登录记录和命令历史方法](http://blog.csdn.net/leadway123/article/details/49155421)