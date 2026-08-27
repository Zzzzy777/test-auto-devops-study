# RuoYi‑Vue 后端部署笔记（环境准备到数据库初始化）

## 一、所需环境清单
部署RuoYi‑Vue后端需要3个基础服务：
1. JDK8及以上（本项目使用JDK17运行）
2. MySQL 5.7 / 8.0
3. Redis

> 注意：Windows本机部署容易出现Redis兼容性、IDEA缓存异常；Linux虚拟机部署稳定性更高。

## 二、源码获取
1. 从Gitee拉取RuoYi‑Vue源码
2. 解压源码，**避免路径包含中文、空格、特殊符号**
> ❗踩坑：路径带中文会导致IDEA各种莫名报错，项目存放路径全部使用英文。

## 三、MySQL数据库准备
### 1. 创建数据库
登录MySQL客户端，执行SQL创建数据库，数据库名固定为 `ry_vue`
```sql
CREATE DATABASE ry_vue DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
```

### 2. 导入项目 SQL 脚本
#### 源码目录 `ruoyi/sql` 下面存在两个 sql 文件：
1. `ry_vue.sql` 业务数据表
2. `quartz.sql` 定时任务表

> 踩坑记录:
>1. quartz.sql 部分语句报错可以忽略，不影响后台基础功能使用。
>2. MySQL8.0 连接 URL 需要注意 `useSSL=false`、时区 `serverTimezone=GMT%2B8`，否则启动报错。

### 3. 确认数据库账号权限
确认 MySQL 账号可以正常访问 `ry_vue`，账号密码后续要配置到 yml 配置文件。

## 四、Redis 准备
### Docker 启动 Redis（推荐，规避 Windows 版本兼容 bug）
```bash
docker run -d --name redis-ruoyi -p 6379:6379 redis
```

>验证 redis 连通：`redis-cli` 可以正常连接即为成功。

## 五、后端配置文件修改
### 找到 `application-druid.yml`、`application-dev.yml`
1. 修改数据库 url、数据库用户名、数据库密码，和本机 MySQL 保持一致
2. Redis 地址端口默认本机 `127.0.0.1:6379`，无密码则密码留空

## 六、IDEA 项目 JDK 配置
1. File → Project Structure
2. Project SDK 设置为 JDK17，项目语言级别 17
3. 所有子模块 Module 语言级别统一设置为 17
4. Maven 刷新，等待全部依赖下载完成。
>❗踩坑：项目和模块语言级别两处都要修改，只改一处会编译报错。

## 七、下一步
1. 执行 `RuoYiApplication` 启动类，启动 SpringBoot 后端服务；
2. 访问地址：`http://localhost:8081`，默认账号 admin /admin123。