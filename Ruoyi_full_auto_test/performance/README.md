# JMeter 性能测试

## 测试计划

`RuoYi_login_user_list.jmx` 包含两个请求：

1. `POST /login`：获取 token
2. `GET /system/user/list`：携带 Bearer token 查询用户列表

默认线程组是 5 个并发用户、10 秒 ramp-up、每个用户 2 次循环，适合先做基线，不代表生产压测结论。

## 命令行执行

在安装 JMeter 后，于项目根目录执行：

```powershell
jmeter -n `
  -t performance/RuoYi_login_user_list.jmx `
  -Jhost=localhost `
  -Jport=8081 `
  -Jusername=admin `
  -Jpassword=admin123 `
  -l reports/jmeter-results.jtl `
  -e -o reports/jmeter-html
```

参数含义：

- `-n`：非 GUI 模式
- `-t`：测试计划文件
- `-J`：覆盖 JMeter 属性
- `-l`：保存原始结果
- `-e -o`：生成 HTML 报告

## 执行建议

1. 先用 GUI 模式单线程验证登录和 token 提取。
2. 再用 5 并发建立基线，记录平均响应时间、P90/P95、吞吐量和错误率。
3. 逐步增加并发，不要一开始就对本地环境进行大压力测试。
4. 性能测试应安排在独立测试环境，并保留服务端 CPU、内存、数据库连接数等监控数据。
5. 不把 `reports/jmeter-results.jtl` 和 HTML 报告提交到 Git。
