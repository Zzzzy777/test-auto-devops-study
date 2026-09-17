# Mall 电商系统本地部署说明

## 1. 服务端口

| 服务 | 端口 |
|---|---:|
| 项目 1 后端 | 8081（本项目不占用） |
| 项目 1 前端 | 82（本项目不占用） |
| 项目 2 mall-admin 后端 | 8082 |
| 项目 2 mall-portal 后端 | 8085 |
| 项目 2 后台前端 | 8090 |
| 项目 2 商城 H5 前端 | 8060 |
| MySQL 容器 | 3307 |
| Redis 容器 | 6380 |
| MongoDB 容器 | 27017 |
| RabbitMQ 服务 | 5672 |
| RabbitMQ 管理页面 | 15672 |

## 2. 访问地址

- 后台管理页面：<http://localhost:8090>
- 商城 H5 页面：<http://localhost:8060>
- RabbitMQ 管理页面：<http://localhost:15672>
- 后台健康检查：<http://localhost:8082/actuator/health>
- 商城后端健康检查：<http://localhost:8085/actuator/health>

本地示例账号：

```text
后台账号：admin
后台密码：macro123
商城账号：test
商城密码：123456
RabbitMQ：mall / mall
MySQL：root / 123456
```

以上账号只适用于本地演示数据库。公开部署或生产环境必须修改密码，不要把生产凭据提交到 GitHub。

## 3. 首次构建

在项目根目录执行：

```powershell
powershell -ExecutionPolicy Bypass -File .\setup-and-build.ps1
```

脚本会完成：

1. 构建 Mall 后端 Maven 模块；
2. 安装后台前端依赖并构建；
3. 安装商城前端依赖并构建。

Java、Maven、Node.js、npm 从系统 `PATH` 查找，不依赖某台电脑的固定路径。

## 4. 启动和停止

先启动 Docker Desktop，然后执行：

```powershell
powershell -ExecutionPolicy Bypass -File .\start-all.ps1
```

检查服务：

```powershell
powershell -ExecutionPolicy Bypass -File .\check-all.ps1
```

停止项目服务并保留基础设施容器：

```powershell
powershell -ExecutionPolicy Bypass -File .\stop-all.ps1 -KeepInfrastructure
```

停止项目服务和基础设施容器：

```powershell
powershell -ExecutionPolicy Bypass -File .\stop-all.ps1
```

也可以双击根目录下的：

```text
启动项目2.bat
停止项目2.bat
```

## 5. MySQL 连接说明

本机如果已经有 MySQL 占用 IPv4 的 3307 端口，项目配置可能使用 Docker 的 IPv6 回环地址 `[::1]:3307`。如果数据库连接失败，请检查：

```powershell
docker ps -a
docker logs mall-mysql
```

不要在未确认端口占用情况前随意修改数据库地址。

## 6. 常见问题

### 前端无法访问后端

确认 `source/mall-admin-web/.env.development` 的地址为 `http://localhost:8082`，确认 `source/mall-app-web/.env.development` 的地址为 `http://localhost:8085`，然后重新启动前端。

### 后端无法启动

先检查 Docker 基础设施容器和运行日志：

```powershell
powershell -ExecutionPolicy Bypass -File .\check-all.ps1
Get-ChildItem .\runtime\logs
```

### Jenkins 中无法访问 localhost

Jenkinsfile 默认测试 Jenkins Agent 本机上的服务。如果 Jenkins Agent 和被测服务不在同一台机器，需要把测试配置中的地址改成测试环境 IP 或域名，并确保防火墙允许访问。
