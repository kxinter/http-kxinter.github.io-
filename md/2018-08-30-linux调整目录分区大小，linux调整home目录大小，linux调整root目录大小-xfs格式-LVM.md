---
title: linux调整目录分区大小，linux调整home目录大小，linux调整root目录大小(xfs格式/LVM)
tags:
  - 基础运维
  - 分区
categories:
  - Linux
date: 2018-08-30 11:32:03
---

> 说明：xfs格式分区无法无损缩减分区，可无损扩大分区。
<!--more-->
# 一：环境概览：
![enter description here](1.png)
![enter description here](2.png)
<!--more-->
# 二、操作步骤：

``` jboss-cli
# 1.终止占用 /home 进程	 
fuser -m -v -i -k /home 
# 2.备份/home 
cp -r  /home/  homebak/ 
# 3.卸载 /home	 
umount /home	 
# 4.删除/home所在的lv 
lvremove /dev/mapper/centos-home 
# 5.扩展/root所在的lv，增加100G 
lvextend -L +100G /dev/mapper/centos-root 
# 6.扩展/root文件系统	 
xfs_growfs /dev/mapper/centos-root 
# 7.重新创建home lv 
lvcreate -L 40G -n home centos 
# 8.创建文件系统 
mkfs.xfs /dev/centos/home 
# 9.挂载 
mount /dev/centos/home /home 
# 10.还原 /home 相关文件以及对应目录权限
```



三、执行结果：

![enter description here](3.png)

# 四、实测成功：

依旧教程扩容xfs，测试成功！

转载：https://www.cplusplus.me/2717.html