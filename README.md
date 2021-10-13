# kubernetes_admin 基于django和vue的k8s管理平台

[![Python3](https://img.shields.io/badge/python-3.6-green.svg?style=plastic)](https://www.python.org/)
[![Django](https://img.shields.io/badge/django-2.1-brightgreen.svg?style=plastic)](https://www.djangoproject.com/)
[![Paramiko](https://img.shields.io/badge/paramiko-2.4.1-green.svg?style=plastic)](http://www.paramiko.org/)

kubernetes_admin 使用 Python / Django 进行开发,使用了vue做为前端驱动，配置了web Terminal 功能.

注: [www.sadlar.cn](http://www.sadlar.cn) 是我的博客,欢迎关注。

## 核心功能列表

<table>
  <tr>
    <td> 功能: </td><td>解释:</td>
  </tr>
  <tr>
    <td> Ldap统一登录 </td><td>结合ldap，登录设置</td>
  </tr>
  <tr>
    <td> 便捷访问 </td> <td>登录容器内部执行命令，查看容器log</td>
  </tr>
  <tr>
    <td> 方便管理 </td> <td>节点信息，部署集，有状态副本集，服务网关的查看，更新和删除</td>
  </tr>
  <tr>
    <td> 一键立项轻松上云 </td>  <td>自动立项，组员提出申请，组长审批，执行，一键迁移传统业务上云。</td>
  </tr>

</table>

## 安装及使用指南
``` bash
git clone git@git.fengjr.inc:lei.dong/kubernetes_admin.git
cd kubernetes_admin
./build.sh prod #部署生产环境
./build.sh beta #部署beta环境
```

``` bash
migrate 设置默认环境 default = 
setting.py 
APPENV = os.environ.get('APPENV',default='beta')
```# kubernetes_admin
