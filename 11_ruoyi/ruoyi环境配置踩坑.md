# Docker + MySQL / Redis 踩坑总结

## 问题1：MySQL 1045 Access denied for user 'root'@'xxx'
**现象**：使用Docker启动MySQL容器之后，代码连接数据库报1045拒绝访问，密码明明配置正确，但一直连不上。

**排查**
1. 确认yml的账号、密码和docker启动设置的环境变量一致，排除配置抄写错误。
2. MySQL8默认认证插件为`caching_sha2_password`，外部程序直接连接容易权限报错。
3. root账号默认只允许容器本地访问，**不允许宿主机外部访问**，即使密码正确依然报1045。

**尝试过的操作**
- 进入容器内部执行SQL授权，修改root访问权限，刷新权限；
- 重置root密码，但Windows‑Docker环境下权限问题依然反复出现。

**最终取舍**
本地练习环境，不想花大量时间纠缠权限兼容问题，我选择暂时把MySQL跑在宿主机Windows，Docker只负责运行Redis，以此绕过容器MySQL授权复杂问题。

**收获反思**
1. MySQL8认证插件发生变化，和老项目驱动存在兼容性；
2. Docker容器内数据库root账号默认不开放外部访问，需要显式授权；
3. 学习项目可以灵活选择：中间件不一定全部丢进Docker，部分组件放宿主机，减少环境排错成本。

---

## 问题2：本机Redis服务未关闭，端口冲突
**现象**：Docker Redis容器显示状态Up，docker ps看端口映射正常，但Spring项目连接Redis超时或者连接失败。

**排查**
1. 容器本身运行正常，进入容器内部可以正常访问redis；
2. 发现Windows系统开机自启了本地Redis服务，已经占用宿主机6379端口；
3. Docker虽然启动容器，但宿主机端口被本机服务抢占，外部程序实际连不到Docker里面的Redis。

**解决**
Windows服务管理器停止本地Redis服务，释放6379端口，Docker Redis才可以正常对外提供服务。

**收获反思**
1. 同一个端口同一时间只能被一个程序占用；
2. 使用Docker部署中间件，要先检查本机是否已经启动相同端口的服务；
3. 遇到“容器显示正常，但是外部连不上”，优先排查宿主机端口占用、防火墙。

---

## 问题3：Redis NOAUTH HELLO 协议兼容报错
**现象**：代码配置没有改动，前一天项目正常启动，第二天启动报 `NOAUTH HELLO must be called with the client already authenticated`。

**排查**
1. yml密码为空，不是账号密码错误；
2. docker run没有写版本，默认拉取`redis:latest`即Redis7；
3. SpringBoot4内置高版本Lettuce，Redis7默认RESP3协议，无密码场景握手存在兼容性bug。

**解决**
停止本机Redis，指定镜像版本 `redis:6` 启动容器，不修改项目原有代码，项目成功启动。

**收获反思**
1. Docker尽量避免使用latest标签，固定镜像版本，防止环境漂移，出现“昨天能跑，今天报错”；
2. 环境类异常优先对比**前后环境差异**，不要直接复制网上命令盲目尝试。
