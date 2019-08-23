---
title: Docker容器的重启策略及--restart选项详解
tags:
  - docker
categories:
  - Docker
copyright: true
date: 2019-05-10 11:26:58
---
创建容器时没有添加参数  --restart=always ，导致的后果是：当 Docker 重启时，容器未能自动启动。

现在要添加该参数怎么办呢，方法有二：
<!--more-->

# 1 重启策略及--restart选项详解

## 1. Docker容器的重启策略

Docker容器的重启策略是面向生产环境的一个启动策略，在开发过程中可以忽略该策略。

Docker容器的重启都是由Docker守护进程完成的，因此与守护进程息息相关。


**Docker容器的重启策略如下：**
 - `no`，默认策略，在容器退出时不重启容器
 - `on-failure`，在容器非正常退出时（退出状态非0），才会重启容器
      - `on-failure:3`，在容器非正常退出时重启容器，最多重启3次
 - `always`，在容器退出时总是重启容
 - `unless-stopped`，在容器退出时总是重启容器，但是不考虑在Docker守护进程启动时就已经停止了的容器


 

## 2. Docker容器的退出状态码

**`docker run`的退出状态码如下：**
 - `0`，表示正常退出
 - `非0`，表示异常退出（退出状态码采用chroot标准）
    - 125，Docker守护进程本身的错误
    - 126，容器启动后，要执行的默认命令无法调用
    - 127，容器启动后，要执行的默认命令不存在
    - 其他命令状态码，容器启动后正常执行命令，退出命令时该命令的返回状态码作为容器的退出状态码

## 3. docker run的--restart选项

通过`--restart`选项，可以设置容器的重启策略，以决定在容器退出时Docker守护进程是否重启刚刚退出的容器。
`--restart`选项通常只用于`detached模式`的容器。

`--restart`选项不能与`--rm`选项同时使用。显然，`-restart`选项适用于`detached模式`的容器，而`--rm`选项适用于`foreground`模式的容器。

在`docker ps`查看容器时，对于使用了`--restart`选项的容器，其可能的状态只有`Up`或`Restarting`两种状态。

**示例：**

``` bash
docker run -d --restart=always bba-208
docker run -d --restart=on-failure:10 bba-208
```


**补充：**

查看容器重启次数

``` bash
docker inspect -f "{{ .RestartCount }}" bba-208
```

查看容器最后一次的启动时间

``` bash
docker inspect -f "{{ .State.StartedAt }}" bba-208
```

# 2、Docker 命令修改

``` bash
docker container update --restart=always 容器名字
```


``` bash
操作实例如下：
[root@localhost mnt]# docker ps -a
CONTAINER ID        IMAGE               COMMAND                  CREATED              STATUS              PORTS               NAMES
46cdfc60b7a6        nginx               "nginx -g 'daemon ..."   About a minute ago   Up 42 seconds       80/tcp              n3
79d55a734c26        nginx               "nginx -g 'daemon ..."   About a minute ago   Up 42 seconds       80/tcp              n2
f7b2206c019d        nginx               "nginx -g 'daemon ..."   About a minute ago   Up 46 seconds       80/tcp              n1
[root@localhost mnt]# docker container update --restart=always n1
n1
[root@localhost mnt]# systemctl restart docker 
[root@localhost mnt]# docker ps -a
CONTAINER ID        IMAGE               COMMAND                  CREATED             STATUS                     PORTS               NAMES
46cdfc60b7a6        nginx               "nginx -g 'daemon ..."   2 minutes ago       Exited (0) 5 seconds ago                       n3
79d55a734c26        nginx               "nginx -g 'daemon ..."   2 minutes ago       Exited (0) 5 seconds ago                       n2
f7b2206c019d        nginx               "nginx -g 'daemon ..."   2 minutes ago       Up 2 seconds               80/tcp              n1
```

# 3、直接改配置文件
**`（经测试后无效，修改配置文件后，启动容器后，该参数有自动变成了no，修改不生效）`**

{%note success %}
首先停止容器，不然无法修改配置文件
配置文件路径为：`/var/lib/docker/containers/容器ID`
在该目录下找到一个文件 `hostconfig.json `，找到该文件中关键字 `RestartPolicy`
修改前配置：`"RestartPolicy":{"Name":"no","MaximumRetryCount":0}`
修改后配置：`"RestartPolicy":{"Name":"always","MaximumRetryCount":0}`
最后启动容器。
{%endnote%}


----------

# 4 修改docker容器的挂载路径

 - 停止所有docker容器
 

``` bash
sudo docker stop $(docker ps -a | awk '{ print $1}' | tail -n +2)
```

 - 停止docker服务
 

``` bash
sudo service docker stop
```

 - 修改mysql路径
 

``` bash
cd ~
sudo cp -r mysql/ /home/server/
```

 - 备份容器配置文件
 

``` bash
cd /var/lib/docker/containers/de9c6501cdd3
cp hostconfig.json hostconfig.json.bak
cp config.v2.json config.v2.json.bak
```

 - 修改hostconfig的冒号前的配置路径
 

``` bash
vi hostconfig.json

"Binds": ["/home/server/mysql/conf/my.cnf:/etc/mysql/my.cnf", "/home/server/mysql/logs:/logs", "/home/server/mysql/data:/mysql_data"],
```

 - 修改config的Source的配置路径
 

``` bash
vi config.v2.json

       "MountPoints": {

              "/etc/mysql/my.cnf": {

                     "Source": "/home/server/mysql/conf/my.cnf",

                     "Destination": "/etc/mysql/my.cnf",

                     "RW": true,

                     "Name": "",

                     "Driver": "",

                     "Relabel": "",

                     "Propagation": "rprivate",

                     "Named": false,

                     "ID": ""

              },

              "/logs": {

                     "Source": "/home/server/mysql/logs",

                     "Destination": "/logs",

                     "RW": true,

                     "Name": "",

                     "Driver": "",

                     "Relabel": "",

                     "Propagation": "rprivate",

                     "Named": false,

                     "ID": ""

              },

              "/mysql_data": {

                     "Source": "/home/server/mysql/data",

                     "Destination": "/mysql_data",

                     "RW": true,

                     "Name": "",

                     "Driver": "",

                     "Relabel": "",

                     "Propagation": "rprivate",

                     "Named": false,

                     "ID": ""

              },

              "/var/lib/mysql": {

                     "Source": "",

                     "Destination": "/var/lib/mysql",

                     "RW": true,

                     "Name": "85d91bff7012b57606af819480ce267449084e81ab386737c80ace9fe75f6621",

                     "Driver": "local",

                     "Relabel": "",

                     "Propagation": "",

                     "Named": false,

                     "ID": "897cd0152dd152166cb2715044ca4a3915a1b66280e0eb096eb74c2d737d7f77"

              }

       },
```


----------

# 5 修改docker默认的存储位置
docker 的所有images及相关信息存储位置为：`/var/lib/docker`

 - 查看默认的docker存储路径
 

``` bash
docker info |grep 'Docker Root Dir'
WARNING: No swap limit support
Docker Root Dir: /var/lib/docker
```

 - 停止所有docker容器

``` bash
sudo docker stop $(docker ps -a | awk '{ print $1}' | tail -n +2)
```

 - 停止docker服务

``` bash
sudo service docker stop
cd /var/lib
```

 - 打包docker目录

``` bash
sudo tar -czvf /usr/docker.tar.gz docker/
cd /usr/
sudo tar -xzvf docker.tar.gz
```

 - 修改docker默认的存储位置

``` bash
sudo vim /etc/docker/daemon.json

{
    "graph": "/home/server/docker"
}
```

 - 启动docker服务

``` bash
sudo service docker start
```

 - 启动所有docker容器

``` bash
sudo docker start $(docker ps -a | awk '{ print $1}' | tail -n +2)
```

 - 查看修改后docker存储路径
 

``` bash
docker info |grep 'Docker Root Dir'
WARNING: No swap limit support
Docker Root Dir: /usr/docker

```
本文转自：https://www.cnblogs.com/zhuochong/p/10070516.html ！！！！！！