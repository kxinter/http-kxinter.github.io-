---
title: npm私库部署-cnpmjs
tags:
  - cnpmjs
  - 私有仓库
categories:
  - Linux
date: 2018-08-16 18:25:38
---

# 一、部署cnpm
<!--more-->
## 1、获取代码

``` crmsh
git clone git://github.com/fengmk2/cnpmjs.org.git
```

## 2、创建mysql库

Default

``` sql
create database cnpmjs;
use cnpmjs;
source docs/db.sql【db.sql位于cnpmjs.org/docs/db.sql】
```

## 3、安装依赖

安装依赖其实就是一个 npm install，不过 CNPM 把该指令已经写到 Makefile 里面了，所以直接执行下面的命令就好了。
``` shell
$ cd cnpmjs.org 
$ npm install
```
当然万一你是 Windows 用户或者不会 make，那么还是要用 npm install。
``` jboss-cli
$ npm install --build-from-source --registry=https://registry.npm.taobao.org --disturl=https://npm.taobao.org/mirrors/node
```

## 4、修改配置文件

修改配置

``` vim
vim /cnpmjs.org/config/index.js
```
![enter description here](1.png)

cnpm提供两个端口：7001和7002，其中7001用于NPM的注册服务，7002用于Web访问。

bindingHost为安装cnpm的服务器ip地址，也就是在浏览器中只能通过访问http://192.168.48.57来访问cnpm以及获取npm的注册服务。

![2](2.png)
按照之前创建的数据库来进行配置

这里将会列举一些常用的配置项，其余的一些配置项请自行参考 config/index.js 文件。

### 配置字段参考

https://segmentfault.com/a/1190000005946580

``` dsconfig
enableCluster：是否启用 cluster-worker 模式启动服务，默认 false，生产环节推荐为 true;
registryPort：API 专用的 registry 服务端口，默认 7001；
webPort：Web 服务端口，默认 7002；
bindingHost：监听绑定的 Host，默认为 127.0.0.1，如果外面架了一层本地的 Nginx 反向代理或者 Apache 反向代理的话推荐不用改；
sessionSecret：session 用的盐；
logdir：日志目录；
uploadDir：临时上传文件目录；
viewCache：视图模板缓存是否开启，默认为 false；
enableCompress：是否开启 gzip 压缩，默认为 false；
admins：管理员们，这是一个 JSON Object，对应各键名为各管理员的用户名，键值为其邮箱，默认为 { fengmk2: 'fengmk2@gmail.com', admin: 'admin@cnpmjs.org', dead_horse: 'dead_horse@qq.com' }；
logoURL：Logo 地址，不过对于我这个已经把 CNPM 前端改得面目全非的人来说已经忽略了这个配置了；
adBanner：广告 Banner 的地址；
customReadmeFile：实际上我们看到的 cnpmjs.org 首页中间一大堆冗长的介绍是一个 Markdown 文件转化而成的，你可以设置该项来自行替换这个文件；
customFooter：自定义页脚模板；
npmClientName：默认为 cnpm，如果你有自己开发或者 fork 的 npm 客户端的话请改成自己的 CLI 命令，这个应该会在一些页面的说明处替换成你所写的；
backupFilePrefix：备份目录；
database：数据库相关配置，为一个对象，默认如果不配置将会是一个 ~/.cnpmjs.org/data.sqlite 的 SQLite；
db：数据的库名；
username：数据库用户名；
password：数据库密码；
dialect：数据库适配器，可选 "mysql"、"sqlite"、"postgres"、"mariadb"，默认为 "sqlite"；
hsot：数据库地址；
port：数据库端口；
pool：数据库连接池相关配置，为一个对象；
maxConnections：最大连接数，默认为 10；
minConnections：最小连接数，默认为 0；
maxIdleTime：单条链接最大空闲时间，默认为 30000 毫秒；
storege：仅对 SQLite 配置有效，数据库地址，默认为 ~/.cnpmjs/data.sqlite；
nfs：包文件系统处理对象，为一个 Node.js 对象，默认是 [fs-cnpm]() 这个包，并且配置在 ~/.cnpmjs/nfs 目录下，也就是说默认所有同步的包都会被放在这个目录下；开发者可以使用别的一些文件系统插件（如上传到又拍云等）,又或者自己去按接口开发一个逻辑层，这些都是后话了；
registryHost：暂时还未试过，我猜是用于 Web 页面显示用的，默认为 r.cnpmjs.org；
enablePrivate：是否开启私有模式，默认为 false；
如果是私有模式则只有管理员能发布包，其它人只能从源站同步包；
如果是非私有模式则所有登录用户都能发布包；
scopes：非管理员发布包的时候只能用以 scopes 里面列举的命名空间为前缀来发布，如果没设置则无法发布，也就是说这是一个必填项，默认为 [ '@cnpm', '@cnpmtest', '@cnpm-test' ]，据苏千大大解释是为了便于管理以及让公司的员工自觉按需发布；更多关于 NPM scope 的说明请参见 npm-scope；
privatePackages：就如该配置项的注释所述，出于历史包袱的原因，有些已经存在的私有包（可能之前是用 Git 的方式安装的）并没有以命名空间的形式来命名，而这种包本来是无法上传到 CNPM 的，这个配置项数组就是用来加这些例外白名单的，默认为一个空数组；
sourceNpmRegistry：更新源 NPM 的 registry 地址，默认为 https://registry.npm.taobao.org；
sourceNpmRegistryIsCNpm：源 registry 是否为 CNPM，默认为 true，如果你使用的源是官方 NPM 源，请将其设为 false；
syncByInstall：如果安装包的时候发现包不存在，则尝试从更新源同步，默认为 true；
syncModel：更新模式（不过我觉得是个 typo），有下面几种模式可以选择，默认为 "none";
"none"：永不同步，只管理私有用户上传的包，其它源包会直接从源站获取；
"exist"：定时同步已经存在于数据库的包；
"all"：定时同步所有源站的包；
syncInterval：同步间隔，默认为 "10m" 即十分钟；
syncDevDependencies：是否同步每个包里面的 devDependencies 包们，默认为 false；
badgeSubject：包的 badge 显示的名字，默认为 cnpm；
userService：用户验证接口，默认为 null，即无用户相关功能也就是无法有用户去上传包，该部分需要自己实现接口功能并配置，如与公司的 Gitlab 相对接，这也是后话了；
alwaysAuth：是否始终需要用户验证，即便是 $ cnpm install 等命令；
httpProxy：代理地址设置，用于你在墙内源站在墙外的情况。
```

下面是index.js配置实例：

``` js
'use strict';

var mkdirp = require('mkdirp');
var copy = require('copy-to');
var path = require('path');
var fs = require('fs');
var os = require('os');

var version = require('../package.json').version;

var root = path.dirname(__dirname);
var dataDir = path.join(process.env.HOME || root, '.cnpmjs.org');

var config = {
  version: version,
  dataDir: dataDir,

  /**
   * Cluster mode
   */
  enableCluster: false,
  numCPUs: os.cpus().length,

  /*
   * server configure
   */
  //cnpm提供两个端口：7001和7002，其中7001用于NPM的注册服务，7002用于Web访问。
  registryPort: 7001,
  webPort: 7002,
  //bindingHost为安装cnpm的服务器ip地址，也就是在浏览器中只能通过访问http://192.168.48.57来访问cnpm以及获取npm的注册服务。
  bindingHost: '192.168.1.12', // only binding on 127.0.0.1 for local access

  // debug mode
  // if in debug mode, some middleware like limit wont load
  // logger module will print to stdout
  debug: process.env.NODE_ENV === 'development',
  // page mode, enable on development env
  pagemock: process.env.NODE_ENV === 'development',
  // session secret
  sessionSecret: 'cnpmjs.org test session secret',
  // max request json body size
  jsonLimit: '10mb',
  // log dir name
  logdir: path.join(dataDir, 'logs'),
  // update file template dir
  uploadDir: path.join(dataDir, 'downloads'),
  // web page viewCache
  viewCache: false,

  // config for koa-limit middleware
  // for limit download rates
  limit: {
    enable: false,
    token: 'koa-limit:download',
    limit: 1000,
    interval: 1000 * 60 * 60 * 24,
    whiteList: [],
    blackList: [],
    message: 'request frequency limited, any question, please contact fengmk2@gmail.com',
  },

  enableCompress: false, // enable gzip response or not

  // default system admins
  admins: {
    // name: email
    fengmk2: 'fengmk2@gmail.com',
    admin: 'admin@cnpmjs.org',
    dead_horse: 'dead_horse@qq.com',
  },

  // email notification for errors
  // check https://github.com/andris9/Nodemailer for more informations
  mail: {
    enable: false,
    appname: 'cnpmjs.org',
    from: 'cnpmjs.org mail sender <adderss@gmail.com>',
    service: 'gmail',
    auth: {
      user: 'address@gmail.com',
      pass: 'your password'
    }
  },

  logoURL: 'https://os.alipayobjects.com/rmsportal/oygxuIUkkrRccUz.jpg', // cnpm logo image url
  adBanner: '',
  customReadmeFile: '', // you can use your custom readme file instead the cnpm one
  customFooter: '', // you can add copyright and site total script html here
  npmClientName: 'cnpm', // use `${name} install package`
  packagePageContributorSearch: true, // package page contributor link to search, default is true

  // max handle number of package.json `dependencies` property
  maxDependencies: 200,
  // backup filepath prefix
  backupFilePrefix: '/cnpm/backup/',

  /**
   * database config
   */
  //配置数据库连接信息
  database: {
    db: 'cnpm',
    username: 'root',
    password: '123456',

    // the sql dialect of the database
    // - currently supported: 'mysql', 'sqlite', 'postgres', 'mariadb'
    dialect: 'mysql',

    // custom host; default: 127.0.0.1
    host: '192.168.1.12',

    // custom port; default: 3306
    port: 3306,

    // use pooling in order to reduce db connection overload and to increase speed
    // currently only for mysql and postgresql (since v1.5.0)
    pool: {
      maxConnections: 10,
      minConnections: 0,
      maxIdleTime: 30000
    },

    // the storage engine for 'sqlite'
    // default store into ~/.cnpmjs.org/data.sqlite
    storage: path.join(dataDir, 'data.sqlite'),

    logging: !!process.env.SQL_DEBUG,
  },

  // package tarball store in local filesystem by default
  nfs: require('fs-cnpm')({
    dir: path.join(dataDir, 'nfs')
  }),
  // if set true, will 302 redirect to `nfs.url(dist.key)`
  downloadRedirectToNFS: false,

  // registry url name
  registryHost: 'r.cnpmjs.org',

  /**
   * registry mode config
   */

  // enable private mode or not
  // private mode: only admins can publish, other users just can sync package from source npm
  // public mode: all users can publish
  enablePrivate: false,

  // registry scopes, if don't set, means do not support scopes
  scopes: [ '@cnpm', '@cnpmtest', '@cnpm-test' ],

  // some registry already have some private packages in global scope
  // but we want to treat them as scoped private packages,
  // so you can use this white list.
  privatePackages: [],

  /**
   * sync configs
   */

  // the official npm registry
  // cnpm wont directly sync from this one
  // but sometimes will request it for some package infomations
  // please don't change it if not necessary
  officialNpmRegistry: 'https://registry.npmjs.com',
  officialNpmReplicate: 'https://replicate.npmjs.com',

  // sync source, upstream registry
  // If you want to directly sync from official npm's registry
  // please drop them an email first
  sourceNpmRegistry: 'https://registry.npm.taobao.org',

  // upstream registry is base on cnpm/cnpmjs.org or not
  // if your upstream is official npm registry, please turn it off
  sourceNpmRegistryIsCNpm: true,

  // if install return 404, try to sync from source registry
  syncByInstall: true,

  // sync mode select
  // none: do not sync any module, proxy all public modules from sourceNpmRegistry
  // exist: only sync exist modules
  // all: sync all modules
  //配置从仓库同步到本地（重要）
  syncModel: 'exist', // 'none', 'all', 'exist'

  syncConcurrency: 1,
  // sync interval, default is 10 minutes
  syncInterval: '10m',

  // sync polular modules, default to false
  // because cnpm can't auto sync tag change for now
  // so we want to sync popular modules to ensure their tags
  syncPopular: false,
  syncPopularInterval: '1h',
  // top 100
  topPopular: 100,

  // sync devDependencies or not, default is false
  syncDevDependencies: false,
  // try to remove all deleted versions from original registry
  syncDeletedVersions: true,

  // changes streaming sync
  syncChangesStream: false,
  handleSyncRegistry: 'http://127.0.0.1:7001',

  // badge subject on http://shields.io/
  badgePrefixURL: 'https://img.shields.io/badge',
  badgeSubject: 'cnpm',

  // custom user service, @see https://github.com/cnpm/cnpmjs.org/wiki/Use-Your-Own-User-Authorization
  // when you not intend to ingegrate with your company's user system, then use null, it would
  // use the default cnpm user system
  userService: null,

  // always-auth https://docs.npmjs.com/misc/config#always-auth
  // Force npm to always require authentication when accessing the registry, even for GET requests.
  alwaysAuth: false,

  // if you're behind firewall, need to request through http proxy, please set this
  // e.g.: `httpProxy: 'http://proxy.mycompany.com:8080'`
  httpProxy: null,

  // snyk.io root url
  snykUrl: 'https://snyk.io',

  // https://github.com/cnpm/cnpmjs.org/issues/1149
  // if enable this option, must create module_abbreviated and package_readme table in database
  //enableAbbreviatedMetadata: false,
  //配置enableAbbreviatedMetadata为true（默认false）,解决不能同步。重要！
  enableAbbreviatedMetadata: true,

  // global hook function: function* (envelope) {}
  // envelope format please see https://github.com/npm/registry/blob/master/docs/hooks/hooks-payload.md#payload
  globalHook: null,

  opensearch: {
    host: '',
  },
};

if (process.env.NODE_ENV === 'test') {
  config.enableAbbreviatedMetadata = true;
}

if (process.env.NODE_ENV !== 'test') {
  var customConfig;
  if (process.env.NODE_ENV === 'development') {
    customConfig = path.join(root, 'config', 'config.js');
  } else {
    // 1. try to load `$dataDir/config.json` first, not exists then goto 2.
    // 2. load config/config.js, everything in config.js will cover the same key in index.js
    customConfig = path.join(dataDir, 'config.json');
    if (!fs.existsSync(customConfig)) {
      customConfig = path.join(root, 'config', 'config.js');
    }
  }
  if (fs.existsSync(customConfig)) {
    copy(require(customConfig)).override(config);
  }
}

mkdirp.sync(config.logdir);
mkdirp.sync(config.uploadDir);

module.exports = config;

config.loadConfig = function (customConfig) {
  if (!customConfig) {
    return;
  }
  copy(customConfig).override(config);
};
```

## 5、启动服务

搞好配置之后就可以直接启动服务了。
``` crmsh
$ node dispatch.js
```
### 官方脚本启动

官方的其它一些指令，比如你可以用 NPM 的 script 来运行。

``` shell
$ npm run start
```

> 在 CNPM 里面，npm script 还有下面几种指令

``` dockerfile
npm run dev：调试模式启动；
npm run test：跑测试；
npm run start：启动 CNPM；
npm run status：查看 CNPM 启动状态；
npm run stop：停止 CNPM。
```

## 6、访问cnpm

http://192.168.1.12:7002/
![enter description here](3.png)
# 二、问题总结

## 问题1：安装cnmp依赖问题

npm 默认使用官方源（国外），速度慢,已报错；可以安装cnpm，使用cnpm install安装（淘宝源）

Default

``` gams
//安装cnpm
 $ npm install -g cnpm --registry=https://registry.npm.taobao.org
//使用cnpm执行安装依赖命令
 $ cnpm install
```
## 问题2：设置同步后报错

设置同步后，syncModel设置为exist或all,通过仓库下载模块报如下错误

 

``` shell
[c#0] [error] [connect] sync error: TypeError: Cannot read property ‘findAll’ of null
```

**解决办法：**

在index.js文件内设置enableAbbreviatedMetadata: true，问题解决。

参考：https://github.com/cnpm/cnpmjs.org/issues/1236