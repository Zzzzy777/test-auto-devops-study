# RuoYi 全链路自动化测试项目

## 1. 项目定位

这是一个面向测试工程师/测试开发工程师岗位的自动化测试项目，围绕 RuoYi 后台的用户管理模块，覆盖：

- Playwright + pytest：浏览器 UI 自动化
- Requests + pytest：接口自动化
- MySQL：可选的数据校验与辅助清理
- Allure/JUnit：测试报告
- Jenkins：持续集成
- JMeter：登录与用户查询接口的性能测试模板

项目重点不是“写几个脚本”，而是展示一套可维护的测试工程：Page Object、接口封装、动态测试数据、失败截图、日志、报告和 CI。

## 2. 被测环境

| 服务 | 默认地址 | 说明 |
|---|---|---|
| RuoYi 前端 | `http://localhost:82` | Playwright 访问 |
| RuoYi 后端 API | `http://localhost:8081` | Requests/JMeter 访问 |
| Jenkins | `http://localhost:8080` | CI 服务，不是 RuoYi API |

如果你的端口不同，不修改测试代码，优先通过环境变量覆盖。

## 3. 目录结构

```text
Ruoyi_full_auto_test/
├─ common/                         配置、日志、测试数据、API 客户端
├─ pages/                          Playwright Page Object
├─ test_ui/                        UI 自动化用例
├─ test_api/                       API 自动化用例
├─ performance/                    JMeter 性能测试计划
├─ docs/                           测试计划、用例、缺陷、CI 文档
├─ reports/                        运行时报告（已加入 .gitignore）
├─ conftest.py                     全局 fixture、失败截图
├─ pytest.ini                      pytest 配置
├─ Jenkinsfile                     Windows Agent CI 流水线
├─ requirements.txt                Python 依赖
└─ .env.example                    环境变量示例
```

## 4. 当前自动化场景

### UI 场景

1. 管理员登录
2. 新增用户成功
3. 新增用户必填项校验
4. 重复用户名校验
5. 用户搜索
6. 编辑用户并校验修改结果

### API 场景

1. 登录成功/登录失败
2. 用户查询与详情查询
3. 新增用户
4. 重复用户名异常
5. 修改用户
6. 删除用户并校验删除结果
7. 删除不存在用户异常

测试数据使用 `ui_test_`、`api_test_` 等前缀和 UUID 生成，测试结束后通过 API 清理，避免污染环境。

## 5. 安装与运行

在项目根目录执行：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m playwright install chromium
```

### 本地 headed 调试

```powershell
pytest test_ui/test_ruoyi_login.py -s --headed --slowmo=600
pytest test_ui/test_ruoyi_user_add.py -s --headed --slowmo=600
pytest test_ui -s --headed --slowmo=600
```

### API 与 UI 全量回归（headless）

不传 `--headed` 即为 headless：

```powershell
$env:PYTHONUTF8 = "1"
pytest test_ui test_api `
  --browser chromium `
  --alluredir=reports/allure-results `
  --junitxml=reports/junit.xml `
  -ra --tb=short
```

### 查看 Allure 报告

```powershell
allure serve reports/allure-results
```

## 6. 环境变量

可复制 `.env.example` 为本地配置参考，或直接设置环境变量：

```powershell
$env:RUOYI_FRONTEND_BASE_URL = "http://localhost:82"
$env:RUOYI_API_BASE_URL = "http://localhost:8081"
$env:RUOYI_UI_USERNAME = "admin"
$env:RUOYI_UI_PASSWORD = "admin123"
$env:RUOYI_API_USERNAME = "admin"
$env:RUOYI_API_PASSWORD = "admin123"
```

不要把真实账号密码提交到 Git，Jenkins 中使用 Credentials 或 Job 环境变量注入。

## 7. Jenkins 流水线

`Jenkinsfile` 面向 Windows Jenkins Agent，流程包括：

1. 检查前端 82 和后端 8081 端口
2. 安装 Python 依赖和 Chromium
3. headless 执行 UI/API 测试
4. 生成 JUnit 与 Allure 结果
5. 归档日志、失败截图和测试报告

详细配置步骤见 `docs/jenkins_setup.md`。

## 8. 性能测试

`performance/RuoYi_login_user_list.jmx` 是可导入 JMeter 的基础测试计划，覆盖：

- 登录接口 `POST /login`
- 用户列表接口 `GET /system/user/list`
- 登录响应 token 提取并作为后续请求的 Bearer Token
- HTTP 状态码与业务 `code=200` 断言

运行方式见 `performance/README.md`。第一次执行建议使用 5 并发、每次 2 个循环，确认脚本和环境无误后再逐步加压。

## 9. 已验证结果

在 RuoYi 前后端服务正常启动的环境中，最近一次等价 CI 命令验证结果为：

```text
13 passed
```

报告产物：

```text
reports/junit.xml
reports/allure-results/
reports/logs/pytest.log
```

## 10. 面试讲解重点

建议按以下顺序讲项目：

1. 先说明业务模块和风险点：登录、用户新增、重复数据、编辑、删除
2. 解释为什么 UI 与 API 分工：UI 验证真实用户流程，API 负责快速查询和清理数据
3. 说明如何保证重复执行：UUID 动态数据 + `try/finally` 清理
4. 说明 Page Object 如何降低定位器和业务步骤耦合
5. 说明失败时如何定位：pytest 日志、Allure 附件、失败截图、JUnit
6. 说明 Jenkins 如何做到无人值守回归，以及 JMeter 如何验证接口性能

项目中可以使用 AI 辅助查错和生成初稿，但你必须能够独立解释：定位器选择、接口鉴权、断言设计、数据清理、CI 参数和失败排查过程。
