# JMeter 性能测试

测试计划 `RuoYi_login_user_list.jmx` 覆盖一条可用于冒烟和基线测试的登录链路：

1. `POST /login` 登录并提取 `token`；
2. `GET /system/user/list` 携带 `Authorization: Bearer ${token}`；
3. 对 HTTP 状态码和 RuoYi 业务响应码进行断言。

## 前置条件

- RuoYi 后端已启动，默认地址为 `http://localhost:8081`；
- JMeter 已安装，并且 `jmeter.bat` 已加入 PATH，或者设置了 `JMETER_HOME`；
- 测试账号有登录和用户列表查询权限。

## 本地冒烟测试：1 线程、1 次循环

先进入项目目录。下面命令会生成 JTL 原始结果和 HTML 报告；HTML 报告必须使用新的空目录。

```powershell
cd D:\运维测试\test-auto-devops-study\Ruoyi-api-ui-auto-test
$jmeter = if ($env:JMETER_HOME) { Join-Path $env:JMETER_HOME 'bin\jmeter.bat' } else { 'jmeter' }
New-Item -ItemType Directory -Force reports\jmeter | Out-Null
if (Test-Path reports\jmeter\smoke-html) { Remove-Item reports\jmeter\smoke-html -Recurse -Force }
& $jmeter -n -t performance\RuoYi_login_user_list.jmx `
  -Jhost=localhost -Jport=8081 `
  -Jusername=admin -Jpassword=admin123 `
  -Jthreads=1 -Jramp_up=1 -Jloops=1 `
  -l reports\jmeter\smoke-result.jtl -e -o reports\jmeter\smoke-html
if ($LASTEXITCODE -ne 0) { throw 'JMeter smoke test failed' }
Start-Process reports\jmeter\smoke-html\index.html
```

打开 `reports/jmeter/smoke-html/index.html`，确认 `登录 POST /login` 和 `查询用户列表 GET /system/user/list` 均为成功。若失败，先查看 JTL 和 JMeter 控制台中实际返回的状态码/响应内容，不要直接修改断言来掩盖问题。

## 本地基线测试：5 线程、2 次循环

```powershell
if (Test-Path reports\jmeter\baseline-html) { Remove-Item reports\jmeter\baseline-html -Recurse -Force }
& $jmeter -n -t performance\RuoYi_login_user_list.jmx `
  -Jhost=localhost -Jport=8081 `
  -Jusername=admin -Jpassword=admin123 `
  -Jthreads=5 -Jramp_up=10 -Jloops=2 `
  -l reports\jmeter\baseline-result.jtl -e -o reports\jmeter\baseline-html
if ($LASTEXITCODE -ne 0) { throw 'JMeter baseline test failed' }
python performance\check_jtl.py `
  --jtl reports\jmeter\baseline-result.jtl `
  --max-error-rate 0 `
  --max-p95-ms 2000
```

`check_jtl.py` 会从真实 JTL 计算并打印：样本数、成功数、失败数、错误率、平均响应时间、P90/P95/P99 和近似吞吐量。当错误率或 P95 超过阈值时返回非 0，适合作为 CI 质量门禁。脚本不会生成或伪造性能数据。

## 参数说明

测试计划通过 JMeter 属性支持覆盖：

- `host`：后端主机名；
- `port`：后端端口；
- `username` / `password`：登录账号；
- `threads`：并发线程数，默认 5；
- `ramp_up`：启动时间（秒），默认 10；
- `loops`：每个线程循环次数，默认 2。

JMX 中对应 `${__P(threads,5)}`、`${__P(ramp_up,10)}` 和 `${__P(loops,2)}`，命令行的 `-J` 值会覆盖默认值。

## 结果记录

只记录实际执行结果：样本数、TPS/吞吐量、平均响应时间、P90/P95/P99、错误率，以及 CPU、内存、JVM、数据库连接池和慢 SQL。不要把未经运行的数字写入 README、简历或面试材料。