---
title: bitnami软件修改URL方法
tags:
  - bitnami
categories:
  - Linux
copyright: true
date: 2018-09-07 15:33:16
---

# 1 更改首页页面
<!--more-->
``` stata
install/apache2/conf/bitnami/bitnami.conf
```

修改`bitnami.con`文件，更改首页页面。

``` subunit
<VirtualHost _default_:80>
  DocumentRoot "/opt/mediawiki-1.26.2-2/apache2/htdocs"
  <Directory "/opt/mediawiki-1.26.2-2/apache2/htdocs">
   改为
<VirtualHost _default_:80>
  DocumentRoot "/opt/mediawiki-1.26.2-2/apps/mediawiki/htdocs"
  <Directory "/opt/mediawiki-1.26.2-2/apps/mediawiki/htdocs">
```

# 2 更改应用访问地址后缀

例如：http://172.20.20.37/moodle   改为http://172.20.20.37 

 

``` stata
Install/apps/moodle/conf/httpd-prefix.conf
```

修改`httpd-prefix.conf`文件，更改应用页面更目录

``` tex
Alias /moodle/ "C:\Bitnami\moodle-2.8.5-1/apps/moodle/htdocs/login/"
Alias /moodle "C:\Bitnami\moodle-2.8.5-1/apps/moodle/htdocs/login/"
 

改为

 

DocumentRoot "C:\Bitnami\moodle-2.8.5-1/apps/moodle/htdocs/login"   
#Alias /moodle/ "C:\Bitnami\moodle-2.8.5-1/apps/moodle/htdocs/login/"
#Alias /moodle "C:\Bitnami\moodle-2.8.5-1/apps/moodle/htdocs/login/"
```

 

# 3 更改应用根目录。

一般情况下，只需修改`bitnami.con`文件就可以达到URL后缀显示的问题，个别情况下需要修改`apps`下的`httpd-prefix.conf`文件。

还可以修改后缀名称。

例如：http://172.20.20.21/moodle     改为 http://172.20.20.21/mmkk 

也是修改`httpd-prefix.conf`文件。


# 4 修改端口号：参考上面80位置

``` stata
install/apache2/conf/bitnami/bitnami.conf
```

如果还不行，同时修改apache配置文件端口号。

``` stata
install/apache2/conf/httpd.conf
```

 

 

