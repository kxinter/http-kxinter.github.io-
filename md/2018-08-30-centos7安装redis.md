---
title: centos7安装redis
tags:
  - redis
  - 部署
categories:
  - Linux
date: 2018-08-30 16:45:26
---

# 1 下载redis

下载redis-3.2.9.tar.gz

``` stylus
wget http://download.redis.io/releases/redis-3.2.9.tar.gz

tar -zxvf redis-3.2.9.tar.gz

mv redis-3.2.9 redis
```

# 2 安装redis

``` elixir
[root@bogon home]# cd redis/

[root@bogon redis]# make && make install
```
![enter description here](1.png)


## 2.1 初始化redis

``` elixir
[root@bogon redis]# cd utils/

[root@bogon utils]# ./install_server.sh
```
![enter description here](2.png)



> 通过上图，我们可以看出`redis`初始化后`redis`配置文件为`/etc/redis/6379.conf`，日志文件为`/var/log/redis_6379.log`，数据文件`dump.rdb`存放到`/var/lib/redis/6379`目录下，启动脚本为`/etc/init.d/redis_6379`。

现在我们要使用` systemd`，所以在 `/etc/systems/system` 下创建一个单位文件名字为` redis_6379.service`。

``` groovy
vim /etc/systemd/system/redis_6379.service
```

填写以下内容：

``` ini
[Unit]
Description=Redis on port 6379
[Service]
Type=forking
ExecStart=/etc/init.d/redis_6379 start
ExecStop=/etc/init.d/redis_6379 stop
[Install]
WantedBy=multi-user.target
```


## 2.2 查看redis版本

``` stata
redis-cli --version
```
![enter description here](3.png)

# 3 参考资料：

http://www.cnblogs.com/sandea/p/5782192.html
