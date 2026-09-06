# JMeter 性能测试

测试计划 `RuoYi_login_user_list.jmx` 覆盖：

1. `POST /login` 登录并提取 `token`；
2. `GET /system/user/list` 携带 `Authorization: Bearer ${token}`；
3. HTTP 和业务响应断言。

## 命令

```powershell
$jmeter = if ($env:JMETER_HOME) { Join-Path $env:JMETER_HOME 'bin\jmeter.bat' } else { 'jmeter' }
New-Item -ItemType Directory -Force reports\jmeter | Out-Null
& $jmeter -n -t performance\RuoYi_login_user_list.jmx `
  -Jhost=localhost -Jport=8081 `
  -Jusername=admin -Jpassword=admin123 `
  -Jthreads=5 -Jramp_up=10 -Jloops=2 `
  -l reports\jmeter\result.jtl -e -o reports\jmeter\html
```

变量：`host`、`port`、`username`、`password`；JMeter GUI 中的默认线程组为 5 线程、10 秒启动、每线程 2 次循环。若需要覆盖线程/循环，建议把测试计划中的线程组改为 `${__P(threads,5)}` 和 `${__P(loops,2)}` 后再使用命令行参数；当前计划的地址和账号参数已支持 `-J` 覆盖。

## 结果记录

只记录实际执行结果：样本数、TPS、平均响应时间、P90/P95/P99、错误率，以及 CPU、内存、JVM、数据库连接池和慢 SQL。不要把未经运行的数字写入简历。
