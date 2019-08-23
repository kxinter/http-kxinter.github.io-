---
title: Openstack调整实例大小_冷迁移
tags:
  - openstack
categories:
  - Openstack
date: 2018-08-28 16:03:09
---

> 有时虚拟机创建后发现虚拟机规格太小，满足不了业务需求。于是需要在线拉伸虚拟机的规格。
<!--more-->
1、用admin用户登录dashboard，创建满足需求的虚拟机规格

2、输入适当的参数

3、修改controller和各个computer节点的nova.cnf文件，打开下面两个参数

``` ini
allow_resize_to_same_host=True 
scheduler_default_filters=RetryFilter,AvailabilityZoneFilter,RamFilter,ComputeFilter,ComputeCapabilitiesFilter,ImagePropertiesFilter,ServerGroupAntiAffinityFilter,ServerGroupAffinityFilter
```

4、重启控制节点nova服务

``` thrift
# systemctl restart openstack-nova-api.service openstack-nova-conductor.service openstack-nova-scheduler.service openstack-nova-cert.service openstack-nova-consoleauth.service openstack-nova-compute.service openstack-nova-novncproxy.service
```

5、重启计算节点nova服务

``` vala
# service openstack-nova-compute restart
```

参考资料：
http://www.cnblogs.com/goodcook/p/6509808.html