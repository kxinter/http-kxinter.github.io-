---
title: Centos7部署vpn服务器_PPTP
tags:
  - vpn
  - pptp
  - 部署
categories:
  - Linux
copyright: true
date: 2018-09-10 11:59:09
---

# 1 环境
<!--more-->
系统：centos 7.2 1511

# 2 详细步骤

## 2.1 验证内核是否加载了MPPE模块：

内核的`MPPE`模块用于支持`Microsoft Point-to-Point Encryption`。Windows自带的VPN客户端就是使用这种加密方式，主流的`Linux Desktop`也都有`MPPE`支持。其实到了我们这个内核版本，默认就已经加载了`MPPE`，只需要使用下面命令验证一下，显示`MPPE ok`即可：

``` vim
modprobe ppp-compress-18 && echo MPPE is ok
```

## 2.2 安装所需的软件包：

``` nginx
yum install –y ppp pptpd iptables
```

## 2.3 修改ppp配置文件

配置`ppp`需要编辑它的两个配置文件，一个是`option`（选项）文件，一个是`用户账户`文件。首先编辑option文件：

``` lsl
vi /etc/ppp/options.pptpd

ms-dns 8.8.8.8                  #去掉“＃”，设置ＤＮＳ

ms-dns 8.8.4.4
```


``` nginx
vi /etc/ppp/chap-secrets
```

这个文件非常简单，其中用明文存储VPN客户的用户名、服务名称（`option.pptpd`文件`name pptpd`   vpn的服务器名字）、密码和IP地址范围，每行一个账户：

``` gcode
username1         pptpd    passwd1    *

username2         pptpd    passwd2    *
```

其中第一第三列分别是用户名和密码；第二列应该和上面的文件`/etc/ppp/options.pptpd`中`name`后指定的服务名称一致；最后一列限制客户端IP地址，星号表示没有限制。

## 2.4 修改pptpd配置文件

``` lsl
vi /etc/pptpd.conf

option /etc/ppp/options.pptpd

logwtmp

localip 192.168.0.1

remoteip 192.168.0.207-217
```

其中`option`选项指定使用`/etc/ppp/options.pptpd`中的配置；`logwtmp`表示使用`WTMP日志`。

后面两行是比较重要的两行。VPN可以这样理解，Linux客户端使用一个虚拟网络设备`ppp0`（Windows客户端也可以理解成VPN虚拟网卡），连接到服务器的虚拟网络设备`ppp0`上，这样客户端就加入了服务器端`ppp0`所在的网络。`localip`就是可以分配给服务器端`ppp0`的IP地址，`remoteip`则是将要分配给客户端`ppp0`（或者虚拟网卡）的。

这两项都可以是多个IP，一般`localip`设置一个`IP`就行了，`remoteip`则视客户端数目，分配一段IP。其中`remoteip`的`IP段`需要和`localip`的`IP段`一致。

`localip`和`remoteip`所处的`IP段`可以随意些指定，但其范围内不要包含实际网卡`eth0`的IP地址。一般情况下，使用上面配置文件中的配置就好使了，你需要做的只是把`192.168.0.207-217`这个IP区间修改成你喜欢的`192.168.0.a-b`，其中`1<a<b<255`。

## 2.5 打开内核的IP转发功能：

``` stylus
vi /etc/sysctl.conf

找到其中的行：

net.ipv4.ip_forward = 0
```

修改为：

``` stylus
net.ipv4.ip_forward = 1
```

然后执行下面命令使上述修改生效：

``` nginx
sysctl –p
```

## 2.6 配置iptables防火墙放行和转发规则：

最后，还需要配置防火墙。这里配置防火墙有三个目的：一是设置默认丢弃规则，保护服务器的安全；二是放行我们允许的数据包，提供服务；三是通过配置nat表的POSTROUTING链，增加NAT使得VPN客户端可以通过服务器访问互联网。总之我们的原则就是，只放行我们需要的服务，其他统统拒绝。

首先介绍跟PPTP VPN相关的几项：

   - 允许GRE(Generic Route Encapsulation)协议，PPTP使用GRE协议封装PPP数据包，然后封装成IP报文

   - 放行1723端口的PPTP服务

   - 放行状态为RELATED,ESTABLISHED的入站数据包（正常提供服务的机器上防火墙应该都已经配置了这一项）

   - 放行VPN虚拟网络设备所在的192.168.0.0/24网段与服务器网卡eth0之间的数据包转发

   - 为从VPN网段192.168.0.0/24转往网卡eth0的出站数据包做NAT

如果你其他的防火墙规则已经配置好无需改动，只需要增加上述相关VPN相关的规则，那么执行下面几条命令即可（第三条一般不用执行，除非你原来的防火墙连这个规则都没允许，但是多执行一遍也无妨）：



``` lsl
iptables -A INPUT -p gre -j ACCEPT

iptables -A INPUT -p tcp -m tcp --dport 1723 -j ACCEPT

iptables -A INPUT -m state --state RELATED,ESTABLISHED -j ACCEPT

iptables -A FORWARD -s 192.168.0.0/24 -o eth0 -j ACCEPT

iptables -A FORWARD -d 192.168.0.0/24 -i eth0 -j ACCEPT

iptables -t nat -A POSTROUTING -s 192.168.0.0/24 -o eth0 -j MASQUERADE
```



# 3 问题总结

使用centos 6.5部署vpn pptp

遇到连接错误，总是连接不上

## 3.1 日志错误1：

``` applescript
[root@localhost log]#vi /var/log/messages 
Jun 13 14:00:25 localhost pptpd[9248]: CTRL: Client 101.69.242.170 control connection started
Jun 13 14:00:25 localhost pptpd[9248]: CTRL: Starting call (launching pppd, opening GRE)
Jun 13 14:00:25 localhost pppd[9249]: Warning: can't open options file /root/.ppprc: Permission denied
Jun 13 14:00:25 localhost pppd[9249]: The remote system is required to authenticate itself
Jun 13 14:00:25 localhost pppd[9249]: but I couldn't find any suitable secret (password) for it to use to do so.
Jun 13 14:00:25 localhost pppd[9249]: (None of the available passwords would let it use an IP address.)
Jun 13 14:00:25 localhost pptpd[9248]: GRE: read(fd=6,buffer=6124a0,len=8196) from PTY failed: status = -1 error = Input/output error, usually caused by unexpected termination of pppd, check option syntax and pppd logs
Jun 13 14:00:25 localhost pptpd[9248]: CTRL: PTY read or GRE write failed (pty,gre)=(6,7)
Jun 13 14:00:25 localhost pptpd[9248]: CTRL: Client 101.69.242.170 control connection finished
```

相关配置文件

``` lsl
[root@localhost ~]# more /etc/pptpd.conf |grep -v ^#
option /etc/ppp/options.pptpd
debug /var/log/pptpd.log
localip 10.10.1.20
remoteip 10.10.1.30-254

[root@localhost ~]# more /etc/ppp/options.pptpd|grep -v ^#
name pptpd
refuse-pap
refuse-chap
refuse-mschap
require-mschap-v2
require-mppe-128
ms-dns 221.228.255.1
ms-dns 223.6.6.6
proxyarp
lock
nobsdcomp 
novj
novjccomp
nologfd
```

我使用的centos 6.5 64bit ，相关安装包如下：

``` lsl
[root@localhost ~]# rpm -qa |grep "ppp*"
libreport-plugin-rhtsupport-2.0.9-19.el6.centos.x86_64
device-mapper-event-libs-1.02.79-8.el6.x86_64
ppl-0.10.2-11.el6.x86_64
pptpd-1.4.0-3.el6.x86_64
abrt-addon-ccpp-2.0.8-21.el6.centos.x86_64
device-mapper-1.02.79-8.el6.x86_64
device-mapper-event-1.02.79-8.el6.x86_64
tcp_wrappers-7.6-57.el6.x86_64
cloog-ppl-0.15.7-1.2.el6.x86_64
snappy-1.1.0-1.el6.x86_64
kernel_ppp_mppe-1.0.2-3dkms.noarch
pptp-1.7.2-8.1.el6.x86_64
device-mapper-libs-1.02.79-8.el6.x86_64
tcp_wrappers-libs-7.6-57.el6.x86_64
cpp-4.4.7-4.el6.x86_64
device-mapper-persistent-data-0.2.8-2.el6.x86_64
ppp-2.4.5-5.el6.x86_64
```

现在不知道问题出在什么地方，麻烦各位帮忙看看，谢谢！！！


已经解决，修改配置

``` r
options.pptpd把
require-mschap-v2
require-mppe-128
```

这两行注释掉即可。如下图：
![enter description here](1.png) 

> **这里是关闭加密，跳过加密。此方法修改过没有用处。**



## 3.2 错误2：

``` subunit
[root@webserver ~]# sysctl -p

net.ipv4.ip_forward = 1

net.ipv4.conf.default.rp_filter = 1

net.ipv4.conf.default.accept_source_route = 0

kernel.sysrq = 0

kernel.core_uses_pid = 1

net.ipv4.tcp_syncookies = 1

error: "net.bridge.bridge-nf-call-ip6tables" is an unknown key

error: "net.bridge.bridge-nf-call-iptables" is an unknown key

error: "net.bridge.bridge-nf-call-arptables" is an unknown key

kernel.msgmnb = 65536

kernel.msgmax = 65536

kernel.shmmax = 68719476736

kernel.shmall = 4294967296

You have mail in /var/spool/mail/root
```

版本没错但是发现转发有错


> **加载模块然后重启解决**

``` mipsasm
[root@webserver ~]# modprobe bridge

[root@webserver ~]# lsmod | grep bridge

bridge                 79078  0 

stp                     2218  1 bridge

llc                     5546  2 bridge,stp

[root@webserver ~]# service pptpd restart

Shutting down pptpd:                                       [  OK  ]

Starting pptpd:                                            [  OK  ]

Warning: a pptpd restart does not terminate existing 

connections, so new connections may be assigned the same IP 

address and cause unexpected results.  Use restart-kill to 

destroy existing connections during a restart.
```

<div class="note info"><p>此处是重新加载`bridge`模块，重新加载了，没有作用，后来实验，发现是否重新加载，都不影响vpn使用,最终就没管他，不知道是否有影响。</p></div>

 

最终如何解决的，其实也没有做什么修改，就是重新`yum remove –y ppp* pptp* `后，重新`yum install –y ppp* pptp* iptables*` 后，多次重启，和重设置vpn帐号，又可以用了，**I don’t know why.**

 

**最终解决方案：**

后来发现一个问题，当客户端开启防火墙的时候就能连接，当关闭防火墙的时候就无法连接报错。I don’t know why.

