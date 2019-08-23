---
title: MySQL自带的性能压力测试工具mysqlslap
tags:
  - mysql
categories:
  - Linux
copyright: true
date: 2019-04-28 11:48:08
---
 # 1 mysqlslap介绍
 <!--more-->
 `mysqlslap`是从`MySQL5.1.4`版就开始官方提供的压力测试工具。

通过模拟多个并发客户端并发访问MySQL来执行压力测试，同时提供了较详细的SQL执行数据性能报告，并且能很好的对比多个存储引擎（MyISAM，InnoDB等）在相同环境下的相同并发压力下的性能差别。

mysqlslap 官方介绍：http://dev.mysql.com/doc/refman/5.6/en/mysqlslap.html

## 1.1 常用参数 [options] 详解

***`--host=host_name`***:    `-h host_name` 连接到的MySQL服务器的主机名（或IP地址），默认为本机localhost;

***`--user=user_name`***:    `-u user_name` 连接MySQL服务时用的用户名;

***`--password[=password]`***:  `-p[password]` 连接MySQL服务时用的密码;

***`--create-schema`***:    代表自定义的测试库名称，测试的`schema`，MySQL中`schema`也就是`database`;(没指定使用哪个数据库时，可能会遇到错误mysqlslap: Error when connecting to server: 1049 Unknown database 'mysqlslap')

***`***--query=name***`***:  `-q` 使用自定义脚本执行测试（可以是SQL字符串或脚本），例如可以调用自定义的一个存储过程或者sql语句来执行测试。

***`--create`***:    创建表所需的SQL（可以是SQL字符串或脚本）

***`--concurrency=N`***:  `-c N` 表示并发量，也就是模拟多少个客户端同时执行query。可指定多个值，以逗号或者--delimiter参数指定的值做为分隔符。例如：--concurrency=100,200,500（分别执行100、200、500个并发）。

***`--iterations=N`***:   `-i N `测试执行的迭代次数，代表要在不同的并发环境中，各自运行测试多少次；多次运行以便让结果更加准确。

***`--number-of-queries=N`***:   总的测试查询次数(并发客户数×每客户查询次数)

***`--engine=engine_name`***:  `-e engine_name` 代表要测试的引擎，可以有多个，用分隔符隔开。例如：--engines=myisam,innodb,memory。

**`--auto-generate-sq`**:  `-a` 自动生成测试表和数据，表示用mysqlslap工具自己生成的SQL脚本来测试并发压力。

***`--auto-generate-sql-load-type=type`***:   测试语句的类型。代表要测试的环境是读操作还是写操作还是两者混合的。取值包括：read (scan tables), write (insert into tables), key (read primary keys), update (update primary keys), or mixed (half inserts, half scanning selects). 默认值是：mixed.

***`--auto-generate-sql-add-auto-increment`***:   代表对生成的表自动添加auto_increment列，从5.1.18版本开始支持。

***`--number-char-cols=N`***:  ` -x N` 自动生成的测试表中包含多少个字符类型的列，默认1

***`--number-int-cols=N`***:  ` -y N `自动生成的测试表中包含多少个数字类型的列，默认1

***`--commint=N`***:   多少条DML后提交一次。

***`--compress`***:  ` -C` 如果服务器和客户端支持都压缩，则压缩信息传递。

***`--only-print`***:   只打印测试语句而不实际执行。

***`--detach=N`***:   执行N条语句后断开重连。

***`--debug-info`***:  ` -T` 打印内存和CPU的相关信息。

## 1.2 测试范例：

``` dos
mysqlslap -uroot -p --socket /tmp/mysql3306.sock --concurrency=1 --iterations=1 --create-schema='test' --query='SELECT id,unionid,current_num,total_num FROM invite_join WHERE unionid="Cmo" AND active_id="3" AND is_deleted =0 ORDER BY id DESC LIMIT 1;' --number-of-queries=1000000
```

**各种测试参数实例（-p后面跟的是mysql的root密码）：**

 - 单线程测试。测试做了什么。

``` dos
# mysqlslap -a -uroot -p123456
```

- 多线程测试。使用–concurrency来模拟并发连接。

``` dos
# mysqlslap -a -c 100 -uroot -p123456
```

- 迭代测试。用于需要多次执行测试得到平均值。

``` dos
# mysqlslap -a -i 10 -uroot -p123456
```


``` dos
# mysqlslap ---auto-generate-sql-add-autoincrement -a -uroot -p123456
# mysqlslap -a --auto-generate-sql-load-type=read -uroot -p123456
# mysqlslap -a --auto-generate-secondary-indexes=3 -uroot -p123456
# mysqlslap -a --auto-generate-sql-write-number=1000 -uroot -p123456
# mysqlslap --create-schema world -q "select count(*) from City" -uroot -p123456
# mysqlslap -a -e innodb -uroot -p123456
# mysqlslap -a --number-of-queries=10 -uroot -p123456
```

- 测试同时不同的存储引擎的性能进行对比：

``` dos
# mysqlslap -a --concurrency=50,100 --number-of-queries 1000 --iterations=5 --engine=myisam,innodb --debug-info -uroot -p123456
```

- 执行一次测试，分别50和100个并发，执行1000次总查询：

``` dos
# mysqlslap -a --concurrency=50,100 --number-of-queries 1000 --debug-info -uroot -p123456
```

- 50和100个并发分别得到一次测试结果(Benchmark)，并发数越多，执行完所有查询的时间越长。为了准确起见，可以多迭代测试几次:

``` dos
# mysqlslap -a --concurrency=50,100 --number-of-queries 1000 --iterations=5 --debug-info -uroot -p123456
```