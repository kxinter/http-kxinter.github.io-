---
title: Mediawiki安装及LDAP认证问题
tags:
  - Mediawiki
  - wiki
categories:
  - Linux
copyright: true
date: 2018-09-07 14:41:01
---

# 1 环境
<!--more-->
安装环境：CentOS-7-x86_64-DVD-1511

Mediawiki: bitnami-mediawiki-1.26.2-2-linux-x64-installer.run

LDAP扩展插件：LdapAuthentication-REL1_26-70ab129.tar.gz

# 2 安装mediawiki


首先安装`bitnami-mediawiki-1.26.2-2-linux-x64-installer.run`

``` lsl
#chmod   755 bitnami-mediawiki-1.26.2-2-linux-x64-installer.run   //赋予读写权限

#./bitnami-mediawiki-1.26.2-2-linux-x64-installer.run           //执行安装
```



**安装到最后出现mysql数据库错误**：

``` subunit
Error: Error running /opt/mediawiki-1.26.2-2/mysql/scripts/myscript.sh

/opt/mediawiki-1.26.2-2/mysql ****: FATAL ERROR: please install the following

Perl modules before executing scripts/mysql_install_db:

Data::Dumper


ERROR 2002 (HY000): Can't connect to local MySQL server through socket

'/opt/mediawiki-1.26.2-2/mysql/tmp/mysql.sock' (2)

ERROR 2002 (HY000): Can't connect to local MySQL server through socket

'/opt/mediawiki-1.26.2-2/mysql/tmp/mysql.sock' (2)

ERROR 2002 (HY000): Can't connect to local MySQL server through socket

'/opt/mediawiki-1.26.2-2/mysql/tmp/mysql.sock' (2)
```

（根据提示，发现系统缺少Dumper模块）

根据提示安装Data-Dumper.x86_64

``` gcode
# yum install perl-Data-Dumper.x86_64          //安装插件模块。
```

……………

OK,  Mediawiki安装成功。

# 3 开启AD域用户认证登录

Ldap认证需要php支持ldap,需要安装ldap支持模块（`php-ldap`），及开启`php`的`ldap`功能(修改`php.ini`文件)。

	> 备注：不安装php-ldap，LdapAuthentication插件不工作

1、  安装php-ldap模块：

``` elixir
[root@localhost mediawiki]# yum   install php-ldap
```

 2、 开启`ldap`功能
即修改`php.ini`文件，将`extension=php_ldap.dll`前的分号去掉。

``` lsl
[root@localhost mediawiki]# vi   /opt/mediawiki-1.26.2-2/php/etc/php.ini
```
![enter description here](1.png)


3、下载`LdapAuthentication`插件：`LdapAuthentication-REL1_26-70ab129.tar.gz`

解压插件到extensions目录：

``` lsl
# tar -xzf   LdapAuthentication-REL1_26-70ab129.tar.gz   /opt/mediawiki-1.26.2-2/apps/mediawiki/htdocs/extensions/
```

 

4、编辑`LocalSettings.php`配置文件
![enter description here](2.png)


在`LocalSettings.php` 末尾添加如下内容：

``` php
require_once("extensions/LdapAuthentication/LdapAuthentication.php");

$wgAuth= new LdapAuthenticationPlugin(); ## 这两行激活插件



$wgLDAPDomainNames = array( "dealeasy"   );    //域名简写

$wgLDAPServerNames = array(   "dealeasy"=>"172.20.20.10" );     //域控域名或者ip

$wgLDAPSearchStrings = array(   "dealeasy"=>"USER-NAME@dealeasy" );     //USER-NAME 不要修改它,默认用户名替代位置，特定字符



$wgLDAPBaseDNs = array(   "dealeasy"=>"dc=dealeasy,dc=local");

$wgLDAPSearchAttributes = array(   "dealeasy"=>"sAMAccountName");    //加上这两句就可以把DC上的用户名都同步过来了



$wgLDAPUseLocal = false;       是否使用本地用户,ture代表使用，这里写入不使用

$wgLDAPUpdateLDAP = false;

$wgLDAPMailPassword = false;



$wgMinimalPasswordLength = 1;

$wgLDAPEncryptionType =   array("dealeasy"=>"clear");



$wgShowSQLErrors = true;

$wgDebugDumpSql = true;

$wgShowDBErrorBacktrace = true;          //这三行网上找到，因ldap用户登录出现数据库查询错误，添加这三行后，在出现错误时可以在页面上显示错误信息
```
![enter description here](3.png)



Ok, `LocalSettings.php`编辑完成。

 

下面就可以直接使用域用户登录了。

# 4 Database错误
![enter description here](4.png)

报错（前面`LocalSettings.php`添加后三行才能看到报错详情）：

**Database error**
![enter description here](5.png)
``` stata
A database query error has occurred. This may indicate a bug in the software.

（翻译：数据库错误　　　　一个数据库查询错误发生。这可能表明软件中的缺陷。）


Query:

SELECT domain FROM `ldap_domains` WHERE user_id = '4' LIMIT 1

Function: LdapAuthenticationPlugin::loadDomain

Error: 1146 Table 'bitnami_mediawiki.ldap_domains' doesn't exist (localhost:3306)

Backtrace:

#0 /opt/mediawiki-1.26.2-2/apps/mediawiki/htdocs/includes/db/Database.php(1076): DatabaseBase->reportQueryError('Table 'bitnami_...', 1146, 'SELECT  domain ...', 'LdapAuthenticat...', false)

#1 /opt/mediawiki-1.26.2-2/apps/mediawiki/htdocs/includes/db/Database.php(1600): DatabaseBase->query('SELECT  domain ...', 'LdapAuthenticat...')

#2 /opt/mediawiki-1.26.2-2/apps/mediawiki/htdocs/includes/db/Database.php(1689): DatabaseBase->select('ldap_domains', Array, Array, 'LdapAuthenticat...', Array, Array)

#3 /opt/mediawiki-1.26.2-2/apps/mediawiki/htdocs/extensions/LdapAuthentication/LdapAuthentication.php(2041): DatabaseBase->selectRow('ldap_domains', Array, Array, 'LdapAuthenticat...')

#4 /opt/mediawiki-1.26.2-2/apps/mediawiki/htdocs/extensions/LdapAuthentication/LdapAuthentication.php(2060): LdapAuthenticationPlugin::loadDomain(Object(User))

#5 /opt/mediawiki-1.26.2-2/apps/mediawiki/htdocs/extensions/LdapAuthentication/LdapAuthentication.php(1237): LdapAuthenticationPlugin::saveDomain(Object(User), 'dealeasy')

#6 /opt/mediawiki-1.26.2-2/apps/mediawiki/htdocs/includes/specials/SpecialUserlogin.php(830): LdapAuthenticationPlugin->updateUser(Object(User))

#7 /opt/mediawiki-1.26.2-2/apps/mediawiki/htdocs/includes/specials/SpecialUserlogin.php(958): LoginForm->authenticateUserData()

#8 /opt/mediawiki-1.26.2-2/apps/mediawiki/htdocs/includes/specials/SpecialUserlogin.php(341): LoginForm->processLogin()

#9 /opt/mediawiki-1.26.2-2/apps/mediawiki/htdocs/includes/specialpage/SpecialPage.php(384): LoginForm->execute(NULL)

#10 /opt/mediawiki-1.26.2-2/apps/mediawiki/htdocs/includes/specialpage/SpecialPageFactory.php(553): SpecialPage->run(NULL)

#11 /opt/mediawiki-1.26.2-2/apps/mediawiki/htdocs/includes/MediaWiki.php(281): SpecialPageFactory::executePath(Object(Title), Object(RequestContext))

#12 /opt/mediawiki-1.26.2-2/apps/mediawiki/htdocs/includes/MediaWiki.php(714): MediaWiki->performRequest()

#13 /opt/mediawiki-1.26.2-2/apps/mediawiki/htdocs/includes/MediaWiki.php(508): MediaWiki->main()

#14 /opt/mediawiki-1.26.2-2/apps/mediawiki/htdocs/index.php(41): MediaWiki->run()

#15 {main}
```
 

最终，通过报错信息`Error: 1146 Table 'bitnami_mediawiki.ldap_domains' doesn't exist (localhost:3306)`，发现不存在`ldap_domains`表，即`bitnami_mediawiki`不存在这个表，后来尝试在`phpmyAdmin`上为`bitnami_mediawiki`创建`ldap_domains`表，并在表内创建`user_id`和`domain`列，问题解决。

> 备注：根据多次实验和页面错误提示，才确认建立`user_id`和`domain`列


# 5 备份

备份数据库、配置文件、附件目录`images`、插件目录`extensions`

## 5.1 备份脚本

``` groovy
Now=$(date   +"%Y%m%d%H")

File=bitnami_mediawiki-$Now.sql

echo   **********start$Now************    >>    /mnt/mediawiki-bak/log/$Now.log

/opt/mediawiki-1.26.2-2/mysql/bin/mysqldump   -uroot -pDe123456 bitnami_mediawiki > /mnt/mediawiki-bak/$File

echo   **********cp LocalSettings.php********** >>  /mnt/mediawiki-bak/log/$Now.log

rsync   -avzrtopgL  --progress    /opt/mediawiki-1.26.2-2/apps/mediawiki/htdocs/LocalSettings.php   /mnt/mediawiki-bak/LocalSettings.php

echo   *********cp images ******** >>    /mnt/mediawiki-bak/log/$Now.log

rsync   -avzrtopgL  --progress   /opt/mediawiki-1.26.2-2/apps/mediawiki/htdocs/images /mnt/mediawiki-bak/

echo   ********cp extensions ********* >>    /mnt/mediawiki-bak/log/$Now.log

rsync   -avzrtopgL  --progress   /opt/mediawiki-1.26.2-2/apps/mediawiki/htdocs/extensions /mnt/mediawiki-bak/   >> /mnt/mediawiki-bak/log/$Now.log

echo   ********end$Now********* >> /mnt/mediawiki-bak/log/$Now.log
```





#  6 安装包及插件等

![LdapAuthentication-REL1_26-70ab129.tar.gz](LdapAuthentication-REL1_26-70ab129.tar.gz)

![LdapAuthentication-REL1_26-70ab129.tar.gz](LdapAuthentication-REL1_26-70ab129.tar.gz)

![MsUpload-REL1_26-47cfb25.tar.gz](MsUpload-REL1_26-47cfb25.tar.gz)

![SyntaxHighlight_GeSHi-REL1_26-a15f02e.tar.gz](SyntaxHighlight_GeSHi-REL1_26-a15f02e.tar.gz)

![WikiEditor-REL1_26-72db6c7.tar.gz](WikiEditor-REL1_26-72db6c7.tar.gz)

安装包：`bitnami_mediawiki`（自己下载）
