---
title: Docker集群WEB管理工具Shipyard
tags:
  - shipyard
  - docker
categories:
  - Docker
copyright: true
date: 2018-08-22 17:00:58
---

# 一、 说明
<!--more-->
Shipyard部署总体较为简单，有一键部署脚本，只需执行相应命令就可以实现部署，但在部署中还是出现很多问题，主要是shipyard官方网站无法访问，无法使用官方一键脚本部署，使用网上找到的修改版，里面有部分内容有所缺失，现已修改。

# 二、环境

centos:7.4

master: 192.168.1.44

node1: 192.168.1.12

node2: 192.168.1.18

docker version: docker-ce-18.03.0-ce

# 三、安装步骤

安装之前需要部署好docker环境

## 1、master节点执行一件部署命令

``` shell
# 正常直接从官方拉取脚本执行就行了，命令如下
$ curl -s https://shipyard-project.com/deploy | bash -s

[root@master ~]# curl -s https://shipyard-project.com/deploy | bash -s
Deploying Shipyard
 -> Starting Database
Unable to find image 'rethinkdb:latest' locally
Trying to pull repository xxx.mirror.aliyuncs.com/rethinkdb ...
Pulling repository xxx.mirror.aliyuncs.com/rethinkdb
Trying to pull repository docker.io/library/rethinkdb ...
latest: Pulling from docker.io/library/rethinkdb
Digest: sha256:29640c7d5015832c40305ad5dcc5d0996ce79b87f7e32d2fd99c9d65ad9414d4
 -> Starting Discovery
 -> Starting Cert Volume
 -> Starting Proxy
 -> Starting Swarm Manager
 -> Starting Swarm Agent
 -> Starting Controller
Waiting for Shipyard on 192.168.1.44:8080
 
Shipyard available at http://192.168.1.44:8080
Username: admin Password: shipyard

# 或者下载脚本后本地执行，命令如下
$ sh deploy
```

执行脚本的时候会自动下载相关镜像，也可以事先下载镜像文件

``` crmsh
[root@master ~]# docker pull alpine
[root@master ~]# docker pull library/rethinkdb
[root@master ~]# docker pull microbox/etcd
[root@master ~]# docker pull shipyard/docker-proxy
[root@master ~]# docker pull swarm
[root@master ~]# docker pull shipyard/shipyard
```
通过访问http://IP：8080登录shipyard,默认帐号密码：admin   shipyard
![enter description here](1.png)

## 2、分别在node节点执行如下命令，添加节点到shipyard

``` crmsh
# 部署机就是master节点
$ curl -sSL https://shipyard-project.com/deploy | ACTION=node DISCOVERY=etcd://<shipyard部署机ip> bash -s
# 或者通过本地脚本执行命令
$ cat deploy | ACTION=node DISCOVERY=etcd://<shipyard部署机ip> bash -s
```
![enter description here](2.png)
![enter description here](3.png)
![enter description here](4.png)

# 四、问题总结

## 注意项目1：

—————————————————————————————————————
上面安装shipyard的脚本是英文版的，其实还有中文版的脚本，下面两种都可以使用：（两个地址都失效）

1）安装shipyard

``` shell
$ curl -sSL http://dockerclub.net/public/script/deploy | bash -s ==> 中文版
$ curl -sSL https://shipyard-project.com/deploy | bash -s ==> 英文版
```

2）添加node节点

``` shell
$ curl -sSL http://dockerclub.net/public/script/deploy | ACTION=node DISCOVERY=etcd://<shipyard部署机ip> bash -s ==> 中文版
$ curl -sSL https://shipyard-project.com/deploy | ACTION=node DISCOVERY=etcd://<shipyard部署机ip> bash -s ==> 英文版
```

3）删除shipyard（在节点机上执行，就会将节点从shipyard管理里踢出）

``` shell
$ curl http://dockerclub.net/public/script/deploy | ACTION=remove bash -s ==> 中文版
$ curl -sSL https://shipyard-project.com/deploy | ACTION=remove bash -s ==> 英文版
```

—————————————————————————————————————

问题项目2：
—————————————————————————————————————

1）安装shipyard前不需要部署swarm集群，一键包已包含集群建设

2）部署后无法发现节点，容器页面报错，意思是到节点IP:3375端口无法建立连接，500错误；根据排查，发现所有节点swarm_manager容器都没有开启3375端口，于是在脚本里面修改

容器启动命令，添加开启3375端口，具体看下方脚本；

3）在shipyard web页面，master自身发现较慢，不知道什么原因

4）中文版shipard创建容器的时候，设置端口映射但不生效，使用英文版没有问题，未发现问题原因

5）shipyard只适合较小规模docker集群，功能上已跟不上现阶段的docker集群需求。

—————————————————————————————————————

# deploy脚本

这个是中文版的脚本，和官方的区别就是修改了shipyard镜像文件，下方标注部分说明

``` bash
#!/bin/bash

if [ "$1" != "" ] && [ "$1" = "-h" ]; then
    echo "Shipyard Deploy uses the following environment variables:"
    echo "  ACTION: this is the action to use (deploy, upgrade, node, remove)"
    echo "  DISCOVERY: discovery system used by Swarm (only if using 'node' action)"
    echo "  IMAGE: this overrides the default Shipyard image"
    echo "  PREFIX: prefix for container names"
    echo "  SHIPYARD_ARGS: these are passed to the Shipyard controller container as controller args"
    echo "  TLS_CERT_PATH: path to certs to enable TLS for Shipyard"
    echo "  PORT: specify the listen port for the controller (default: 8080)"
    echo "  IP: specify the address at which the controller or node will be available (default: eth0 ip)"
    echo "  PROXY_PORT: port to run docker proxy (default: 2375)"
    exit 1
fi

if [ -z "`which docker`" ]; then
    echo "You must have the Docker CLI installed on your \$PATH"
    echo "  See http://docs.docker.com for details"
    exit 1
fi

ACTION=${ACTION:-deploy}
#官方IMAGE=${IMAGE:-shipyard/shipyard:latest}
#备注官方shipyard:latest标签镜像似乎有问题，实际使用shipyard:master标签镜像
IMAGE=${IMAGE:-dockerclub/shipyard:latest}
PREFIX=${PREFIX:-shipyard}
SHIPYARD_ARGS=${SHIPYARD_ARGS:-""}
TLS_CERT_PATH=${TLS_CERT_PATH:-}
CERT_PATH="/etc/shipyard"
PROXY_PORT=${PROXY_PORT:-2375}
SWARM_PORT=3375
SHIPYARD_PROTOCOL=http
SHIPYARD_PORT=${PORT:-8080}
SHIPYARD_IP=${IP}
DISCOVERY_BACKEND=etcd
DISCOVERY_PORT=4001
DISCOVERY_PEER_PORT=7001
ENABLE_TLS=0
CERT_FINGERPRINT=""
LOCAL_CA_CERT=""
LOCAL_SSL_CERT=""
LOCAL_SSL_KEY=""
LOCAL_SSL_CLIENT_CERT=""
LOCAL_SSL_CLIENT_KEY=""
SSL_CA_CERT=""
SSL_CERT=""
SSL_KEY=""
SSL_CLIENT_CERT=""
SSL_CLIENT_KEY=""

show_cert_help() {
    echo "To use TLS in Shipyard, you must have existing certificates."
    echo "The certs must be named ca.pem, server.pem, server-key.pem, cert.pem and key.pem"
    echo "If you need to generate certificates, see https://github.com/ehazlett/certm for examples."
}

check_certs() {
    if [ -z "$TLS_CERT_PATH" ]; then
        return
    fi

    if [ ! -e $TLS_CERT_PATH ]; then
        echo "Error: unable to find certificates in $TLS_CERT_PATH"
        show_cert_help
        exit 1
    fi

    if [ "$PROXY_PORT" = "2375" ]; then
        PROXY_PORT=2376
    fi
    SWARM_PORT=3376
    SHIPYARD_PROTOCOL=https
    LOCAL_SSL_CA_CERT="$TLS_CERT_PATH/ca.pem"
    LOCAL_SSL_CERT="$TLS_CERT_PATH/server.pem"
    LOCAL_SSL_KEY="$TLS_CERT_PATH/server-key.pem"
    LOCAL_SSL_CLIENT_CERT="$TLS_CERT_PATH/cert.pem"
    LOCAL_SSL_CLIENT_KEY="$TLS_CERT_PATH/key.pem"
    SSL_CA_CERT="$CERT_PATH/ca.pem"
    SSL_CERT="$CERT_PATH/server.pem"
    SSL_KEY="$CERT_PATH/server-key.pem"
    SSL_CLIENT_CERT="$CERT_PATH/cert.pem"
    SSL_CLIENT_KEY="$CERT_PATH/key.pem"
    CERT_FINGERPRINT=$(openssl x509 -noout -in $LOCAL_SSL_CERT -fingerprint -sha256 | awk -F= '{print $2;}')

    if [ ! -e $LOCAL_SSL_CA_CERT ] || [ ! -e $LOCAL_SSL_CERT ] || [ ! -e $LOCAL_SSL_KEY ] || [ ! -e $LOCAL_SSL_CLIENT_CERT ] || [ ! -e $LOCAL_SSL_CLIENT_KEY ]; then
        echo "Error: unable to find certificates"
        show_cert_help
        exit 1
    fi

    ENABLE_TLS=1
}

# container functions
start_certs() {
    ID=$(docker run \
        -ti \
        -d \
        --restart=always \
        --name $PREFIX-certs \
        -v $CERT_PATH \
        alpine \
        sh)
    if [ $ENABLE_TLS = 1 ]; then
        docker cp $LOCAL_SSL_CA_CERT $PREFIX-certs:$SSL_CA_CERT
        docker cp $LOCAL_SSL_CERT $PREFIX-certs:$SSL_CERT
        docker cp $LOCAL_SSL_KEY $PREFIX-certs:$SSL_KEY
        docker cp $LOCAL_SSL_CLIENT_CERT $PREFIX-certs:$SSL_CLIENT_CERT
        docker cp $LOCAL_SSL_CLIENT_KEY $PREFIX-certs:$SSL_CLIENT_KEY
    fi
}

remove_certs() {
    docker rm -fv $PREFIX-certs > /dev/null 2>&1
}

get_ip() {
    if [ -z "$SHIPYARD_IP" ]; then
        SHIPYARD_IP=`docker run --rm --net=host alpine ip route get 8.8.8.8 | awk '{ print $7;  }'`
    fi
}

start_discovery() {
    get_ip

    ID=$(docker run \
        -ti \
        -d \
        -p 4001:4001 \
        -p 7001:7001 \
        --restart=always \
        --name $PREFIX-discovery \
        microbox/etcd:latest -addr $SHIPYARD_IP:$DISCOVERY_PORT -peer-addr $SHIPYARD_IP:$DISCOVERY_PEER_PORT)
}

remove_discovery() {
    docker rm -fv $PREFIX-discovery > /dev/null 2>&1
}

start_rethinkdb() {
    ID=$(docker run \
        -ti \
        -d \
        --restart=always \
        --name $PREFIX-rethinkdb \
        rethinkdb)
}

remove_rethinkdb() {
    docker rm -fv $PREFIX-rethinkdb > /dev/null 2>&1
}

start_proxy() {
    TLS_OPTS=""
    if [ $ENABLE_TLS = 1 ]; then
        TLS_OPTS="-e SSL_CA=$SSL_CA_CERT -e SSL_CERT=$SSL_CERT -e SSL_KEY=$SSL_KEY -e SSL_SKIP_VERIFY=1"
    fi
    # Note: we add SSL_SKIP_VERIFY=1 to skip verification of the client
    # certificate in the proxy image.  this will pass it to swarm that
    # does verify.  this helps with performance and avoids certificate issues
    # when running through the proxy.  ultimately if the cert is invalid
    # swarm will fail to return.
    ID=$(docker run \
        -ti \
        -d \
        -p $PROXY_PORT:$PROXY_PORT \
        --hostname=$HOSTNAME \
        --restart=always \
        --name $PREFIX-proxy \
        -v /var/run/docker.sock:/var/run/docker.sock \
        -e PORT=$PROXY_PORT \
        --volumes-from=$PREFIX-certs $TLS_OPTS\
        shipyard/docker-proxy:latest)
}

remove_proxy() {
    docker rm -fv $PREFIX-proxy > /dev/null 2>&1
}

start_swarm_manager() {
    get_ip

    TLS_OPTS=""
    if [ $ENABLE_TLS = 1 ]; then
        TLS_OPTS="--tlsverify --tlscacert=$SSL_CA_CERT --tlscert=$SSL_CERT --tlskey=$SSL_KEY"
    fi

    EXTRA_RUN_OPTS=""

    if [ -z "$DISCOVERY" ]; then
        DISCOVERY="$DISCOVERY_BACKEND://discovery:$DISCOVERY_PORT"
        EXTRA_RUN_OPTS="--link $PREFIX-discovery:discovery"
    fi
    ID=$(docker run \
        -ti \
        -d \
#下面3375端口是我出现无法连接节点后自己添加的，问题是启动容器没有开放3375端口
        -p 3375:3375 \
        --restart=always \
        --name $PREFIX-swarm-manager \
        --volumes-from=$PREFIX-certs $EXTRA_RUN_OPTS \
        swarm:latest \
        m --replication --addr $SHIPYARD_IP:$SWARM_PORT --host tcp://0.0.0.0:$SWARM_PORT $TLS_OPTS $DISCOVERY)
}

remove_swarm_manager() {
    docker rm -fv $PREFIX-swarm-manager > /dev/null 2>&1
}

start_swarm_agent() {
    get_ip

    if [ -z "$DISCOVERY" ]; then
        DISCOVERY="$DISCOVERY_BACKEND://discovery:$DISCOVERY_PORT"
        EXTRA_RUN_OPTS="--link $PREFIX-discovery:discovery"
    fi
    ID=$(docker run \
        -ti \
        -d \
        --restart=always \
        --name $PREFIX-swarm-agent $EXTRA_RUN_OPTS \
        swarm:latest \
        j --addr $SHIPYARD_IP:$PROXY_PORT $DISCOVERY)
}

remove_swarm_agent() {
    docker rm -fv $PREFIX-swarm-agent > /dev/null 2>&1
}

start_controller() {
    #-v $CERT_PATH:/etc/docker:ro \
    TLS_OPTS=""
    if [ $ENABLE_TLS = 1 ]; then
        TLS_OPTS="--tls-ca-cert $SSL_CA_CERT --tls-cert=$SSL_CERT --tls-key=$SSL_KEY --shipyard-tls-ca-cert=$SSL_CA_CERT --shipyard-tls-cert=$SSL_CERT --shipyard-tls-key=$SSL_KEY"
    fi

    ID=$(docker run \
        -ti \
        -d \
        --restart=always \
        --name $PREFIX-controller \
        --link $PREFIX-rethinkdb:rethinkdb \
        --link $PREFIX-swarm-manager:swarm \
        -p $SHIPYARD_PORT:$SHIPYARD_PORT \
        --volumes-from=$PREFIX-certs \
        $IMAGE \
        --debug \
        server \
        --listen :$SHIPYARD_PORT \
        -d tcp://swarm:$SWARM_PORT $TLS_OPTS $SHIPYARD_ARGS)
}

wait_for_available() {
    set +e 
    IP=$1
    PORT=$2
    echo Waiting for Shipyard on $IP:$PORT

    docker pull ehazlett/curl > /dev/null 2>&1

    TLS_OPTS=""
    if [ $ENABLE_TLS = 1 ]; then
        TLS_OPTS="-k"
    fi

    until $(docker run --rm ehazlett/curl --output /dev/null --connect-timeout 1 --silent --head --fail $TLS_OPTS $SHIPYARD_PROTOCOL://$IP:$PORT/ > /dev/null 2>&1); do
        printf '.'
        sleep 1 
    done
    printf '\n'
}

remove_controller() {
    docker rm -fv $PREFIX-controller > /dev/null 2>&1
}

if [ "$ACTION" = "deploy" ]; then
    set -e

    check_certs

    get_ip 

    echo "Deploying Shipyard"
    echo " -> Starting Database"
    start_rethinkdb
    echo " -> Starting Discovery"
    start_discovery
    echo " -> Starting Cert Volume"
    start_certs
    echo " -> Starting Proxy"
    start_proxy
    echo " -> Starting Swarm Manager"
    start_swarm_manager
    echo " -> Starting Swarm Agent"
    start_swarm_agent
    echo " -> Starting Controller"
    start_controller

    wait_for_available $SHIPYARD_IP $SHIPYARD_PORT

    echo "Shipyard available at $SHIPYARD_PROTOCOL://$SHIPYARD_IP:$SHIPYARD_PORT"
    if [ $ENABLE_TLS = 1 ] && [ ! -z "$CERT_FINGERPRINT" ]; then
        echo "SSL SHA-256 Fingerprint: $CERT_FINGERPRINT"
    fi
    echo "Username: admin Password: shipyard"

elif [ "$ACTION" = "node" ]; then
    set -e

    if [ -z "$DISCOVERY" ]; then
        echo "You must set the DISCOVERY environment variable"
        echo "with the discovery system used with Swarm"
        exit 1
    fi

    check_certs

    echo "Adding Node"
    echo " -> Starting Cert Volume"
    start_certs
    echo " -> Starting Proxy"
    start_proxy
    echo " -> Starting Swarm Manager"
    start_swarm_manager $DISCOVERY
    echo " -> Starting Swarm Agent"
    start_swarm_agent

    echo "Node added to Swarm: $SHIPYARD_IP"
    
elif [ "$ACTION" = "upgrade" ]; then
    set -e

    check_certs

    get_ip

    echo "Upgrading Shipyard"
    echo " -> Pulling $IMAGE"
    docker pull $IMAGE

    echo " -> Upgrading Controller"
    remove_controller
    start_controller

    wait_for_available $SHIPYARD_IP $SHIPYARD_PORT

    echo "Shipyard controller updated"

elif [ "$ACTION" = "remove" ]; then
    # ignore errors
    set +e

    echo "Removing Shipyard"
    echo " -> Removing Database"
    remove_rethinkdb
    echo " -> Removing Discovery"
    remove_discovery
    echo " -> Removing Cert Volume"
    remove_certs
    echo " -> Removing Proxy"
    remove_proxy
    echo " -> Removing Swarm Agent"
    remove_swarm_agent
    echo " -> Removing Swarm Manager"
    remove_swarm_manager
    echo " -> Removing Controller"
    remove_controller

    echo "Done"
else
    echo "Unknown action $ACTION"
    exit 1
fi
```

# 参考资料

https://www.cnblogs.com/kevingrace/p/6867820.html

https://www.fcwys.cc/index.php/archives/145.html