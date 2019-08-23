---
title: Redis+Keepalived双机热备
tags:
  - redis
  - keepalived
  - 双机
categories:
  - Linux
date: 2018-08-30 16:25:31
---

# 1 环境
<!--more-->
主机	IP	OS
		
		

|   主机  |IP     |    OS |
| --- | --- | --- |
|   master-server  |   172.20.22.145  |  centos7.2   |
|   slave-server  |   172.20.22.53  |  centos7.2   |

# 2 参考资料

https://my.oschina.net/guol/blog/182491

http://blog.csdn.net/qguanri/article/details/51120178

http://blog.csdn.net/zgf19930504/article/details/52024724

# 3 整体思路

在keepalived+redis的使用过程中有四种情况：

1.  一种是keepalived挂了，同时redis也挂了，这样的话直接VIP飘走之后，是不需要进行redis数据同步的，因为redis挂了，你也无法去master上同步，不过会损失已经写在master上却还没同步到slave上面的这部分数据。

2. 另一种是keepalived挂了，redis没挂，这时候VIP飘走后，redis的master/slave还是老的对应关系，如果不变化的话会把数据写入redis slave中，从而不会同步到master上去，这就要借助监控脚本反转redis的master/slave关系。这时候就要预留一点时间进行数据同步，然后反转master/slave。

3. 还有一种是keepalived没挂，redis挂了，这时候根据监控脚本会检测到redis挂了，并且降低keepalived master的优先级，同样会导致VIP飘走，情况和第二种一样，也是需要进行数据同步，然后反转当前redis的master/slave关系的。

4. 随后一种是keepalived没挂，redis也没挂，大吉大利啊，什么都不用操作。

> 本文的实验环境四种情况都适合，第一种是不需要同步数据的，脚本会默认去同步数据，但是其实是不会成功的。脚本主要是用来处理第二和第三种情况的。

# 4 安装redis

参考本站：centos7安装redis

## 4.1 修改主从redis配置文件

``` vim
vim /etc/redis/6379.conf
```

### 4.1.1 主redis:

``` lsl
#修改bind绑定IP,只有绑定的IP才能访问redis，0.0.0.0标识所有地址都能访问。
bind 0.0.0.0
```


### 4.1.2 从redis:

``` lsl
#修改bind绑定IP,只有绑定的IP才能访问redis，0.0.0.0标识所有地址都能访问。
bind 0.0.0.0
#添加slaveof&nbsp;IP&nbsp;Port,表示作为该IP服务器的备机
slaveof 172.20.22.145 6379
```


## 4.2 启动并测试

``` thrift
service redis_6379 start
```

### 4.2.1 主redis

``` css
[root@bogon ~]# redis-cli -p 6379                       #登录redis

127.0.0.1:6379> set hao 333                                  #添加hao值为333 

OK

127.0.0.1:6379> get hao                                        #查看hao的值

"333"

127.0.0.1:6379>
```

### 4.2.2 从redis

``` css
[root@bogon scripts]# redis-cli -p 6379

127.0.0.1:6379> get hao                               #查看hao的值，获取到值说明同步成功。

"333"

127.0.0.1:6379>
```

# 5 安装keepalived

``` ebnf
yum install keepalived
```

## 5.1 修改配置文件

``` vim
vim /etc/keepalived/keepalived.conf
```
```
#MASTER配置文件：

! Configuration File for keepalived
vrrp_script chk_redis {
        script "/etc/keepalived/scripts/chk_redis.sh"     #监控脚本
        interval 2                                        #监控间隔时间 秒
        timout 2                                          #响应超时：超过多长时间未响应认为是失败
        fall 3                                            #检测失败几次，认为是redis服务器挂了
        weight -60                       #自我确定服务器挂了之后,优先级加多少, 也就是宕机之后 priority 加多少weight，这里是减60
}
vrrp_instance VI_1 {
    state MASTER                         #MASTER表示主，BACKUP表示为从
    interface eth0                       #eth0表示监听的网卡
    virtual_router_id 51
    priority 100                         #优先级，从服务器推选主服务器就是根据这个来比较的，从服务器必须小于主服务器优先级。
    advert_int 1
    authentication {
        auth_type PASS                   #认证凭证，可自定义
        auth_pass 1111
    }
    track_script {
          chk_redis                      #运行chk_redis模块
    }
    virtual_ipaddress {
        172.20.22.199                                      #VIP地址（虚拟IP）
    }
    unicast_src_ip 172.20.22.145               #keepalived 内部通信,本机ip 地址（没加也没影响）
    unicast_peer {
        172.20.22.53                      
    }
    notify_master /etc/keepalived/scripts/redis-master.sh           #keepalived 状态切换master时执行的脚本
    notify_backup /etc/keepalived/scripts/redis-backup.sh           #keepalived 状态切换为backup时执行的脚本
    notify_fault /etc/keepalived/scripts/redis-fault.sh             #keepalived 状态为fault时执行的脚本
    notify_stop /etc/keepalived/scripts/redis-stop.sh               #keepalived 服务停止时执行脚本
}
```


``` pf.conf
# BACKUP配置文件

backup配置文件至修改了2处，其它都一样。

! Configuration File for keepalived
vrrp_script chk_redis {
        script "/etc/keepalived/scripts/chk_redis.sh"   ###监控脚本
        interval 2                                        ###监控时间
        timout 2          #响应超市：超过多长时间未响应认为是失败
        fall 3            #检测失败几次，认为是redis服务器挂了
        weight -60           #自我确定服务器挂了之后,优先级加多少, 也就是宕机之后 priority + weight
}
vrrp_instance VI_1 {
    state BACKUP
    interface enp2s0

virtual_router_id 51
    priority 50
    advert_int 1
    authentication {
        auth_type PASS
        auth_pass 1111
    }
    track_script {
          chk_redis
    }
    virtual_ipaddress {
        172.20.22.199
    }
    unicast_src_ip 172.20.22.53
    unicast_peer {
        172.20.22.145
    }
    notify_master /etc/keepalived/scripts/redis-master.sh
    notify_backup /etc/keepalived/scripts/redis-backup.sh
    notify_fault /etc/keepalived/scripts/redis-fault.sh
    notify_stop /etc/keepalived/scripts/redis-stop.sh
}
```

## 5.2 创建脚本

创建scripts目录 /etc/keepalived,在scripts目录内创建redis-master.sh,redis-backup.sh,redis-fault.sh,redis-stop.sh,chk_redis.sh

### 5.2.1 chk_redis.sh脚本

``` awk
#!/bin/bash  
#检测redis是否正常运行，根据检测结果返回不同的值
     
#日志文件位置  
logFile=/usr/etc/redis/keepalived/logs/redis-keepalived.log  
  
#ping 本机redis服务  
pingRS=`/usr/local/bin/redis-cli -a 123456 PING`  
  
#如果ping 的结果为PONG,那么返回0 ,否则返回1；PONG代表PING通redis,当返回值为1时，执行降低优先级操作。
if [ $pingRS == "PONG" ]; then  
   echo "[`date`] ping is ok !" >>$logFile  
   exit 0  
else  
   echo "[`date`] ping is error !" >>$logFile  
   exit 1  
fi
```


### 5.2.2 redis-master.sh

> （master主机脚本与slave主机基本雷同，只需修改远程ip地址）

``` ruby
#!/bin/bash
rediscli="redis-cli"
logfile="/var/log/keepalived-redis-state.log"
date >> %logfile
echo "[master]" >> $logfile
echo " 运行作为远程server备机并同步数据命令" >> $logfile
$rediscli SLAVEOF 172.20.22.53 6379 >> $logfile                  #远程redis IP地址，解释为以该IP为主，做数据同步。
sleep 10      #等待10秒，再运行下面命令。
echo "运行升级为主服务器命令" >> $logfile
$rediscli SLAVEOF NO ONE >> $logfile
echo "切换master完成" >> $logfile
```


### 5.2.3 redis-backup.sh

> （master主机脚本与slave主机基本雷同，只需修改远程ip地址）

``` bash
#!/bin/bash
rediscli="redis-cli"
logfile="/var/log/keepalived-redis-state.log"
date >> $logfile
echo "[backup]" >> $logfile
echo "等待13秒同步数据后运行下面命令" >> $logfile
sleep 13
echo "以远方IP为主机，同步数据" >> $logfile
$rediscli slaveof 172.20.22.53 6379 >> $logfile
echo "切换backup完成" >> $logfile
```

keepalived进入backup/stop/fault时的检测脚本，由于内容都一致，所以只写出redis_backup.sh

主从主机脚本内容一致，只需修改IP地址为对方IP

``` lsl
$rediscli slaveof 172.20.22.53 6379      #修改为对方IP
```


# 6 测试


# 7 注意事项：

1.  VRRP脚本(vrrp_script)和VRRP实例(vrrp_instance)属于同一个级别

2.  notify_master 、notify_backup、notify_fault、notify_stop参数

> `notify_stop`      keepalived停止运行前运行`notify_stop`指定的脚本
> `notify_master`  keepalived切换到master时执行的脚本 
> `notify_backup`  keepalived切换到backup时执行的脚本 
> `notify_fault`    keepalived出现故障时执行的脚本

3. 启动顺序，先启动redis,后启动keepalived

# 8 说明

此方法可以实现完全的自动化主从切换，但同步数据的时间（即脚本中的sleep时间）生产环境中无法完全掌控，实际使用中建议手动切回，**`或在主服务器上keepalived.conf中添加不抢占主机参数nopreempt（此参数要求配置文件中keepalived状态都为backup，根据优先级选择master）`**

示例：

``` dts
vrrp_instance VI_1 {
    state BACKUP
    interface eth0
    virtual_router_id 51i
    nopreempt                #redis或keepalived恢复后不抢占master，依然作为backup运行。
    priority 100
    advert_int 1
    authentication {
        auth_type PASS
        auth_pass 1111
    }
    track_script {
            chk_redis
    }
    virtual_ipaddress {
        172.20.22.199
    }
    notify_backup /etc/keepalived/scripts/redis_backup.sh
    notify_master /etc/keepalived/scripts/redis_master.sh
    notify_fault  /etc/keepalived/scripts/redis_fault.sh
}
```


