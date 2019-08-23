---
title: Openvpn基于LDAP认证下进行包过滤（控制访问权限）
tags:
  - openvpn
  - ldap
categories:
  - Linux
date: 2018-08-31 17:54:57
---

# 1 说明
<!--more-->
> 方案：采用minimal_pf.so模块和包过滤
> 
> 此方法同样适用于基本认证。
<!--more-->
参考资料：http://backreference.org/2010/06/18/openvpns-built-in-packet-filter/

http://732233048.blog.51cto.com/9323668/1713088

# 2 安装openvpn及设置LDAP认证

详细步骤参考本站 **openvpn部署之部署基于ad域认证访问内网**

# 3 控制访问权限

## 3.1 创建及编辑minimal_pf.c模块

``` elixir
[root@openvpn ~]# cd /etc/openvpn/

[root@openvpn openvpn]# vim minimal_pf.so
```

键入以下内容（内容固定）

``` cpp
/* minimal_pf.c 
 * ultra-minimal OpenVPN plugin to enable internal packet filter */
#include <stdio.h>
#include <stdlib.h>
 
#include "include/openvpn-plugin.h"
 
/* dummy context, as we need no state */
struct plugin_context {
  int dummy;
};
 
/* Initialization function */
OPENVPN_EXPORT openvpn_plugin_handle_t openvpn_plugin_open_v1 (unsigned int *type_mask, const char *argv[], const char *envp[]) {
  struct plugin_context *context;
  /* Allocate our context */
  context = (struct plugin_context *) calloc (1, sizeof (struct plugin_context));
 
  /* Which callbacks to intercept. */
  *type_mask = OPENVPN_PLUGIN_MASK (OPENVPN_PLUGIN_ENABLE_PF);
 
  return (openvpn_plugin_handle_t) context;
}
 
/* Worker function */
OPENVPN_EXPORT int openvpn_plugin_func_v2 (openvpn_plugin_handle_t handle,
            const int type,
            const char *argv[],
            const char *envp[],
            void *per_client_context,
            struct openvpn_plugin_string_list **return_list) {
   
  if (type == OPENVPN_PLUGIN_ENABLE_PF) {
    return OPENVPN_PLUGIN_FUNC_SUCCESS;
  } else {
    /* should not happen! */
    return OPENVPN_PLUGIN_FUNC_ERROR;
  }
}
 
/* Cleanup function */
OPENVPN_EXPORT void openvpn_plugin_close_v1 (openvpn_plugin_handle_t handle) {
  struct plugin_context *context = (struct plugin_context *) handle;
  free (context);
}
```


## 3.2 构建插件

下载并解压OpenVPN源码压缩包（严格来说，只需要openvpn-plugin.h）

openvpn源码安装包：`openvpn-2.3.11.tar.gz  ，解压文件，复制`include`目录到`/etc/openvpn`

并使用以下命令构建插件：

``` bash
INCLUDE="-I/etc/openvpn"         # CHANGE THIS!!!!
CC_FLAGS="-O2 -Wall -g"
NAME=minimal_pf
gcc $CC_FLAGS -fPIC -c $INCLUDE $NAME.c && \
gcc $CC_FLAGS -fPIC -shared -Wl,-soname,$NAME.so -o $NAME.so $NAME.o -lc
```




## 3.3 创建包过滤文件

``` jboss-cli
mkdir /etc/openvpn/ccd

cd /etc/openvpn/ccd
```

创建以`用户名.pf`命名的文件，输入以下内容。

``` accesslog
vi client1.pf             #客户client1，只对10.10.1.0网段有权限
[CLIENTS ACCEPT]
[SUBNETS DROP]
+10.10.1.0/24
[END]


vi client.pf              #客户client，对所有内网服务器都有权限
[CLIENTS ACCEPT]
[SUBNETS ACCEPT]
[END]
```

### 3.3.1 包过滤文件补充

包过滤文件格式：

``` sql
[CLIENTS DROP|ACCEPT]
{+|-}common_name1
{+|-}common_name2
 . . .
[SUBNETS DROP|ACCEPT]
{+|-}subnet1
{+|-}subnet2
 . . .
[END]


过滤文件语法：
CLIENTS部分用于定义common name；
SUBNETS部分用于定义IP地址、IP网段；
DROP|ACCEPT用于设置默认规则，就是没有明确指明的common name，那么他们将会使用；
{+|-}用于设置是否允许，如果是“+”，那么表示允许，如果是“-”则表示不允许；
[END]表示策略文件的结束


cat client10.pf
[CLIENTS ACCEPT]
[SUBNETS ACCEPT]
-192.168.9.7
+192.168.9.0/24
[END]
```

> 注意事项：
> 
> 创建过滤文件时，允许访问的地址写到上面，禁止访问的地址写在后面。如果先禁止访问网段，在允许访问网段IP地址，依然受限。
> 
> 例如：
> ![enter description here](1.png)



## 3.4 创建客户端连接脚本

``` vim
cd /etc/openvpn

vim client-connect.sh
```



``` bash
#!/bin/sh
 
# /etc/openvpn/client-connect.sh: sample client-connect script using pf rule files
 
# rules template file
template="/etc:wq/openvpn/ccd/${common_name}.pf"
 
# create the file OpenVPN wants with the rules for this client
if [ -f "$template" ] && [ ! -z "$pf_file" ]; then
  cp -- "$template" "$pf_file"
else
  # if anything is not as expected, fail
  exit 1
fi
```


## 3.5 修改openvpn配置文件

``` vim
vim /etc/openvpn/server.conf
```


``` maxima
ca /etc/openvpn/easy-rsa/keys/ca.crt
cert /etc/openvpn/easy-rsa/keys/server.crt
key /etc/openvpn/easy-rsa/keys/server.key
dh /etc/openvpn/easy-rsa/keys/dh2048.pem
server 10.8.0.0 255.255.255.0
ifconfig-pool-persist ipp.txt
;server-bridge 10.8.0.4 255.255.255.0 10.8.0.50 10.8.0.100
;push "redirect-gateway def1 bypass-dhcp"
;push "redirect-gateway"
;push "dhcp-option DNS 172.20.20.10"
;push "dhcp-option DNS 202.102.224.68"
;push "route 0.0.0.0 0.0.0.0"
push "route 172.20.20.0 255.255.255.0"
push "route 172.20.22.0 255.255.255.0"
push "route 172.20.10.0 255.255.255.0"
push "route 172.20.19.0 255.255.255.0"
push "route 10.224.255.224 255.255.255.224"
;push "route 172.20.18.0 255.255.255.0"
;push "route 172.20.17.0 255.255.255.0"
;push "dhcp-option DNS 172.20.20.10"
;push "dhcp-option DNS 202.102.224.68"
client-to-client
duplicate-cn
keepalive 10 120
#tls-auth /etc/openvpn/easy-rsa/ta.key 0
comp-lzo
max-clients 10
persist-key
persist-tun
status openvpn-status.log
log        /var/log/openvpn.log
log-append /var/log/openvpn-append.log
verb 3
plugin /usr/lib64/openvpn/plugin/lib/openvpn-auth-ldap.so "/etc/openvpn/auth/ldap.conf"
client-cert-not-required
username-as-common-name
client-config-dir /etc/openvpn/ccd          #添加
plugin /etc/openvpn/minimal_pf.so           #添加                        
client-connect /etc/openvpn/client-connect.sh       #添加
#script-security 3
```


## 3.6 重启openvpn服务器

``` maxima
/etc/init.d/openvpn restart
```

配置完成。