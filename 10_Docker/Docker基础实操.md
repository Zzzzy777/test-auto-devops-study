# Docker基础实操
## 学习目标
1. 理解Docker镜像、容器概念
2. 使用docker run启动mysql容器，端口映射
3. 容器基础命令实操
4. 踩坑：Windows Docker Desktop连接MySQL报1045拒绝访问

## 1、核心概念
|名词|说明|
|----|----|
|镜像(image)|打包好的应用模板（比如mysql5.7镜像），只读|
|容器(container)|镜像运行起来的实例，可读写，一个镜像可以启动多个容器|
|端口映射 `-p`|把宿主机端口映射到容器内部端口，外部可以访问容器服务|

## 2、常用基础命令
```bash
# 查看本地镜像
docker images

# 查看正在运行容器
docker ps

# 查看全部容器（包含停止的）
docker ps -a

# 启动mysql5.7容器
docker run -d \
--name mysql-test \
-p 3307:3306 \
-e MYSQL_ROOT_PASSWORD=123456 \
mysql:5.7 \
--default-authentication-plugin=mysql_native_password \
--bind-address=0.0.0.0

# 停止容器
docker stop mysql-test

# 启动已经存在的容器
docker start mysql-test

# 删除容器（容器必须先停止）
docker rm -f mysql-test

# 进入容器内部终端
docker exec -it mysql-test bash

# 容器内登录mysql
docker exec -it mysql-test mysql -uroot -p123456
```

## 3、MySQL 容器用户授权实操
```sql
-- 创建允许任意IP访问用户
CREATE USER 'test'@'%' IDENTIFIED WITH mysql_native_password BY '123456';
-- 授予全部权限
GRANT ALL PRIVILEGES ON *.* TO 'test'@'%';
FLUSH PRIVILEGES;
```

## 4、重点踩坑记录 Windows Docker Desktop 1045 Access denied
### 现象：
- 容器内部可以正常登录 MySQL；Windows 本地 pymysql，通过`127.0.0.1:3307`连接，报 1045 访问拒绝。

### 已经做过排查
1. docker run 添加参数 `--bind‑address=0.0.0.0`，容器监听全部网卡
2. 设置 mysql 认证插件为 `mysql_native_password`，适配 pymysql
3. 创建 `test@%` 用户，授权并刷新权限

### 根本原因
- Windows Docker Desktop 环境特殊：宿主机访问映射端口，MySQL 识别客户端来源是`localhost`。
- `test@%`只匹配外部远程 IP，**不匹配[localhost](https://localhost)来源**，所以拒绝登录。

### 解决思路
#### 【企业真实环境】
- **脚本运行在 Linux 虚拟机 / 服务器内部**，在 Linux 内部访问 Docker 容器 MySQL，不会出现该问题。
>实训说明：掌握 docker 启动容器、端口映射、用户授权原理，Windows 本地环境兼容坑可以记录，不必强行跑通。