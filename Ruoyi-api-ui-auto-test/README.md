# RuoYi 一体化质量保障与持续集成项目

本项目把 RuoYi 的接口自动化、UI 自动化、JMeter 性能测试和 Jenkins CI 整合到一个可重复运行的测试工程中。

## 能力范围

- Requests + Pytest：登录、用户、角色、菜单、部门、权限和业务链路；
- Playwright：登录、用户新增、查询、编辑、重复数据和必填校验；
- JMeter：登录获取 token，并携带 token 查询用户列表；
- Allure/JUnit：测试结果、日志、失败截图和 CI 归档；
- 动态测试数据：`api_test_`、`ui_test_`、`api_test_role_` 前缀，测试后自动清理。

## 目录

```text
common/                 配置、HTTP 客户端、业务 API Client、数据工厂
pages/                  Playwright Page Object
test_api/               接口自动化
test_ui/                UI 自动化
performance/            JMeter 测试计划和说明
reports/                运行时报告（自动生成，不提交 Git）
conftest.py             全局失败截图
pytest.ini              pytest 配置
Jenkinsfile             Windows Jenkins 流水线
```

## 前置条件

1. Python 3.10+；
2. RuoYi 前端已启动，默认 `http://localhost:82`；
3. RuoYi 后端已启动，默认 `http://localhost:8081`；
4. 测试账号具备用户、角色、菜单和部门查询/维护权限；
5. `RUOYI_DEFAULT_DEPT_ID` 必须是当前数据库中存在的部门 ID。

如果前后端没有启动，项目可以完成语法检查和用例收集，但真实 API/UI 测试会失败，这是环境未就绪，不是测试框架问题。

## 安装

```powershell
cd D:\auto-test-note\projects\Ruoyi_finally
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m playwright install chromium
```

## 配置

推荐在当前 PowerShell 会话设置环境变量，不要提交真实密码：

```powershell
$env:RUOYI_FRONTEND_BASE_URL = 'http://localhost:82'
$env:RUOYI_API_BASE_URL = 'http://localhost:8081'
$env:RUOYI_UI_USERNAME = 'admin'
$env:RUOYI_UI_PASSWORD = 'admin123'
$env:RUOYI_API_USERNAME = 'admin'
$env:RUOYI_API_PASSWORD = 'admin123'
$env:RUOYI_DEFAULT_DEPT_ID = '105'
```

配置示例见 `.env.example`。项目核心代码直接读取环境变量，不依赖额外的 dotenv 插件。

## 先检查项目本身

```powershell
python -m compileall common pages test_api test_ui conftest.py
python -m pytest --collect-only -q
```

## 运行 API

```powershell
python -m pytest test_api -v --tb=short `
  --alluredir=reports/allure-results `
  --junitxml=reports/api-junit.xml
```

## 运行 UI

无界面回归：

```powershell
python -m pytest test_ui -v --browser chromium --tb=short `
  --alluredir=reports/allure-results `
  --junitxml=reports/ui-junit.xml
```

可视化调试：

```powershell
python -m pytest test_ui -s --headed --slowmo=300 --browser chromium
```

UI 失败截图在 `reports/screenshots/fail/`，日志在 `reports/logs/pytest.log`。

## Allure

安装 Allure CLI 后：

```powershell
allure serve reports/allure-results
```

## JMeter

详细说明见 `performance/README.md`。示例：

```powershell
$jmeter = if ($env:JMETER_HOME) { Join-Path $env:JMETER_HOME 'bin\jmeter.bat' } else { 'jmeter' }
New-Item -ItemType Directory -Force reports\jmeter | Out-Null
& $jmeter -n -t performance\RuoYi_login_user_list.jmx `
  -Jhost=localhost -Jport=8081 `
  -Jusername=admin -Jpassword=admin123 `
  -Jthreads=5 -Jramp_up=10 -Jloops=2 `
  -l reports\jmeter\result.jtl -e -o reports\jmeter\html
```

当前 JMX 使用 `host`、`port`、`username`、`password` 参数；线程数和循环数可以在命令行覆盖。性能结论必须以真实运行数据为准，记录 TPS、平均响应时间、P90/P95/P99、错误率和资源指标。

## Jenkins

`Jenkinsfile` 默认执行 API，可通过参数选择 UI 和 JMeter。流水线要求 Windows Agent 已安装 Python、Playwright/Chromium 和 JMeter，并建议使用 Jenkins Credentials 注入账号密码。凭据 ID 可按你的 Jenkins 实际名称调整。

## 当前用例数量

以 `python -m pytest --collect-only -q` 的实际输出为准。不要在 README 或简历中虚构测试数量、通过率或性能提升比例。
