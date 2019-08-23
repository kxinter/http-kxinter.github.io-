---
title: linux调整目录分区大小，linux调整home目录大小，linux调整root目录大小（ext格式/LVM）
tags:
  - 分区
categories:
  - Linux
copyright: true
date: 2018-08-30 11:36:21
---

> **说明：ext格式分区可无损扩大或缩小分区。要先对文件系统进行缩小，然后才能缩小逻辑卷，一层层向下。和扩大正好相反。**
> 
> 注意vg_sql-lv_home其中的sql其实为hostname!
<!--more-->
# resize2fs命令

resize2fs命令被用来增大或者收缩未加载的“ext2/ext3”文件系统的大小。如果文件系统是处于mount状态下，那么它只能做到扩容，前提条件是内核支持在线resize。，linux kernel 2.6支持在mount状态下扩容但仅限于ext3文件系统。

来自: http://man.linuxde.net/resize2fs

# 一、首先df -h查看分区情况（这里我想调整home目录）

``` lsl
[root@sql ~]# df -h
Filesystem                  Size  Used Avail Use% Mounted on
/dev/mapper/vg_sql-lv_root   50G  906M   46G   2%  /
tmpfs                        935M     0  935M   0% /dev/shm
/dev/sda1                    477M   30M  422M   7% /boot
/dev/mapper/vg_sql-lv_home   341G   67M  323G   1% /home
```



# 二、卸载home目录umount /home

``` lsl
[root@sql ~]# umount /home
[root@sql ~]# df -h
Filesystem                     Size  Used Avail Use% Mounted on
/dev/mapper/vg_sql-lv_root     50G  706M   46G   2% /
tmpfs                         935M     0  935M   0% /dev/shm
/dev/sda1                      477M   30M  422M   7% /boot
```


# 三、重新指定/home目录大小

**缩小文件系统**

``` pf
[root@sql ~]# e2fsck -f /dev/mapper/vg_sql-lv_home
e2fsck 1.41.12 (17-May-2010)
Pass 1: Checking inodes, blocks, and sizes
Pass 2: Checking directory structure
Pass 3: Checking directory connectivity
Pass 4: Checking reference counts
Pass 5: Checking group summary information
/dev/mapper/vg_sql-lv_home: 11/22650880 files (0.0% non-contiguous), 1471409/90597376 blocks
[root@sql ~]# resize2fs -p /dev/mapper/vg_sql-lv_home 30G
resize2fs 1.41.12 (17-May-2010)
Resizing the filesystem on /dev/mapper/vg_sql-lv_home to 7864320 (4k) blocks.
Begin pass 2 (max = 32768)
Relocating blocks             XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
Begin pass 3 (max = 2765)
Scanning inode table          XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
The filesystem on /dev/mapper/vg_sql-lv_home is now 7864320 blocks long.
```



# 四、挂载/home，然后查看调整后的大小

``` lsl
[root@sql ~]# mount /home
[root@sql ~]# df -h
Filesystem                        Size  Used Avail Use% Mounted on
/dev/mapper/vg_sql-lv_root        50G  706M   46G   2% /
tmpfs                             935M     0  935M   0% /dev/shm
/dev/sda1                         477M   30M  422M   7% /boot
/dev/mapper/vg_sql-lv_home        30G   44M   28G   1% /home
```



# 五、用lvreduce命令把目标分区(/home)减小至30G

**缩小逻辑卷**

``` asciidoc
[root@sql ~]# lvreduce -L 30G /dev/mapper/vg_sql-lv_home
WARNING: Reducing active and open logical volume to 30.00 GiB
THIS MAY DESTROY YOUR DATA (filesystem etc.)
Do you really want to reduce lv_home? [y/n]: y
  Size of logical volume vg_sql/lv_home changed from 345.60 GiB (88474 extents) to 30.00 GiB (7680 extents).
  Logical volume lv_home successfully resized
```



# 六、用vgdisplay命令查看多余的空间，可以看到多出约320G的空间

``` yaml
[root@sql ~]# vgdisplay
  --- Volume group ---
  VG Name               vg_sql
  System ID            
  Format                lvm2
  Metadata Areas        1
  Metadata Sequence No  5
  VG Access             read/write
  VG Status             resizable
  MAX LV                0
  Cur LV                3
  Open LV               3
  Max PV                0
  Cur PV                1
  Act PV                1
  VG Size               399.51 GiB
  PE Size               4.00 MiB
  Total PE              102274
  Alloc PE / Size       21480 / 83.91 GiB
  Free  PE / Size       80794 / 315.60 GiB
  VG UUID               L9OUKR-6alh-ms7H-yimo-ypYm-lLYa-DqkpMC
```



# 七、用lvextend命令将多余的约320G空间挂载到/目录下

**扩大逻辑卷**

> 注：在设定lv_root的大小时，不要把Free PE / Size的空间全部都用上，这很可能会出现Free
> PE空间不足的现象，建议保留一点Free PE的空间。
> 
> 另：我这里搞上完没有出错，其实没有出错，查看空闲大小，显示Free PE / Size 0 / 0

``` sqf
[root@sql ~]# lvextend -L +315.60G /dev/mapper/vg_sql-lv_root
  Rounding size to boundary between physical extents: 315.60 GiB
  Size of logical volume vg_sql/lv_root changed from 50.00 GiB (12800 extents) to 365.60 GiB (93594 extents).
  Logical volume lv_root successfully resized
```


# 八、激活目录大小（扩展后的/目录）

**扩大文件系统**

> 注：执行这个命令后，会进入漫长的等待，这里我是机械硬盘，且调整分区约320G，耗时较长

``` applescript
[root@sql ~]# resize2fs -p /dev/mapper/vg_sql-lv_root
resize2fs 1.41.12 (17-May-2010)
Filesystem at /dev/mapper/vg_sql-lv_root is mounted on /; on-line resizing required
old desc_blocks = 4, new_desc_blocks = 23
Performing an on-line resize of /dev/mapper/vg_sql-lv_root to 95840256 (4k) blocks.
The filesystem on /dev/mapper/vg_sql-lv_root is now 95840256 blocks long.
```


# 九、df -h查看修改成功后的分区情况

``` jboss-cli
[root@sql ~]# df -h
Filesystem                       Size  Used Avail Use% Mounted on
/dev/mapper/vg_sql-lv_root       360G  720M  341G   1% /
tmpfs                            935M     0  935M   0% /dev/shm
/dev/sda1                        477M   30M  422M   7% /boot
/dev/mapper/vg_sql-lv_home       30G   44M   28G   1% /home
```
转载：https://www.cplusplus.me/2316.html



