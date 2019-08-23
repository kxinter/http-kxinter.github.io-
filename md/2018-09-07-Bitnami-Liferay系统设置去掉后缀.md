---
title: Bitnami_Liferay系统设置去掉后缀
tags:
  - liferay
  - bitnami
categories:
  - Linux
copyright: true
date: 2018-09-07 14:26:26
---

# 1 修改配置文件
<!--more-->
执行以下操作：

``` groovy
mv /opt/liferay-6.2-7/apache-tomcat/webapps/ROOT/ /opt/liferay-6.2-7/apache-tomcat/webapps/ROOT.backup

mv /opt/liferay-6.2-7/apache-tomcat/webapps/liferay /opt/liferay-6.2-7/apache-tomcat/webapps/ROOT

sed -i 's/portal.ctx/#portal.ctx/g'  /opt/liferay-6.2-7/apache-tomcat/webapps/ROOT/WEB-INF/classes/portal-ext.properties
```

 

打开`/opt/liferay-6.2-7/apps/liferay/conf/httpd-app.conf`文件做如下修改：

``` dts
将<Location /liferay>

  ProxyPass ajp://localhost:8009/liferay

  <IfModule pagespeed_module>

      ModPagespeedDisallow "*"

  </IfModule>

</Location>

 

改为：

<Location />

  ProxyPass ajp://localhost:8009/

  <IfModule pagespeed_module>

      ModPagespeedDisallow "*"

  </IfModule>

</Location>

 

并且在最后加上：

# App url redirect

RewriteEngine On

RedirectMatch ^/$ /
```

#  2 修改数据库

访问bitnami_liferay数据库，找到journalarticle表，用：

``` sql
update journalarticle set content=REPLACE (content,'/liferay/document','/document')
```

对表中`content`字段的记录进行批量替换

 

  

> 最后手工修改“规章制度”和“文档模板”的链接
![enter description here](1.png)

现在访问http://172.20.20.58已经可以正常显示了 

参考：https://wiki.bitnami.com/Applications/BitNami_Liferay#Manual_Approach 

 

