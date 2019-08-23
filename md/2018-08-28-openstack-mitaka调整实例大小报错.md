---
title: openstack-mitaka调整实例大小报错
tags:
  - openstack
categories:
  - Openstack
copyright: true
date: 2018-08-28 16:28:21
---

# 1 问题1
<!--more-->
在openstack图形界面对实例进行迁移操作时，出现如下错误

``` stylus
2017-09-18 11:00:21.828 1386 INFO nova.compute.resource_tracker [req-4fe2d206-e9bc-4a61-9389-a01007335c61 - - - - -] Total usable vcpus: 12, total allocated vcpus: 5
2017-09-18 10:55:08.695 1386 ERROR oslo_messaging.rpc.dispatcher return self._do_dispatch(endpoint, method, ctxt, args)
2017-09-18 10:55:08.695 1386 ERROR oslo_messaging.rpc.dispatcher File "/usr/lib/python2.7/site-packages/oslo_messaging/rpc/dispatcher.py", line 127, in _do_dispatch
2017-09-18 10:55:08.695 1386 ERROR oslo_messaging.rpc.dispatcher result = func(ctxt, **new_args)
2017-09-18 10:55:08.695 1386 ERROR oslo_messaging.rpc.dispatcher File "/usr/lib/python2.7/site-packages/nova/exception.py", line 114, in wrapped
2017-09-18 10:55:08.695 1386 ERROR oslo_messaging.rpc.dispatcher payload)
2017-09-18 10:55:08.695 1386 ERROR oslo_messaging.rpc.dispatcher File "/usr/lib/python2.7/site-packages/oslo_utils/excutils.py", line 220, in __exit__
2017-09-18 10:55:08.695 1386 ERROR oslo_messaging.rpc.dispatcher self.force_reraise()
2017-09-18 10:55:08.695 1386 ERROR oslo_messaging.rpc.dispatcher File "/usr/lib/python2.7/site-packages/oslo_utils/excutils.py", line 196, in force_reraise
2017-09-18 10:55:08.695 1386 ERROR oslo_messaging.rpc.dispatcher six.reraise(self.type_, self.value, self.tb)
2017-09-18 10:55:08.695 1386 ERROR oslo_messaging.rpc.dispatcher File "/usr/lib/python2.7/site-packages/nova/exception.py", line 89, in wrapped
2017-09-18 10:55:08.695 1386 ERROR oslo_messaging.rpc.dispatcher return f(self, context, *args, **kw)
2017-09-18 10:55:08.695 1386 ERROR oslo_messaging.rpc.dispatcher File "/usr/lib/python2.7/site-packages/nova/compute/manager.py", line 359, in decorated_function
2017-09-18 10:55:08.695 1386 ERROR oslo_messaging.rpc.dispatcher LOG.warning(msg, e, instance=instance)
2017-09-18 10:55:08.695 1386 ERROR oslo_messaging.rpc.dispatcher File "/usr/lib/python2.7/site-packages/oslo_utils/excutils.py", line 220, in __exit__
2017-09-18 10:55:08.695 1386 ERROR oslo_messaging.rpc.dispatcher self.force_reraise()
2017-09-18 10:55:08.695 1386 ERROR oslo_messaging.rpc.dispatcher File "/usr/lib/python2.7/site-packages/oslo_utils/excutils.py", line 196, in force_reraise
2017-09-18 10:55:08.695 1386 ERROR oslo_messaging.rpc.dispatcher six.reraise(self.type_, self.value, self.tb)
2017-09-18 10:55:08.695 1386 ERROR oslo_messaging.rpc.dispatcher File "/usr/lib/python2.7/site-packages/nova/compute/manager.py", line 328, in decorated_function
2017-09-18 10:55:08.695 1386 ERROR oslo_messaging.rpc.dispatcher return function(self, context, *args, **kwargs)
2017-09-18 10:55:08.695 1386 ERROR oslo_messaging.rpc.dispatcher File "/usr/lib/python2.7/site-packages/nova/compute/manager.py", line 409, in decorated_function
2017-09-18 10:55:08.695 1386 ERROR oslo_messaging.rpc.dispatcher return function(self, context, *args, **kwargs)
2017-09-18 10:55:08.695 1386 ERROR oslo_messaging.rpc.dispatcher File "/usr/lib/python2.7/site-packages/nova/compute/manager.py", line 316, in decorated_function
2017-09-18 10:55:08.695 1386 ERROR oslo_messaging.rpc.dispatcher migration.instance_uuid, exc_info=True)
2017-09-18 10:55:08.695 1386 ERROR oslo_messaging.rpc.dispatcher File "/usr/lib/python2.7/site-packages/oslo_utils/excutils.py", line 220, in __exit__
2017-09-18 10:55:08.695 1386 ERROR oslo_messaging.rpc.dispatcher self.force_reraise()
2017-09-18 10:55:08.695 1386 ERROR oslo_messaging.rpc.dispatcher File "/usr/lib/python2.7/site-packages/oslo_utils/excutils.py", line 196, in force_reraise
2017-09-18 10:55:08.695 1386 ERROR oslo_messaging.rpc.dispatcher six.reraise(self.type_, self.value, self.tb)
2017-09-18 10:55:08.695 1386 ERROR oslo_messaging.rpc.dispatcher File "/usr/lib/python2.7/site-packages/nova/compute/manager.py", line 293, in decorated_function
2017-09-18 10:55:08.695 1386 ERROR oslo_messaging.rpc.dispatcher return function(self, context, *args, **kwargs)
2017-09-18 10:55:08.695 1386 ERROR oslo_messaging.rpc.dispatcher File "/usr/lib/python2.7/site-packages/nova/compute/manager.py", line 387, in decorated_function
2017-09-18 10:55:08.695 1386 ERROR oslo_messaging.rpc.dispatcher kwargs['instance'], e, sys.exc_info())
2017-09-18 10:55:08.695 1386 ERROR oslo_messaging.rpc.dispatcher File "/usr/lib/python2.7/site-packages/oslo_utils/excutils.py", line 220, in __exit__
2017-09-18 10:55:08.695 1386 ERROR oslo_messaging.rpc.dispatcher self.force_reraise()
2017-09-18 10:55:08.695 1386 ERROR oslo_messaging.rpc.dispatcher File "/usr/lib/python2.7/site-packages/oslo_utils/excutils.py", line 196, in force_reraise
2017-09-18 10:55:08.695 1386 ERROR oslo_messaging.rpc.dispatcher six.reraise(self.type_, self.value, self.tb)
2017-09-18 10:55:08.695 1386 ERROR oslo_messaging.rpc.dispatcher File "/usr/lib/python2.7/site-packages/nova/compute/manager.py", line 375, in decorated_function
2017-09-18 10:55:08.695 1386 ERROR oslo_messaging.rpc.dispatcher return function(self, context, *args, **kwargs)
2017-09-18 10:55:08.695 1386 ERROR oslo_messaging.rpc.dispatcher File "/usr/lib/python2.7/site-packages/nova/compute/manager.py", line 3933, in resize_instance
2017-09-18 10:55:08.695 1386 ERROR oslo_messaging.rpc.dispatcher self.instance_events.clear_events_for_instance(instance)
2017-09-18 10:55:08.695 1386 ERROR oslo_messaging.rpc.dispatcher File "/usr/lib64/python2.7/contextlib.py", line 35, in __exit__
2017-09-18 10:55:08.695 1386 ERROR oslo_messaging.rpc.dispatcher self.gen.throw(type, value, traceback)
2017-09-18 10:55:08.695 1386 ERROR oslo_messaging.rpc.dispatcher File "/usr/lib/python2.7/site-packages/nova/compute/manager.py", line 6643, in _error_out_instance_on_exception
2017-09-18 10:55:08.695 1386 ERROR oslo_messaging.rpc.dispatcher raise error.inner_exception
2017-09-18 10:55:08.695 1386 ERROR oslo_messaging.rpc.dispatcher ResizeError: Resize error: not able to execute ssh command: Unexpected error while running command.
2017-09-18 10:55:08.695 1386 ERROR oslo_messaging.rpc.dispatcher Command: ssh -o BatchMode=yes 192.168.1.116 mkdir -p /var/lib/nova/instances/724a9fc0-3786-4ba4-8a43-744ec19a0881
2017-09-18 10:55:08.695 1386 ERROR oslo_messaging.rpc.dispatcher Exit code: 255
2017-09-18 10:55:08.695 1386 ERROR oslo_messaging.rpc.dispatcher Stdout: u''
2017-09-18 10:55:08.695 1386 ERROR oslo_messaging.rpc.dispatcher Stderr: u'Host key verification failed.\r\n
```

建立各计算节点、控制节点之间的SSH免密登录，建立私钥

## 解决方案

 - 开启nova用户登录权限

``` bash
usermod -s /bin/bash nova
```

 - 切换到nova用户

``` stata
su nova
```

生成密钥（各个计算节点执行，控制节点也执行）

``` shell
$ ssh-keygen -t rsa
#默认路径，直接回车
```

 - 所有计算节点均配置

> 依然在nova用户下操作

``` shell
$cat << EOF > ~/.ssh/config

> Host *

> StrictHostKeyChecking no

> UserKnownHostsFile=/dev/null

> EOF
```

 - 发送公钥到控制节点

compute1

``` elixir
scp id_rsa.pub 10.20.0.2:/var/lib/nova/.ssh/id_rsa.pub2
```

compute2

``` elixir
scp id_rsa.pub 10.20.0.2:/var/lib/nova/.ssh/id_rsa.pub3
```

contrloller(10.20.0.2)

``` vala
# cat id_dsa.pub id_dsa.pub2 id_rsa.pub id_rsa.pub2   id_rsa.pub3 id_dsa.pub3 > authorized_keys
# scp authorized_keys  computer1:/var/lib/nova/.ssh
# scp authorized_keys  computer2:/var/lib/nova/.ssh
```

修改权限

``` gradle
# chown nova:nova /var/lib/nova/.ssh/id_rsa /var/lib/nova/.ssh/authorized_keys
```

 - 登录测试

``` nginx
ssh nova@computer
```

在迁移实例，不再报错，并成功。

> 实例迁移根据使用存储不同，有不同差异，详细介绍参考openstack官方文档