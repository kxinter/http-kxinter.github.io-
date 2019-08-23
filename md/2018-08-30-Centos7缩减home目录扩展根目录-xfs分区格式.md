---
title: Centos7缩减home目录扩展根目录（xfs分区格式）
tags:
  - 分区
categories:
  - Linux
date: 2018-08-30 11:41:10
---

# 1 磁盘占用
<!--more-->

修改home目录大小，增加根目录容量。

# 2 注意事项

 - xfsf分区减小分区无法做到无损数据（必须备份数据） 
 - 扩容分区可以保存数据无损

# 3 xfs分区扩展根目录命令过程

把/home内容备份，然后将/home文件系统所在的逻辑卷删除，扩大/root文件系统，新建/home：

``` jboss-cli
tar cvf /tmp/home.tar /home       #备份/home
umount /home                      #卸载/home，如果无法卸载，先终止使用/home文件系统的进程
lvremove /dev/centos/home         #删除/home所在的lv（可删除分区，也可使用下行缩减分区）
lvreduce -L 180G /dev/centos/home #缩小分区到180G(缩小分区后分区数据丢失，需重新格式化并挂载分区，否则重启故障)
lvextend -L +50G /dev/centos/root #扩展/root所在的lv，增加50G
xfs_growfs /dev/centos/root       #扩展/root文件系统
lvcreate -L 56G -n home centos    #重新创建home lv
mkfs.xfs /dev/centos/home         #创建文件系统及格式化
mount /dev/centos/home /home      #挂载
df -h
```

# 4 收缩分区

> ext与xfs格式分区收缩分区命令不同，lvextend -L+19.8G /dev/VolGroup00/LogVol00
> 分区命令后，执行相应收缩命令后扩展的容量才能正常使用

**xfs格式**
如果分区格式为xfs，扩展使用  要用xfs_growfs命令而不是resize2fs命令收缩分区，

``` elixir
[root@rac2 ~]# xfs_growfs -p /dev/VolGroup00/LogVol00
```

执行以上命令后，`df  -h`命令查看才会显示扩容成功。

**ext2、ext3、ext4格式（补充）**
Ext2、ext3、ext4等使用resize2fs收缩分区，xfs使用xfs-growfs命令收缩分区。详情找度娘。

例如:

``` elixir
[root@rac2 ~]# resize2fs -p /dev/VolGroup00/LogVol00
```

