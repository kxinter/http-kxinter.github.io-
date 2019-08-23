---
title: Openstack热迁移和冷迁移
tags:
  - openstack
categories:
  - Openstack
date: 2018-08-28 12:09:56
---

# 1 迁移类型：
<!--more-->
*`非在线迁移` (有时也称之为‘`迁移`’)。也就是在迁移到另外的计算节点时的这段时间虚拟机实例是处于宕机状态的。在此情况下，实例需要重启才能工作。

*`在线迁移` (或 '`真正的在线迁移`')。实例几乎没有宕机时间。用于当实例需要在迁移时保持运行。在线迁移有下面几种类型：

* 基于共享存储的在线迁移。所有的Hypervisor都可以访问共享存储。

* 块在线迁移。无须共享存储。但诸如CD-ROM之类的只读设备是无法实现的。

* 基于卷的在线迁移。实例都是基于卷的而不是临时的磁盘，无须共享存储，也支持迁移(目前仅支持基于libvirt的hypervisor)。

## 1.1 什么是热迁移

`热迁移`（Live Migration，又叫`动态迁移`、`实时迁移`），即虚拟机保存/恢复(Save/Restore)：将整个虚拟机的运行状态完整保存下来，同时可以快速的恢复到原有硬件平台甚至是不同硬件平台上。恢复以后，虚拟机仍旧平滑运行，用户不会察觉到任何差异。

## 1.2 Openstack热迁移

OpenStack有两种在线迁移类型：`live migration`和`block migration`。`Livemigration`需要实例保存在NFS共享存储中，这种迁移主要是实例的内存状态的迁移，速度应该会很快。`Block migration`除了实例内存状态要迁移外，还得迁移磁盘文件，速度会慢些，但是它不要求实例存储在共享文件系统中。
NFS允许一个系统在网络上与他人共享目录和文件。通过使用NFS，用户和程序可以像访问本地文件一样访问远端系统上的文件。

### 1.2.1 迁移步骤

 1. 迁移前的条件检查
动态迁移要成功执行，一些条件必须满足，所以在执行迁移前必须做一些条件检查。
    - 权限检查，执行迁移的用户是否有足够的权限执行动态迁移。
    - 参数检查，传递给 API 的参数是否足够和正确，如是否指定了 block-migrate 参数。
    - 检查目标物理主机是否存在。
    - 检查被迁移的虚拟机是否是 running 状态。
    - 检查源和目的物理主机上的 nova-compute service 是否正常运行。
    - 检查目的物理主机和源物理主机是否是同一台机器。
    - 检查目的物理主机是否有足够的内存(memory)。
    - 检查目的和源物理主机器 hypervisor 和 hypervisor 的版本是否相同。
2. 迁移前的预处理
在真正执行迁移前，必须做一下热身，做一些准备工作。
   - 在目的物理主机上获得和准备虚拟机挂载的块设备(`volume`)。

   -  在目的物理主机上设置虚拟机的网络(`networks`)。

   - 目的物理主机上设置虚拟机的防火墙(`fireware`)。
3. 迁移
条件满足并且做完了预处理工作后，就可以执行动态迁移了。主要步骤如下：
   - 调用 libvirt python 接口 migrateToURI，来把源主机迁移到目的主机。
dom.migrateToURI(CONF.live_migration_uri % dest,logical_sum,None,CONF.live_migration_bandwidth)
live_migration_uri：这个 URI 就是在 3.2.2 里介绍的 libvirtd 进程定义的。
live_migration_bandwidth：这个参数定义了迁移过程中所使用的最大的带宽。
   - 以一定的时间间隔（0.5）循环调用 wait_for_live_migration 方法，来检测虚拟机迁移 的状态，一直到虚拟机成功迁移为止。
4. 迁移后的处理
当虚拟机迁移完成后，要做一些善后工作。
   - 在源物理主机上 detach volume。
   - 在源物理主机上释放 security group ingress rule。
   - 在目的物理主机上更新数据库里虚拟机的状态。
   - 在源物理主机上删除虚拟机。
上面四步正常完成后，虚拟机就成功的从源物理主机成功地迁移到了目的物理主机了

### 1.2.2 Live Migration 的实现

热迁移条件：

1. 计算节点之间可以通过主机名互相访问

2. 计算节点和控制节点的nova uid和gid保持一致

3. vncserver_proxyclient_address和vncserver_listen 监听的是本地IP

4. 必须有共享存储，实例存放在共享存储中，且每个计算节点都可以访问共享存储。否则只能使用块迁移

### 1.2.3 配置

   - 添加live_migration_flag
修改nova的配置文件，在`[libvirt]` 段下 添加如下字段

``` makefile
live_migration_flag="VIR_MIGRATE_UNDEFINE_SOURCE,VIR_MIGRATE_PEER2PEER,VIR_MIGRATE_LIVE,VIR_MIGRATE_PERSIST_DEST,VIR_MIGRATE_TUNNELLED"
```

   - 配置配置versh免密码连接，修改/etc/libvirt/libvirtd.conf
添加如下配置

``` makefile
listen_tls = 0

listen_tcp = 1

tcp_port = "16509"

listen_addr = "172.16.201.8"   #根据自己的计算节点IP改写

auth_tcp = "none"
```


   - 修改/etc/sysconfig/libvirtd 添加如下参数

``` makefile
LIBVIRTD_CONFIG=/etc/libvirt/libvirtd.conf

LIBVIRTD_ARGS="--listen"
```

   - 重启libvirt

``` maxima
systemctl restart libvirtd.service
```

   - 查看监听端口：

``` x86asm
[root@compute1 ~]# netstat -lnpt | grep libvirtd

tcp        0      0 172.16.206.6:16509      0.0.0.0:*               LISTEN      9852/libvirtd
```

   - 测试：

``` groovy
在compute1节点上：

virsh -c qemu+tcp://compute2/system

在compute2节点上

virsh -c qemu+tcp://compute1/system
```
如果能无密码连接上去，表示配置没问题

### 1.2.4动态迁移

   - 查看所有实例
     nova list
   - 查看需要迁移虚拟机实例
     nova show f3d749ba-98e1-4624-9782-6da729ad164c
   - 查看可用的计算节点
     nova-manage service list
   - 查看目标节点资源
     nova-manage service describe_resource computer1
   - 开始迁移，正常无任何回显
     nova live-migration 8da00f69-05f6-4425-9a8a-df56b79a474f computer1

   - 也可以通过dashboard 节点迁移
     用节点迁移需要使用admin管理员用户执

## 1.3 冷迁移配置

1. 冷迁移需要启动nova账户，并配置ssh 免密码认证

``` avrasm
usermod -s /bin/bash nova

su - nova

ssh-keygen -t rsa

# 生成密钥

cp -fa id_rsa.pub authorized_keys
```

将密钥复制到所有计算节点的/var/lib/nova/.ssh下，并设置权限为nova用户

2. 编辑/etc/nova/nova.conf的配置文件，修改下面参数

``` ini
allow_resize_to_same_host=True 

scheduler_default_filters=RetryFilter,AvailabilityZoneFilter,RamFilter,ComputeFilter,ComputeCapabilitiesFilter,ImagePropertiesFilter,ServerGroupAntiAffinityFilter,ServerGroupAffinityFilter 
```

3. 在计算节点重启nova服务

``` maxima
systemctl restart openstack-nova-compute
```

4. 在controller节点重启nova 相关服务

``` thrift
systemctl restart openstack-nova-api.service openstack-nova-scheduler.service
```

