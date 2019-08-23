---
title: Mediawiki优化
tags:
  - mediawiki
  - wiki
categories:
  - Linux
date: 2018-09-07 14:29:55
---

# 1 修改URL后缀
<!--more-->
修改网址显示（`http://172.20.20.21/mediawiki/首页`改为`http://172.20.20.21/首页`）

 - 修改/opt/mediawiki-1.26.2-2/apps/mediawiki/htdocs/ LocalSettings.php文件

``` shell
$wgArticlePath = "/mediawiki/$1";

改为

$wgArticlePath = "/$1";
```

 - 再修改/opt/mediawiki-1.26.2-2/apache2/conf/bitnami/bitnami.conf

``` subunit
<VirtualHost _default_:80>

DocumentRoot "/opt/mediawiki-1.26.2-2/apache2/htdocs"

<Directory "/opt/mediawiki-1.26.2-2/apache2/htdocs">

改为

<VirtualHost _default_:80>

DocumentRoot "/opt/mediawiki-1.26.2-2/apps/mediawiki/htdocs"

<Directory "/opt/mediawiki-1.26.2-2/apps/mediawiki/htdocs">
```


# 2 修改网站LOGO

## 2.1 右上角logo

**方法一**,替换图片文件。

``` groovy
/opt/mediawiki-1.26.2-2/apps/mediawiki/htdocs/resources/assets/wiki.png
```

**方法二**，修改`LocalSettings.php`文件，重新指定LOGO路径

``` shell
$wgLogo             = "$wgScriptPath/resources/assets/huahe.png";
```

## 2.2 左下角

在配置文件LocalSettings.php中加入如下行即`unset($wgFooterIcons['poweredby']);`

#  3 修改目录悬浮加自动隐藏

让目录悬浮起来，并且在不用时让它自动折叠起来，方便阅读和其他操作。自动折叠通过CSS的hover选择器实现，当鼠标移动到目录上时，目录框自动变大。

代码

先进入到下面页面（也许你需要将localhost替换成其他的）：

http://localhost/mediawiki/index.php/MediaWiki:Common.css

在此页你可以设置全局的css样式，在这里加入如下：

``` css
#toc{
 display: block;
 position: fixed;
 top: 100px;
 right: 0px;
 min-width: 100px;
 max-width: 350px;
 max-height: 20px;
 overflow-y: scroll;
 border: 1px solid #aaa;
 border-radius: 0 0 1px 1px;
 -moz-border-radius: 0 0 1px 1px;
 background: rgba(249,249,249,0.75);
 padding: 12px;
 box-shadow: 0 1px 8px #;
 -webkit-box-shadow: 0 1px 8px #;
 -moz-box-shadow: 0 1px 8px #;
}
 
#toc:hover{
 display: block;
 position: fixed;
 top: 100px;
 right: 0px;
 min-width: 100px;
 max-width: 350px;
 max-height: 500px;
 overflow-y: scroll;
 border: 1px solid #aaa;
 border-radius: 0 0 1px 1px;
 -moz-border-radius: 0 0 1px 1px;
 background: rgba(249,249,249,0.75);
 padding: 12px;
 box-shadow: 0 1px 8px #;
 -webkit-box-shadow: 0 1px 8px #;
 -moz-box-shadow: 0 1px 8px #;
 
}
 
body { overflow-x: hidden;}
```

保存，清除浏览器缓存，看看如何！

简直炫酷！。

**关键点解释**

``` scss
top: 100px;　　目录框到顶部距离

right: 0px;　　   目录框到右边框距离

min-width: 100px;　　目录框最小宽度

max-width: 350px;　　目录框最大宽度

max-height: 500px;　　目录框最大高度

background: rgba(249,249,249,0.75);　　背景色和透明度
```

MediaWiki版本

1.20.2

参考
http://blog.klniu.com/post/mediawiki-floating-directory-and-scroll/ 


