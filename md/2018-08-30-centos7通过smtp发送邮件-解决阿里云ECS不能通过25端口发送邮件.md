---
title: centos7通过smtp发送邮件（解决阿里云ECS不能通过25端口发送邮件）
tags:
  - email
  - smtp
categories:
  - Linux
date: 2018-08-30 12:14:32
---

# 1 参考资料
<!--more-->
https://bbs.aliyun.com/read/316576.html

http://blog.csdn.net/qq_25551295/article/details/51803942

# 2 安装mailx

``` ebnf
yum install mailx
```

## 2.1 修改配置文件

``` nginx
vim /etc/mail.rc
```

追加如下内容

``` sql
set smtp="smtps://smtp.mxhichina.com:465"
set smtp-auth=login
set smtp-auth-user="sales@vfutai.xxx"
set smtp-auth-password="Ni-De-Mi-Ma"
set ssl-verify=ignore
set nss-config-dir=/etc/pki/nssdb
```


## 2.2 发送测试

**例子1：**

``` nginx
echo message3 | mail -v -r "sales@vfutai.xxx" -s "This is the subject" dongshan3@foxmail.xxx
```

> `message3` 正文
> 
> `dongshan3@foxmail.xxx` 收件人地址，发送多人加逗号添加邮件地址
> 
> `-r “sales@vfutai.xxx”` 发件人地址
> 
> `-s "This is the subject"`  邮件标题
> 
> `-a  /etc/*.txt`  附件



**列子2：**

``` bash
#!/usr/bin/bash
#发送邮件到kxhuanzi@163.com
sj=`date +%Y%m%d`
echo "备份mysql" >> /opt/mysqldata/$sj.log
mysqldump -uroot -ppassword bitnami_wordpress > /opt/mysqldata/$sj.sql >> /opt/mysqldata/$sj.log
echo "发送mysql备份电子邮件到k*****@163.com" >> /opt/mysqldate/$sj.log
echo MYSQL备份，备份文件名字:$sj.sql,备份日期:`date`.| mail -v -r "32****@qq.com" -a /opt/mysqldata/$sj.sql -s "wordpress备份/$sj" k****@163.com,xh****@gmail.com
echo "发送完成" >> /opt/mysqldata/$sj.log
~
```

