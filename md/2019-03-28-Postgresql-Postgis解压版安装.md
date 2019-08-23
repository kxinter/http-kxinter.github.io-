---
title: Postgresql_Postgis解压版安装
tags:
  - postgresql
categories:
  - Windows
copyright: true
date: 2019-03-28 14:18:56
---
# 1．软件下载
<!--more-->
postgresql-9.6.1-1-windows-x64-binaries.zip

https://www.postgresql.org/download/windows/

postgis-bundle-pg96-2.3.1x64.zip

http://download.osgeo.org/postgis/windows/pg96/

# 2.  将postgresql.zip解压

解压`postgresql-9.6.1-1-windows-x64-binaries.zip`到你想要的安装目录（`D:\GreenSoftware\PostgreSQL961`），主要最好不要有中文或者空格，

 

# 3.  创建数据存放目录
D:\GreenSoftware\PostgreSQL961\data

 

# 4.  初始化数据库

D:\GreenSoftware\PostgreSQL961\bin\ `initdb.exe -D D:\GreenSoftware\PostgreSQL961\data -E UTF8 --locale=Chinese`


# 5.  启动数据库，有两种方式

## 5.1  第一种方式：注册为windows服务方式

### 5.1.1  注册服务

D:\GreenSoftware\PostgreSQL961\bin\ `pg_ctl.exe register -D D:\GreenSoftware\PostgreSQL961\data -Npgsql`
{%note info %}**备注：**
-N表示windows服务名称为pgsql；
{%endnote%}

### 5.1.2 启动服务

``` dos
net start pgsql
```

如果你的安装没有错误，现在就应该可以起来了。

### 5.1.3 关闭服务

``` dos
net stop pgsql
```

### 5.1.4 卸载服务

D:\GreenSoftware\PostgreSQL961\bin\ `pg_ctl.exe unregister -D D:\GreenSoftware\PostgreSQL961\data –Npgsql`

 

## 5.2 第二种方式：直接启动方式

### 5.2.1 启动

D:\GreenSoftware\PostgreSQL961\bin\ `pg_ctl.exe start -w -D D:\GreenSoftware\PostgreSQL961\data`

### 5.2.2 关闭

D:\GreenSoftware\PostgreSQL961\bin\ `pg_ctl.exe stop -W -D D:\GreenSoftware\PostgreSQL961\data`

 

# 6 创建数据库

D:\GreenSoftware\PostgreSQL961\bin\ `createdb.exe -E UTF8 geodb`

D:\GreenSoftware\PostgreSQL961\bin\ `dropdb.exe geodb`

 

# 7 创建用户

D:\GreenSoftware\PostgreSQL961\bin\ `createuser.exe -s -r postgres`

会有是否创建superuser的选项，创建一个名为postgres的超级用户；

> **使用方法:**
> 
> `createuser [选项]... [用户名]`
> 
> 选项:
> 
> -c, --connection-limit=N 角色的连接限制(缺省: 没有限制)
> 
> -d, --createdb 此角色可以创建新数据库
> 
> -D, --no-createdb 此角色不可以创建新数据库
> 
> -e, --echo 显示发送到服务端的命令
> 
> -E, --encrypted 口令加密存储
> 
> -i, --inherit 角色能够继承它所属角色的权限
> 
> （这是缺省情况)
> 
> -I, --no-inherit 角色不继承权限
> 
> -l, --login 角色能够登录(这是缺省情况)
> 
> -L, --no-login 角色不能登录
> 
> -N, --unencrypted 口令不加密存储
> 
> -P, --pwprompt 给新角色指定口令
> 
> -r, --createrole 这个角色可以创建新的角色
> 
> -R, --no-createrole 这个角色没有创建其它角色的权限
> 
> -s, --superuser 角色将是超级用户
> 
> -S, --no-superuser 角色不能是超级用户
> 
> --help 显示此帮助信息, 然后退出
> 
> --version 输出版本信息, 然后退出
> 
> 联接选项:
> 
> -h, --host=HOSTNAM 数据库服务器所在机器的主机名或套接字目录
> 
> -p, --port=PORT 数据库服务器端口号
> 
> -U, --username=USERNAME 联接用户 (不是要创建的用户名)
> 
> -w, -no-password 永远不提示输入口令
> 
> -W, --password 强制提示输入口令
> 
> 如果 -d, -D, -r, -R, -s, -S 和 ROLENAME 一个都没有指定,将使用交互式提示
> 
> 你.
> 
> 臭虫报告至 <pgsql-bugs@postgresql.org>.
> 
> 例子1:>createuser -P -d -U postgres dan
> 
> 解释:-P(大写)说的是为新用户指定口令;-d说的该角色是否可以创建数据库;-U(大写)当前的操作是哪个用户发出的;最后的dan是新用户的名字。
> 
> 补充：
> 
> 查看系统中的所用用户：select * from pg_user;
> 
> 删除一个用户：drop user dan;其中dan为用户名
> 
> D:\GreenSoftware\PostgreSQL961\bin\dropuser.exe postgres

 

## 7.1 修改用户密码

### 7.1.1第一种方式：应用psql命令

D:\GreenSoftware\PostgreSQL961\bin\ `psql.exe postgres`

```sql
postgres=# alter user postgres with password 'xxx';

postgres-# \q
```

 

### 7.1.2第二种方式：为使用pgAdmin修改

用pgAdmin连接到服务器，可以直接修改密码；

 

# 8 将postgis-bundle-pg96-2.3.1x64.zip解压

解压`postgis-bundle-pg96-2.3.1x64.zip`到没有中文或者空格的目录。

 

# 9 修改makepostgisdb_using_extensions.bat文件

![1](1.jpg)

 

# 10 将空间数据导入PostGIS中

![2](2.jpg)

![3](3.jpg)

 

# 11 显示PostGIS中空间数据

![4](4.jpg)

 

![5](5.jpg)

 

 

# 12处理外网访问

## 1. 修改D:\GreenSoftware\PostgreSQL961\data\pg_hba.conf文件

加入如下的文字：

`host    all             all             192.168.1.0/24          md5`
![6](6.png)
 



 

## 2.修改D:\GreenSoftware\PostgreSQL961\data\postgresql.conf文件

加入如下的文字：

将

`#listen_addresses = '127.0.0.1'`

改为：

`listen_addresses = '*'`
 
![7](7.png)
