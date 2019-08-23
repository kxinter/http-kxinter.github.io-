---
title: 双机热备Heartbeat+drbd
tags:
  - heartbeat
  - drbd
  - 双机
  - 部署
categories:
  - Linux
copyright: true
password: 123456
date: 2018-09-07 17:51:13
---

# 1 环境
<!--more-->
系统：Centos7.2 1151

软件：drbd84-utils-8.9.5-1.el7.elrepo.x86_64

主服务器：172.20.20.66

备服务器：172.20.20.35

虚拟IP（virtual_ip）：172.20.20.237

修改主服务器名称：masterNode  

修改备服务器名称： backupNode

主备服务器添加下方地址到/etc/hosts文件：

`172.20.20.66  masterNode`

`172.20.20.35  backupNode`

# 2 简单说明

主备服务器分别创建一个分区，挂载到新创建的目录drbd中，通过drbd目录完成数据同步。

只有主服务器挂载目录，备服务器不用挂载。

备服务器要挂载目录，需要先把主服务器设置成`secondary（备机）`，备服务器设置成`primary（主机）`，然后挂载到目录。

# 3 添加硬盘并挂载

## 3.1 查询硬盘信息

**（如果使用的是新加硬盘，可以在最下方看到硬盘信息，例子使用本地空闲空间）**

**例如：**    

  ![1](1.png)                               


``` elixir
[root@bogon /]# fdisk -l
```

![2](2.png)

``` elixir
[root@bogon /]# df –h
```

![3](3.png)

## 3.2 Fdisk创建分区

``` elixir
[root@bogon /]# fdisk /dev/sda
```

![4](4.png)


> **注：下图设置分区格式可以省略，后面会进行格式化。**

![5](5.png)



## 3.3 查看硬盘信息

``` elixir
[root@bogon /]# fdisk –l
```

![6](6.png)



## 3.4 Partprobe刷新分区表（注：最好每做一步遇到找不到问题都刷新一下）

``` elixir
[root@bogon /]# partprobe
```



# 4 安装配置drbd

## 4.1 YUM安装drbd

``` scala
[root@localhost mapper]# rpm --import http://elrepo.org/RPM-GPG-KEY-elrepo.org

[root@localhost mapper]# rpm -Uvh http://www.elrepo.org/elrepo-release-7.0-2.el7.elrepo.noarch.rpm

[root@localhost mapper]# yum -y install drbd84-utils kmod-drbd84
```

### 4.1.1 问题1

二次安装存在YUM安装失败，需要源码安装，源码安装包在http://oss.linbit.com/drbd/ 下载。

Rpm包在https://pkgs.org/centos-7/elrepo-x86_64/kmod-drbd84-8.4.6-1.el7.elrepo.x86_64.rpm.html

https://pkgs.org/centos-7/elrepo-x86_64/drbd84-utils-8.9.5-1.el7.elrepo.x86_64.rpm/download/   下载。

``` llvm
[root@drbd2 home]# rpm -Uvh   http://elrepo.org/linux/elrepo/el7/x86_64/RPMS/drbd84-utils-8.9.5-1.el7.elrepo.x86_64.rpm   [root@htest2 home]# rpm -Uvh http://elrepo.org/linux/elrepo/el7/x86_64/RPMS/kmod-drbd84-8.4.6-1.el7.elrepo.x86_64.rpm
```

## 4.2 配置global_common.conf

**编辑全局配置：**

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

## 4.3 配置r0资源：

**创建r0资源：**

> 注：r0可以随便命名。

``` vim
vi  /etc/drbd.d/r0.res
```
写入文件内容：

``` q
resource   r0{ 

        on masterNode{ 

                device          /dev/drbd1; #逻辑设备的路径 

                disk            /dev/sda3;  #物理设备 

                address         192.168.58.128:7788; 

                meta-disk       internal; 

        }   

        on backupNode{ 

                device          /dev/drbd1; 

                disk            /dev/sda3; 

                address         192.168.58.129:7788; 

                meta-disk       internal; 

        }   

}
```

  

需要把上面用到的防火墙7788端口打开，这个端口是自定义的，如果嫌麻烦可以直接关掉防火墙。

> 注：`masterNode/ backupNode`是主机名字，根据实际情况书写。

说明：

`device`  是自定义的物理设备的逻辑路径

`disk`        是磁盘设备，或者是逻辑分区

`address`   是机器监听地址和端口

`meta-disk`   这个还没弄明白，看到的资料都是设为：internal（局域网）

## 4.4 建立resource

``` dsconfig
modprobe drbd               //载入 drbd 模块  

lsmod | grep drbd            //确认 drbd 模块是否载入  
```
![7](7.png)


``` dsconfig
dd if=/dev/zero of=/dev/sda2 bs=1M count=100    //把一些资料塞到 sda3 內 (否则 create-md 时会报错)  

drbdadm create-md r0                 //建立 drbd resource  

drbdadm up r0                    //   #启用资源
```


### 4.4.1 我遇到的问题1：


``` perl
[root@backupNode /]# drbdadm up r0  

1: Failure: (104) Can not open backing device.  

Command 'drbdsetup attach 1 /dev/sda2 /dev/sda3 internal' terminated with exit code   
```
原因是我之前已经挂在了/dev/sda3，需要先卸载/dev/sda3设备，解决办法:

``` nginx
 umount /dev/sda2 
```
问题解决.

### 4.4.2 我遇到的问题2：

``` elixir
[root@backupNode /]# drbdadm create-md r0  

‘r0‘ not defined in your config (for this host). 
```

 

   原因是drbd.conf配置文件计算机名和本机的计算机名不一致。

   修改配置文件计算机名。
   问题解决。

### 4.4.3 我遇到的问题3：

``` applescript
[root@htest2 drbd.d]# drbdadm create-md r0

drbd.d/r0.res:3: no minor given nor device name contains a minor number

drbd.d/r0.res:9: no minor given nor device name contains a minor number
```

`r0.res`中`drbd`资源必须含有数字，猜测与分区模块有重名。

![8](8.png)

![9](9.png)

问题解决。

### 4.4.4 我遇到的问题4

在centos 6.4上部署时，yum安装完成后加载模块报错。

``` 
正确安装drbd模块后，使用modprobe进行加载
# modprobe drbd
FATAL: Module drbd not found.
出现如上错误
```


原因：这是因为系统默认的内核并不支持此模块，所以需要更新内核
更新内核的方法：
可以用 yum install kernel* 方式来更新。 
如果你要节约点时间的话可以只更新一下的几个包： 
            kernel-devel 
            kernel 
            kernel-headers

更新后，记得要重新启动操作系统！！！

**> 注：以上每一步骤，都需要在主备服务器上进行配置设置。**

## 4.5 设置Primary Node

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

## 4.6 创建DRBD文件系统

上面已经完成了/dev/drbd1的初始化，现在来把/dev/drbd1格式化成ext4格式的文件系统,在masterNode上执行：

``` elixir
[root@masterNode /]# mkfs.ext3 /dev/drbd1  
```

输出：

``` mipsasm
mke2fs 1.41.12 (17-May-2010)  

文件系统标签=  

操作系统:Linux  

块大小=4096 (log=2)  

 分块大小=4096 (log=2)  

Stride=0 blocks, Stripe width=0 blocks  

589824 inodes, 2358959 blocks  

117947 blocks (5.00%) reserved for the super user  

第一个数据块=0  

Maximum filesystem blocks=2415919104  

 72 block groups  

32768 blocks per group, 32768 fragments per group  

 8192 inodes per group  

Superblock backups stored on blocks:  

        32768, 98304, 163840, 229376, 294912, 819200, 884736, 1605632  

   

 正在写入inode表: 完成  

Creating journal (32768 blocks): 完成  

Writing superblocks and filesystem accounting information: 完成  

   

This filesystem will be automatically checked every 21 mounts or  

 180 days, whichever comes first.  Use tune2fs -c or -i to override.  
```


然后，将`/dev/drbd1`挂载到之前创建好的`/drbd`目录：

``` groovy
[root@masterNode /]# mount /dev/drbd1 /drbd
```
现在只要把数据写入`/drbd`目录，`drbd`即会立刻把数据同步到`backupNode`的`/dev/sda2`分区上了。

## 4.7 DRBD同步测试

1、首先，在主服务器上先将设备卸载，同时将主服务器降为备用服务器：

``` elixir
[root@masterNode /]# umount /dev/drbd1  

[root@masterNode /]# drbdadm secondary r0  
```


2、然后，登录备用服务器，将备用服务器升为主服务器，同时挂载drbd1设备到 /drbd目录：

``` coffeescript
 [root@masterNode /]# ssh backup 

Last login: Sun May 27 19:57:17 2012 from masternode  

[root@backupNode ~]# drbdadm primary r0  

[root@backupNode ~]# mount /dev/drbd1 /drbd/  
```

3、最后，进入`/drbd`目录，就可以看到之前在另外一台机器上放入的数据了，如果没有看到，说明同步失败！

## 4.8 设置开机启动

> 注：设置DRBD开机启动，需要手动设置主备级别，找到方法后补充。

``` elixir
[root@drbd2 rc.d]# systemctl enable drbd
```

# 5 安装配置keepalived

(使用Heartbeat代替，只做了解，功能和heartbeat一样，Heartbeat自带drbd检测脚本)

# 5.1 YUM安装keepalived

Centos 7 自带 keepalived，可以直接YUM安装。

``` elixir
[root@drbd1 rc3.d]# yum install -y keepalived
```

# 5.2 配置keepalived.conf

``` groovy
[root@drbd1 /]# vi /etc/keepalived/keepalived.conf
```

### 5.2.1 主服务器配置

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

### 5.2.2 备服务器配置

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

## 5.3 启动服务

``` elixir
[root@drbd1 /]# systemctl start keepalived
```

## 5.4 查看网卡信息

   当启动`keepalived`后，查看网卡信息，主服务器会显示挂载虚拟IP`172.20.20.237`成功，备服务器没有挂载虚拟IP，如果主备服务器同时显示挂载虚拟Ip,则属于脑裂故障，需要继续调试。如果主服务器`keepalived`程序挂掉后，备用服务器会自动升级为主服务器，并挂载虚拟ip，主服务器恢复后恢复主从关系。

``` elixir
[root@drbd1 /]# ip a
```
![10](10.png)

![11](11.png)

## 5.5 验证测试

 1、在主服务器上新建一个网页，内容为 `172.20.20.66`

 2、在备用服务器上新建一个网页，内容为 `172.20.20.35`

 3、启动主备服务器的`http`服务和`Keepalived`服务

 4、通过浏览数，输入虚拟IP地址 `172.20.20.237`

        页面显示为 `172.20.20.66`

5、关闭主服务器的`Keepalived`服务，通过浏览器输入IP地址`172.20.20.237`

        页面显示为 `172.20.20.35`

6、再次启动主服务器的`Keepalived`服务，通过浏览器输入IP地址`172.20.20.237`

        页面显示为 `172.20.20.66`

## 5.6 设置开机启动服务

``` elixir
[root@drbd2 rc.d]# systemctl enable keepalived
```

# 6 安装配置heartbeat

## 6.1 创建用户和组

先创建用户和组，否则glue安装报错。

``` shell
# groupadd -g 200 haclient              #创建GID为200的用户组

# useradd -g haclient -u 200 -s /bin/false -M   hacluster        #创建用户（具体什么意思没懂）
```



YUM安装所需组件

``` vala
# yum install -y libtool libtool-ltdl-devel   glib2-devel libxml2-devel libxml2 bzip2-devel e2fsprogs-devel libuuid-devel   libxslt-devel asciidoc docbook-style-xsl libnet
```



## 6.2 安装glue

源码安装heartbeat之前首先得源码安装glue。

下载glue：http://www.linux-ha.org/wiki/Download 
    进入源码目录安装：**./autogen.sh**
    生成配置文件：**./configure**
    编译安装：**make && make install**

**./autogen.sh安装报错及解决办法**

``` 
报错信息：

You must have autoconf installed to compile the cluster-glue package.

Download the appropriate package for your system,

or get the source tarball at: ftp://ftp.gnu.org/pub/gnu/autoconf/
```
![12](12.png)

**解决办法：**

``` ebnf
yum install    libtool
```

## 6.3 安装agents

不安装agents的话，在安装Heartbeat时会报错，具体什么错误忘记记录了。

下载http://www.linux-ha.org/wiki/Download

``` vim
./autogen.sh

./configure

make && make install
```

## 6.4 安装heartbeat：

> 安装glue/agents/heartbeat,编译安装路径最好默认，自定义的话有报错。

    下载heartbeat：http://www.linux-ha.org/wiki/Downloads

    进入源码目录生成配置文件：`./ConfigureMe configure --disable-swig --disable-snmp-subagent`

编译安装：`make && make install`

**没有按照上述操作可能遇到的错误：**

``` vbnet
libtoolize: putting   libltdl files in `libltdl'.
  
 

libtoolize:   `COPYING.LIB' not found in `/usr/share/libtool/libltdl

./bootstrap   exiting due to error (sorry!).
```

解决办法：

``` ebnf
yum   install libtool-ltdl-devel
```

## 6.5 同步时间

同步两台节点的时间

``` shell
# rm -rf /etc/localtime

# \cp -f /usr/share/zoneinfo/Asia/Shanghai   /etc/localtime

# yum install -y ntp

# ntpdate -d cn.pool.ntp.org
```

## 6.6 配置主节点heartbeat

总共有三个文件需要配置:
`ha.cf` 监控配置文件
`haresources` 资源管理文件
`authkeys` 心跳线连接加密文件

配置文件位置 `/usr/share/doc/heartbeat/`

``` vim
# cp ha.cf haresources authkeys /etc/ha.d/    #拷贝配置文件到/etc/ha.d
```

### 6.6.1 修改ha.cf

``` lsl
debugfile /var/log/ha-debug      #用于记录 heartbeat 的调试信息

logfile /var/log/ha-log                  #指名heartbeat的日志存放位置。

logfacility   local0                           #如果未定义上述的日志文件,那么日志信息将送往local0(对应的#/var/log/messages),如果这 3 个日志文件都未定义,那么 heartbeat 默认情况下 将在/var/log 下建立 ha-debug 和 ha-log 来记录 相应的日志信息。 

#bcast eth1                                     #指明心跳使用以太网广播方式，并且是在eth1接口上进行 广播。（实际操作中没有指明。）

keepalive 2                                    #发送心跳报文的间隔,默认单位为秒,如果你毫秒为单位, 那么需要在后面跟 ms 单位,如 1500ms 即代表 1.5s 
  deadtime   30                                  #指定若备用节点在30秒内没有收到主节点的心跳信 号，则立即接管主节点的服务资源。 

warntime 10                                  #指定心跳延迟的时间为10秒。当10秒钟内备份节点不能接收到主节点的心跳信号时，就会往日志中写入一 个警告日志，但此时不会切换服务。发出最后的心跳 警告 信息的间隔。
  initdead 120                                   #在某些系统上，系统启动或重启之后需要经过一段时间 网络才能正常工作，该选项用于解决这种情况产生 的时 间间隔。取值至少为deadtime的两倍。  
  udpport 694                                  #设置广播/单播通信使用的端口，694为默认使用的端口号 

ucast eth0 192.168.60.132          #采用网卡eth0的udp单播来组织心跳，后面跟的
  IP地址应为双机对方的IP地址。  对方IP

auto_failback off                           #用来定义当主节点恢复后，是否将服务自动切回。如果不想启用，请设置为off，默认为on。heartbeat的两台主机分别为主节点和备份节点。主节点在正常情况下占用资源并运行所有的服务，遇到故障时把资源交给备份节点并由备份节点运行服务。在该选项设为on的情况下，一旦主节点恢复运行，则自动获取资源并取代备份节点；如果该选项设置为off，那么当主节点恢复后，将变为备份节点，而原来的备份节点成为主节点。根据实际情况，不能开启，选择off

node drbd1                                  #主节点主机名，可以通过命令"uanme   -n"查看。  
  node drbd2                                 #备用节点主机名。  

#ping 192.168.60.1                         #选择ping的节点，ping节点选择的越好，HA集群就 越强壮，可以选择固定的路由器作为ping节点，或者 应用服务器但是 最好不要选择集群中的成员作为ping 节点，ping节点 仅仅用来测试网络连接。如果指定了多个ping节点如ping   192.168.0.1 192.168.0.2那么只有当能ping通所有ping节点 时才认为网络是连通的，否则则认为不连通.实际中我没有开通检测。

respawn hacluster /usr/libexec/heartbeat/ipfail #该选项是可选配置， 意思 是以 hacluster 这 个用户身份运行/usr/lib/heartbeat/ ipfail 这个 插件 respawn列出与heartbeat一起启动和关闭的 进 程，该进程一般是和heartbeat集成的插件，这些 进程遇到故障可以自动重新启动。最常用的进程是 ipfail，此进程用于检测和处理网络故障，需要配合 ping或者ping_group语句,其中指定的ping node 来检测网络的连通性。在v2版本中，ipfail和crm有 冲突，不能同时使用，如果启用crm的情况下，可以 使用pingd插件代替ipfail

apiauth ipfail gid=haclient uid=hacluster   #指定对客户端 api 的访问控制,缺省为不可 访问，这里指定了 有权限访问 ipfail用户和组。(使用前边创建的用户和组)

#apiauth default  gid=haclient 
  （实际中没有开启此项设置，因为创建的用户和组就是默认用户和组的名字）当配置了默认用户组时，其他所有api授权命令失效且该用户组中的成员可以访问任何api库

如果不在ha.cf文件指定api库的访问权限，则默认的访问权限如下

service   default apiauthipfailuid=haclusterccmgid=haclientpinggid=haclientcl_statusgid=haclientlha-snmpagentuid=rootcrmuid=hacluster  
```



### 6.6.2 修改haresources

``` elixir
drbd1 IPaddr::192.168.84.132/24/eno16777736   drbddisk::r0 Filesystem::/dev/drbd1::/drbd

drbd1是主节点主机名，主备配置文件都一样。

解说：node1   IPaddr::192.168.60.200/24/eth0/    Filesystem::/dev/sdb5::/webdata::ext3  httpd cp.sh db2::db2inst1 其中，node1是HA集群的主节点，IPaddr为heartbeat自带的一个执行脚步，Heartbeat首先将执行/etc/ha.d/resource.d/IPaddr   192.168.60.200/24 start的操作，也就是虚拟出一个子网掩码为255.255.255.0，IP为192.168.60.200的地址。此IP为Heartbeat对外提供服务的网络地址，同时指定此IP使用的网络接口为eth0。接着，Heartbeat将执行共享磁盘分区的挂载操作，"Filesystem::/dev/sdb5::/webdata::ext3"相当于在命令行下执行mount操作，即"mount -t ext3 /dev/sdb5   /webdata"，然后启动httpd，接下列执行cp.sh这个脚本文件之后以db2inst1的身份启动db2。

其中cp.sh必须放置在/etc/ha.d/resource.d/或/etc/init.d/目录中。
```

> **注意主节点和备份节点中资源文件haresources要完全一样。**

### 6.6.3 修改authkeys

> **此配置文件必须设置权限为600（固定的）**

``` lsl
Chmod 600 /etc/ha.d/authkeys
```


``` lsl
auth 1  
  1 crc  
  #2 sha1 sha1_any_password  
  #3 md5 md5_any_password 

authkeys文件用于设定Heartbeat的认证方式，共有3种可用的认证方式，即crc、md5和sha1。3种认证方式的安全性依次提高，但是占用的系统资源也依次增加。如果Heartbeat集群运行在安全的网络上，可以使用crc方式；如果HA每个节点的硬件配置很高，建议使用sha1，这种认证方式安全级别最高；如果是处于网络安全和系统资源之间，可以使用md5认证方式。这里我们使用crc认证方式.

需要说明的一点是：无论auth后面指定的是什么数字，在下一行必须作为关键字再次出现，例如指定了"auth   6"，下面一定要有一行"6 认证类型"。
  最后确保这个文件的权限是600（即-rw-------）。
```

### 6.6.4 对配置文件进行软链接

在`/usr/etc/ha.d/`目录创建软链接，在部署中通过查看日志文件发现是通过此目录运行软件的，具体没搞明白，网上说拷贝的`/etc/ha.d`目录就行了，不知道为什么，为了省事，干脆创建软链接，这样就没问题了。此功能好用。

``` vim
ln -sv /etc/ha.d/shellfuncs /usr/etc/ha.d/shellfuncs

ln -sv /etc/ha.d/ha.cf /usr/etc/ha.d/ha.cf

ln -sv /etc/ha.d/authkeys /usr/etc/ha.d/authkeys

ln -sv /etc/ha.d/resource.d /usr/etc/ha.d/resource.d

ln -sv /etc/ha.d/haresources   /usr/etc/ha.d/haresources

ln -sv /etc/ha.d/harc /usr/etc/ha.d/harc

ln -sv /etc/ha.d/rc.d /usr/etc/ha.d/rc.d
```



复制ocf文件，如果没有，启动的时候会报错

``` 
cp /usr/lib/ocf/lib/heartbeat/ocf-binaries /usr/lib/ocf/resource.d/heartbeat/.ocf-binaries

cp /usr/lib/ocf/lib/heartbeat/ocf-directories /usr/lib/ocf/resource.d/heartbeat/.ocf-directories

cp /usr/lib/ocf/lib/heartbeat/ocf-returncodes /usr/lib/ocf/resource.d/heartbeat/.ocf-returncodes

cp /usr/lib/ocf/lib/heartbeat/ocf-shellfuncs /usr/lib/ocf/resource.d/heartbeat/.ocf-shellfuncs
```

这一块没有用到，发现默认情况下目录里面就存在这些文件，此处作为参考。

备用节点配置文件和主节点配置文件基本一样，只有一个地方有区别。就是

`ucast eth0 192.168.60.132`   **IP地址是对方的IP**

# 7 启动程序顺序

第一步：启动主备节点drbd服务

``` elixir
[root@drbd1 ha.d]# drbdadm up r0
```

第二步：设置升级主节点为primary，并挂载到目录

``` elixir
[root@drbd1 ha.d]# drbdadm primary r0

[root@drbd1 ha.d]# mount /dev/drbd1 /drbd/
```

第三步：启动主备节点Heartbeat服务

``` elixir
[root@drbd1 ha.d]# service heartbeat start
```

等待主备节点连接并配置完成，可以通过`ip a` 命令查看虚拟ip是否生效。以下环境部署完成。在进行主节点维护中，恢复的话必须手动操作，避免出错。



# 8 附件

链接: http://pan.baidu.com/s/1mibp7Uo   密码: y99z 



