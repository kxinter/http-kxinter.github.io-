---
title: centos7如何进入救援模式_resue
tags:
  - 基础运维
categories:
  - Linux
date: 2018-08-30 11:25:26
---

进入系统开机引导界面，按`↓`键，按`e`键，找到`linux16`开头的行，在后面添加`systemd.unit=rescue.target`,然后按`ctrl+x`来进入系统，就能够进入`rescue`的环境了，输入`帐号及密码`，就可以进行相应操作。