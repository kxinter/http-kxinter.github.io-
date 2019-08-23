---
title: zabbix在php7下安装always-populate-raw-post-data=-1问题
tags:
  - zabbix
categories:
  - 自动化运维
copyright: true
date: 2018-09-10 16:55:44
---

 ![1](1.png)                                            
<!--more-->
LNMP 平台 php7 ，`zabbix 安装`可能会出现的问题` always-populate-raw-post-data = -1`，解决方案：

``` groovy
vim /目录/zabbix/include/classes/setup/CFrontendSetup.php
```

找到下面代码、关于`always-populate-raw-post-data`;
添加 

``` php
$current = -1;
 
public function checkPhpAlwaysPopulateRawPostData() {
                $current = ini_get('always_populate_raw_post_data');
                $current = -1;
                return array(
                        'name' => _('PHP always_populate_raw_post_data'),
                        'current' => ($current != -1) ? _('on') : _('off'),
                        'required' => _('off'),
                        'result' => ($current != -1) ? self::CHECK_FATAL : self::CHECK_OK,
                        'error' => _('PHP always_populate_raw_post_data must be set to -1.')
                );
        }
```

重新刷新 zabbix 安装页面即可；



