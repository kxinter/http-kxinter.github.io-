---
title: proxy_pass反向代理配置中url后面加不加/的说明
tags:
  - nginx
categories:
  - Linux
date: 2018-08-23 17:28:53
---

# 1 环境
<!--more-->
OS:centos7

nginx _proxy服务器：192.168.1.23

web服务器：192.168.1.5

# 2 情况说明

## 2.1 path路径后面加”/”

### 2.1.1 情况一

NGINX配置

``` bash?linenums
[root@localhost conf.d]# cat test.conf
server {
listen 80;
server_name localhost;
location / {
root /var/www/html;
index index.html;
}
 
location  /proxy/ {
          proxy_pass http://192.168.1.5:8090/;
		  }
}
```
这样，访问http://192.168.1.23/proxy/就会被代理到http://192.168.1.5:8090/。匹配的proxy目录不需要存在根目录/var/www/html里面

> 注意，终端里如果访问http://192.168.1.23/proxy（即后面不带”/”），则会访问失败！因为proxy_pass配置的url后面加了”/”

访问结果如下

``` dts
[root@localhost conf.d]# curl http://192.168.1.23/proxy/
this is 192.168.1.5
[root@localhost conf.d]# curl http://192.168.1.23/proxy
<html>
<head><title>301 Moved Permanently</title></head>
<body bgcolor="white">
<center><h1>301 Moved Permanently</h1></center>
<hr><center>nginx/1.10.3</center>
</body>
</html>
```
页面访问http://103.110.186.23/proxy的时候，会自动加上”/”（同理是由于proxy_pass配置的url后面加了”/”），并反代到http://103.110.186.5:8090的结果。
![enter description here](1.png)

### 2.1.2 情况二

``` crmsh
[root@localhost conf.d]# cat test.conf
server {
listen 80;
server_name localhost;
location / {
root /var/www/html;
index index.html;
}
 
location  /proxy/ {
          proxy_pass http://192.168.1.5:8090;
}
}

[root@localhost conf.d]# service nginx restart
Redirecting to /bin/systemctl restart  nginx.service
## 那么访问http://192.168.1.23/proxy或http://192.168.1.23/proxy/，都会失败！
## 这样配置后，访问http://192.168.1.23/proxy/就会被反向代理到http://192.168.1.5:8090/proxy/
```
![enter description here](2.png)

### 2.1.3 情况三

``` stata
[root@localhost conf.d]# cat test.conf
server {
listen 80;
server_name localhost;
location / {
root /var/www/html;
index index.html;
}
 
location  /proxy/ {
          proxy_pass http://192.168.1.5:8090/haha/;
}
}
[root@localhost conf.d]# service nginx restart
Redirecting to /bin/systemctl restart  nginx.service
[root@localhost conf.d]# curl http://192.168.1.23/proxy/
192.168.1.5  haha-index.html
```
这样配置的话，访问http://103.110.186.23/proxy代理到http://192.168.1.5:8090/haha/
![enter description here](3.png)


### 2.1.4 情况四

相对于第三种配置的url不加”/”

``` clean
[root@localhost conf.d]# cat test.conf
server {
listen 80;
server_name localhost;
location / {
root /var/www/html;
index index.html;
}
 
location  /proxy/ {
          proxy_pass http://192.168.1.5:8090/haha;
}
}
[root@localhost conf.d]# service nginx restart
Redirecting to /bin/systemctl restart  nginx.service
[root@localhost conf.d]# curl http://192.168.1.23/proxy/index.html
192.168.1.5   hahaindex.html

##################################### 
上面配置后，访问http://192.168.1.23/proxy/index.html就会被代理到http://192.168.1.5:8090/hahaindex.html
同理，访问http://192.168.1.23/proxy/test.html就会被代理到http://192.168.1.5:8090/hahatest.html
[root@localhost conf.d]# curl http://192.168.1.23/proxy/index.html
192.168.1.5   hahaindex.html
```

> 注意，这种情况下，不能直接访问http://192.168.1.23/proxy/，后面就算是默认的index.html文件也要跟上，否则访问失败！
![enter description here](4.png)

———————————————————————————————————————————
上面四种方式都是匹配的path路径后面加”/”，下面说下path路径后面不带”/”的情况：

## 2.2 path路径后面不加”/”

### 2.2.1 情况一

proxy_pass后面url带”/”：

``` crmsh
[root@localhost conf.d]# cat test.conf
server {
listen 80;
server_name localhost;
location / {
root /var/www/html;
index index.html;
}
  
location  /proxy {
          proxy_pass http://192.168.1.5:8090/;
}
}
[root@localhost conf.d]# service nginx restart
Redirecting to /bin/systemctl restart  nginx.service
```
![enter description here](5.png)
### 2.2.2 情况二，

proxy_pass后面url不带”/”

``` crmsh
[root@localhost conf.d]# cat test.conf
server {
listen 80;
server_name localhost;
location / {
root /var/www/html;
index index.html;
}
  
location  /proxy {
          proxy_pass http://192.168.1.5:8090;
}
}
[root@localhost conf.d]# service nginx restart
Redirecting to /bin/systemctl restart  nginx.service
[root@localhost conf.d]#
```
这样配置的话，访问http://103.110.186.23/proxy会自动加上”/”（即变成http://103.110.186.23/proxy/），代理到192.168.1.5:8090/proxy/
![enter description here](7.png)

### 2.2.3 情况三

``` crmsh
[root@localhost conf.d]# cat test.conf
server {
listen 80;
server_name localhost;
location / {
root /var/www/html;
index index.html;
}
  
location  /proxy {
          proxy_pass http://192.168.1.5:8090/haha/;
}
}
[root@localhost conf.d]# service nginx restart
Redirecting to /bin/systemctl restart  nginx.service
```
这样配置的话，访问http://103.110.186.23/proxy会自动加上”/”（即变成http://103.110.186.23/proxy/），代理到http://192.168.1.5:8090/haha/
![enter description here](8.png)

### 2.2.4 情况四

相对于第三种配置的url不加”/”

``` crmsh
[root@localhost conf.d]# cat test.conf
server {
listen 80;
server_name localhost;
location / {
root /var/www/html;
index index.html;
}
  
location  /proxy {
          proxy_pass http://192.168.1.5:8090/haha;
}
}
[root@localhost conf.d]# service nginx restart
Redirecting to /bin/systemctl restart  nginx.service
```
这样配置的话，访问http://103.110.186.23/proxy，和第三种结果一样，同样被代理到http://192.168.1.5:8090/haha/
![enter description here](9.png)
