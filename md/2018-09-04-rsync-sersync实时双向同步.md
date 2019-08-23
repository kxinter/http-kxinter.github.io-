---
title: rsync和sersync实时双向同步
tags:
  - rsync
categories:
  - Linux
copyright: true
date: 2018-09-04 18:10:20
---

# 1 环境
<!--more-->
<table>
    <tr>
        <td>操作系统</td> 
        <td>Centos7.1 511</td> 
   </tr>
       <tr>
        <td>主服务器</td>
		<td> 172.20.20.111</td> 
   </tr>
       <tr>
        <td>从服务器 </td>
		<td> 172.20.22.99 </td>
   </tr>
    <tr>
        <td colspan="2">测试目的：实现主服务器/rsync目录与从服务器/rsync目录实时双向同步.</td>   
    </tr>
	<tr>
	   <td colspan="2">参考资料：http://blog.sina.com.cn/s/blog_9f4962b10102vqua.html 
		http://402753795.blog.51cto.com/10788998/1713179  </td>
		</tr>
</table>
<!--more-->

# 2 以下操作主从服务器都要操作

## 2.1 关闭selinux

``` shell
[root@server1]# vi /etc/selinux/config     #编辑防火墙配置文件

#SELINUX=enforcing                 #注释掉
SELINUX=disabled                #增加

[root@server1]# setenforce 0               #立即生效
```

## 2.2 开启防火墙tcp 873端口（Rsync默认端口）

``` elixir
[root@server1 ]#  firewall-cmd --zone=public --add-port=873/tcp --permanent

[root@server1 ]#  firewall-cmd --reload
```

> 主服务做rsync服务端，从服务器做客户端

# 3 安装rsync（服务端）


``` ebnf
Yum install rsync
```

## 3.1 编辑配置文件


``` nix
Vi /etc/rsyncd.conf

uid = root                        #/rsync目录用户属性

gid = root                        #/rsync目录用户组属性

port = 873                       #rsync同步端口号，默认873

address = 172.20.20.111           #本机IP地址

use chroot = yes                  #是否禁锢用户

read only = no                   # no客户端可上传文件,yes只读

write only = no                   # no客户端可下载文件,yes不能下载

#list = yes

hosts allow = 172.20.22.99               #指定可以联系的客户端主机名或IP

hosts deny = *                         #指定拒绝访问的客户端主机名或IP

max connections = 50                    # 客户端最大连接数目（设置大些，否则同步中可能报错）

motd file = /etc/rsyncd.motd             

pid file = /var/run/rsyncd.pid            #启动后将进程PID放入此文件

log file = /var/log/rsyncd.log             # rsync使用syslog输出日志

lock file = /var/run/rsync.lock           #设置rsync锁文件

transfer logging = yes

log format = %t%a%m%b

syslog facility = local3

timeout = 300                     #超时时间

[liferay1]                         # 要同步的模块名

path =/rsync                      # 要同步的目录（客户端同步文件到哪个目录）

list = yes                        

ignore errors

auth users = root                  # 登陆系统使用的用户名，没有默认为匿名（非主机用户，自定义）

secrets file = /etc/rsyncd.pass1       ## 密码文件存放的位置

comment = linuxsir liferay1           # 这个名名称无所谓，最后模块名一直
```


## 3.2 配置密码文件

密码文件为配置文件中所写的文件/etc/rsyncd.secrets格式为`**账户:密码**`


``` elixir
[root@server1 ]# vi /etc/rsyncd.pass1
```


输入帐号密码（自定义）
![enter description here](1.png)


## 3.3 修改配置文件及密码文件权限(必须600)


``` shell
   # chmod 600 /etc/rsyncd.conf

   # chmod 600 /etc/rsyncd.pass1
```


## 3.4 检查rsync是否启动


``` vala
# lsof -i :873 
或
# netstat -an |grep 873
```


# 4 配置从服务器(客户端)

## 4.1 	设定密码文件

配置密码文件 (注：为了安全，设定密码档案的属性为：`600`。`rsync.pass1`的密码一定要和`Rsync 服务器端/etc/rsyncd.pass1`的设定的密码一样)


``` vala
# vi /etc/rsyncd.pass1
```


     

> 密码文件可与服务端密码文件不一样，这里为了便于记忆，都设置为rsyncd.pass1



![enter description here](2.png)


**客户端密码文件只输入密码，不输入帐号。**

## 4.2 赋予600权限



``` shell
# chmod 600 /etc/rsyncd.pass1 # 必须修改权限
```


## 4.3 测试


``` elixir
$ rsync -avzP --password-file=/etc/rsyncd.pass1 /opt/liferay/data/ tongbu@172.20.20.111::liferay1
```


从客户端同步/rsync目录到服务端

## 4.4 安装sersync

下载地址：https://code.google.com/archive/p/sersync/downloads

下载sersync2.5.4_64bit_binary_stable_final.tar

### 4.4.1 解压


``` css
Tar –xvf    sersync2.5.4_64bit_binary_stable_final.tar
```


解压文件到`/usr/local`,重命名为`serync`

### 4.4.2 修改配置文件


``` lasso
Vi /usr/local/serync/confxml.xml
```



	
``` xml
<?xml version="1.0"   encoding="ISO-8859-1"?>

<head version="2.5">

      <host hostip="localhost"   port="8008"></host>

      <debug start="true"/>

      <fileSystem xfs="false"/>

      <filter start="false">                       #设置为true，开启同步过滤，这里不开启

          <exclude expression="(.*)\.svn"></exclude>

          <exclude expression="(.*)\.gz"></exclude>

          <exclude expression="^info/*"></exclude>

          <exclude expression="^static/*"></exclude>

      </filter>

      <inotify>

          <delete start="true"/>

          <createFolder start="true"/>

          <createFile start="true"/>

          <closeWrite start="true"/>

          <moveFrom start="true"/>

          <moveTo start="true"/>

          <attrib start="false"/>

          <modify start="false"/>

      </inotify>

 

      <sersync>

          <localpath watch="/rsync">

            <remote ip="172.20.20.111" name="liferay1"/>

            <!--<remote   ip="192.168.8.39" name="tongbu"/>-->

            <!--<remote   ip="192.168.8.40" name="tongbu"/>-->

          </localpath>

          <rsync>

            <commonParams   params="-artuz"/>

            <auth start="true" users="root"   passwordfile="/etc/rsyncd.pass1"/>

            <userDefinedPort   start="false" port="874"/><!-- port=874 -->

            <timeout   start="false" time="100"/><!-- timeout=100 -->

            <ssh   start="false"/>

          </rsync>

          <failLog path="/usr/local/sersync/rsync_fail_log.sh"   timeToExecute="60"/><!--de

fault every 60mins execute   once-->        <crontab   start="false" schedule="600"><!--600mins-->

            <crontabfilter   start="false">

                <exclude   expression="*.php"></exclude>

                <exclude   expression="info/*"></exclude>

            </crontabfilter>

          </crontab>

          <plugin start="false" name="command"/>

      </sersync>

 

      <plugin name="command">

          <param prefix="/bin/sh" suffix=""   ignoreError="true"/>    <!--prefix /opt/tongbu/

mmm.sh suffix-->        <filter   start="false">

            <include   expression="(.*)\.php"/>

              <include   expression="(.*)\.sh"/>

          </filter>

      </plugin>

 

      <plugin name="socket">

          <localpath watch="/opt/tongbu">
```


 


``` lua
修改的代码如下:

<delete start="true"/>

<createFolder start="true"/>

<createFile start="true"/>

<closeWrite start="true"/       

#对于大多数应用，可以尝试把createFile（监控文件事件选项）设置为false来提高性能，减少 rsync通讯。因为拷贝文件到监控目录会产生create事件与close_write事件，所以如果关闭create事件，只监控文件拷贝结束时的事件close_write，同样可以实现文件完整同步。 注意：强将createFolder保持为 true，如果将createFolder设为false，则不会对产生的目录进行监控，该目录下的子文件与子目录也不会被监控。所以除非特殊需要，请开启。默认情况下对创建文件（目录）事件与删除文件（目录）事件都进行监控，如果项目中不需要删除远程目标服务器的文件（目录），则可以将delete 参数设置为false，则不对删除事件进行监控。对于大多数应用，可以尝试把createFile（监控文件事件选项）设置为false来提高性能，减少 rsync通讯。因为拷贝文件到监控目录会产生create事件与close_write事件，所以如果关闭create事件，只监控文件拷贝结束时的事件close_write，同样可以实现文件完整同步。 注意：强将createFolder保持为 true，如果将createFolder设为false，则不会对产生的目录进行监控，该目录下的子文件与子目录也不会被监控。所以除非特殊需要，请开启。默认情况下对创建文件（目录）事件与删除文件（目录）事件都进行监控，如果项目中不需要删除远程目标服务器的文件（目录），则可以将delete 参数设置为false，则不对删除事件进行监控。
<localpath watch="/rsync">：          #本地监听目录，源服务器同步目录

<remote ip="172.20.20.111" name="liferay1"/>：    #服务端IP地址和模块名
<auth start="true" users="root" passwordfile="/etc/rsyncd.pass1"/>

#服务端模块rsync认证用户名,服务端rsync认证用户的密码存放路径
failLog path="/tmp/rsync_fail_log.sh"   #脚本运行失败日志路径
```


### 4.4.3  创建日志文件

``` stata
Vi /usr/local/serync/ rsync_fail_log.sh
```
### 4.4.4 启动sersync


``` groovy
/usr/local/sersync/sersync2 -d -r -o /usr/local/sersync/confxml.xml
```


此时客户端可以实施同步目录文件到服务端了。

# 5 实现双向同步

把主从服务器角色互换，从服务器作为服务端，主服务器作为客户端重新部署一次，这样就可以双向实时同步了。



# 6 附件：

=[sersync2.5.4_64bit_binary_stable_final.tar.gz](sersync2.5.4_64bit_binary_stable_final.tar.gz)