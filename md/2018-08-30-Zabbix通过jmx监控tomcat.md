---
title: Zabbix通过jmx监控tomcat
tags:
  - zabbix
  - tomcat
  - jmx
categories:
  - Linux
date: 2018-08-30 17:09:11
---

# 1 环境
<!--more-->
|  名称   |  IP   |
| --- | --- |
|   zabbix server  |   172.20.20.22  |
|   tomcat server  |  172.20.20.111   |


# 2 服务端安装

## 2.1 安装zabbix_java_Gateway

这里直接安装zabbix_java_gateway到zabbix server上面

``` awk
rpm -ivh http://repo.zabbix.com/zabbix/3.0/rhel/7/x86_64/zabbix-java-gateway-3.0.5-1.el7.x86_64.rpm
```

## 2.2 修改配置文件zabbix_java-gateway.

修改zabbix_java_gateway.conf

``` makefile
LISTEN_IP="0.0.0.0"
LISTEN_PORT=10052
PID_FILE="/tmp/zabbix_java.pid"
START_POLLERS=5
```


## 2.3 修改zabbix_server.conf

添加如下几行

JavaGateway=127.0.0.1            //zabbix_server与zabbix_java_gateway在一台服务器上，这里指定java_gateway服务器地址为本机；
JavaGatewayPort=10052
StartJavaPollers=5


## 2.4 重启zabbix_server

``` elixir
[root@zabbixserver ~]# service zabbix-server restart
```

# 3 tomcat客户端配置

添加如下代码到tomcat目录/bin/catalina.sh

``` haml
CATALINA_OPTS="-Djava.rmi.server.hostname=172.20.20.111                   //tomcat客户端ip地址
-Djavax.management.builder.initial=
-Dcom.sun.management.jmxremote=true
-Dcom.sun.management.jmxremote.ssl=false
-Dcom.sun.management.jmxremote.authenticate=false"
```


## 3.1 下载catalina-jmx-remote.jar

因为tomcat服务器安装的java版本是1.7，所以这里下载的jar包是1.7的版本，不同版本的tomcat对应不同版本的catalina-jmx-remote.jar；

在`http://tomcat.apache.org/download-70.cgi`  找到以下JMX Remote jar,把这个文件放到tomcat安装目录的lib子目录下

 - Extras:

    - JMX Remote jar (pgp, md5, sha1)            //下载jmx包
    - Web services jar (pgp, md5, sha1)
    -  JULI adapters jar (pgp, md5, sha1)
    - JULI log4j jar (pgp, md5, sha1)

## 3.2 修改tomcat安装目录conf子目录下的server.xml配置文件

添加如下几行

``` xml
<Listener className="org.apache.catalina.mbeans.JmxRemoteLifecycleListener"  
          rmiRegistryPortPlatform="12345" rmiServerPortPlatform="12346" />
```

完整显示：

``` xml
<Server port="8005" shutdown="SHUTDOWN">
  <Listener className="org.apache.catalina.startup.VersionLoggerListener" />
  <!-- Security listener. Documentation at /docs/config/listeners.html
  <Listener className="org.apache.catalina.security.SecurityListener" />
  -->
  <!--APR library loader. Documentation at /docs/apr.html -->
  <Listener className="org.apache.catalina.core.AprLifecycleListener" SSLEngine="on" />
  <!--Initialize Jasper prior to webapps are loaded. Documentation at /docs/jasper-howto.html -->
  <Listener className="org.apache.catalina.core.JasperListener" />
  <!-- Prevent memory leaks due to use of particular java/javax APIs-->
  <Listener className="org.apache.catalina.core.JreMemoryLeakPreventionListener" />
  <Listener className="org.apache.catalina.mbeans.GlobalResourcesLifecycleListener" />
  <Listener className="org.apache.catalina.core.ThreadLocalLeakPreventionListener" />
  <Listener className="org.apache.catalina.mbeans.JmxRemoteLifecycleListener"
          rmiRegistryPortPlatform="12345" rmiServerPortPlatform="12346" />
省略...
```


## 3.3 重启tomcat.

``` lsl
[root@localhost apache-tomcat-7.0.69]# /opt/tomcat/bin/shutdown.sh 

[root@localhost apache-tomcat-7.0.69]# /opt/tomcat/bin/startup.sh
```

测试是否可以获得数据

测试需要cmdline-jmxclient-0.10.3.jar包，下载包 http://dl.bintray.com/typesafe/maven-releases/cmdline-jmxclient/cmdline-jmxclient/0.10.3/cmdline-jmxclient-0.10.3.jar     

``` x86asm
cd /home

wget http://dl.bintray.com/typesafe/maven-releases/cmdline-jmxclient/cmdline-jmxclient/0.10.3/cmdline-jmxclient-0.10.3.jar

java -jar /home/cmdline-jmxclient-0.10.3.jar - 127.0.0.1:12345 java.lang:type=Memory NonHeapMemoryUsage
```
![enter description here](1.png)


如上图显示，说明可以正常获得数据。

## 3.4 配置防火墙

开放12345/12346端口
![enter description here](2.png)




到这里配置完成。



**参考资料：**

http://jaychang.iteye.com/blog/2214830





# 4 问题：

按照网上的教程，修改tomcat目录中的catalina.sh ，无法再关闭防火墙的前提下正常获取到数据，是因为即使按照配置设定了端口，但实际中并不是只使用设置的端口。

# 5 配置例子：

> （关闭防火墙开启12345端口就无法获取数据）

``` haml
CATALINA_OPTS="-Dcom.sun.management.jmxremote
-Dcom.sun.management.jmxremote.authenticate=false
-Dcom.sun.management.jmxremote.ssl=false
-Dcom.sun.management.jmxremote.port=12345  #定义jmx监听端口
-Djava.rmi.server.hostname=客户端IP"
```




 

