# Docker基础实操
## 学习目标
1. 理解Docker镜像、容器核心概念
2. 使用docker run启动mysql容器，掌握端口映射原理
3. 掌握容器日常基础命令实操
4. 掌握MySQL容器账号授权、权限配置
5. 记录两套环境踩坑：Windows Docker Desktop、Ubuntu虚拟机Docker实操故障

## 1、核心概念
|名词|说明|
|----|----|
|镜像(image)|打包好的应用模板（比如mysql5.7/mysql8.0镜像），只读模板，用来创建容器|
|容器(container)|镜像运行起来的实例，可读写；同一个镜像可以启动多个相互独立容器|
|端口映射 `-p`|把宿主机端口映射到容器内部端口，让外部网络可以访问容器内部服务；格式`宿主机端口:容器内部端口`|

>重点提示：Windows Docker Desktop(WSL2后端)网络行为特殊，宿主机localhost访问映射端口，客户端来源IP不是普通外网IP，会造成MySQL权限匹配异常。

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
# 删除容器（容器必须先停止，-f强制删除）
docker rm -f mysql-test
# 进入容器内部终端
docker exec -it mysql-test bash
# 容器内直接登录mysql
docker exec -it mysql-test mysql -uroot -p123456
```

### Linux 额外排查命令（Ubuntu 虚拟机）
```bash
# 查看docker服务状态
systemctl status docker
# 查看docker详细服务日志，排查启动失败
journalctl -xeu docker.service
# 查看容器运行日志
docker logs mysql-test
# 查看镜像加速器配置
docker info
```

## 3、MySQL 容器用户授权实操
```sql
-- 创建允许任意IP访问用户
CREATE USER 'test'@'%' IDENTIFIED WITH mysql_native_password BY '123456';
-- 授予全部权限
GRANT ALL PRIVILEGES ON *.* TO 'test'@'%';
FLUSH PRIVILEGES;
```

## 4、踩坑记录一：Windows Docker Desktop 1045 Access denied
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

## 5、踩坑记录二：Ubuntu 虚拟机 Docker 实操故障
>实操目标：迁移到 Ubuntu 虚拟机，在 Linux 环境完成 MySQL 容器练习，规避 Windows 的网络兼容问题。

### 故障 1：daemon.json JSON 语法错误导致 Docker 服务启动失败
- 现象:编辑`/etc/docker/daemon.json`配置镜像加速器，JSON 出现符号错误（多余逗号、中文符号），执行`systemctl restart docker`服务启动失败；所有 docker 命令报错`Cannot connect to the Docker daemon`。
- 排查步骤
1. `systemctl status docker`看到服务状态为 failed。
2. 使用`journalctl -xeu docker.service`查看服务日志，定位为配置文件 JSON 解析失败。
3. 重写 daemon.json，严格使用英文半角 JSON 格式，不写注释、不出现多余逗号。
4. 执行`systemctl daemon-reload`，再重启 docker 服务。
5. 验证`systemctl status docker`状态为`active(running)`。

### 故障 2：热点网络环境，无法拉取 MySQL 镜像
- 现象:Docker 服务正常，镜像加速器配置完成，执行`docker pull mysql:8.0` / `docker pull mysql:5.7`，报`connection refused`连接拒绝。更换阿里云、中科大多个国内镜像源，依旧无法拉取镜像。
- 排查:
1. `docker info`确认镜像加速器配置已经加载成功，配置文件本身无语法错误。
2. 判断：虚拟机使用手机热点上网，DNS、外网访问存在网络限制，无法访问镜像仓库。