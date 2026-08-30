# RuoYi Full Auto Test

> 基于 Python 的 RuoYi 用户管理模块自动化测试项目，覆盖 UI 自动化、接口自动化、性能测试与 Jenkins 持续集成。

## 项目简介

本项目以 RuoYi 后台用户管理模块为被测对象，围绕登录、用户新增、查询、编辑、删除及异常校验等核心业务，构建一套可维护、可重复执行、可持续集成的自动化测试工程。

项目采用分层设计：

- Playwright 验证真实浏览器业务流程
- Requests 快速执行接口校验和测试数据清理
- Page Object 封装页面元素和页面操作
- pytest fixture 管理登录状态、页面对象和测试前置条件
- Allure/JUnit 输出测试结果
- Jenkins 在 Windows Agent 上执行 headless 回归
- JMeter 建立登录与用户列表接口性能基线

## 技术栈

| 类型 | 技术 |
|---|---|
| 编程语言 | Python 3 |
| 测试框架 | pytest |
| UI 自动化 | Playwright、pytest-playwright |
| 接口自动化 | Requests |
| 数据辅助 | MySQL、PyMySQL |
| 测试报告 | Allure、JUnit XML |
| 持续集成 | Jenkins、Jenkinsfile |
| 性能测试 | Apache JMeter |
| 版本管理 | Git |

## 测试覆盖

### UI 自动化

| 场景 | 验证内容 |
|---|---|
| 管理员登录 | 登录成功、页面跳转和首页元素 |
| 新增用户 | 表单填写、提交成功、列表查询 |
| 必填校验 | 空表单提交和字段提示 |
| 重复用户名 | 业务错误提示和失败状态 |
| 用户搜索 | 条件查询和目标行校验 |
| 用户编辑 | 修改昵称/手机号并校验列表结果 |

### API 自动化

| 场景 | 接口能力 |
|---|---|
| 登录成功 | 获取并保存 token |
| 登录失败 | 错误账号密码校验 |
| 用户查询 | 用户列表和用户详情 |
| 用户新增 | 新增用户并查询确认 |
| 用户修改 | 修改用户信息 |
| 用户删除 | 删除用户并确认数据不存在 |
| 异常场景 | 重复用户名、删除不存在用户 |

## 工程结构

```text
Ruoyi_full_auto_test/
├─ common/
│  ├─ config.py          环境配置与超时配置
│  ├─ logger.py          统一日志
│  ├─ test_data.py       动态测试数据工厂
│  └─ user_api.py        RuoYi 用户接口客户端
├─ pages/
│  ├─ login_page.py      登录页面对象
│  └─ user_page.py       用户管理页面对象
├─ test_ui/              Playwright UI 自动化用例
├─ test_api/             Requests API 自动化用例
├─ performance/          JMeter 测试计划
├─ reports/              测试运行产物（已忽略）
├─ conftest.py           全局 fixture、日志和失败截图
├─ pytest.ini             pytest 配置
├─ Jenkinsfile           Jenkins CI 流水线
├─ requirements.txt       Python 依赖
└─ .env.example           环境变量示例
```

## 测试设计

### 测试数据隔离

测试用户名使用 `ui_test_`、`api_test_` 等业务前缀结合 UUID 动态生成，避免依赖固定数据。创建类用例在 `finally` 中调用接口清理测试用户，保证用例可以重复执行。

### UI 与 API 协同

- UI 用例负责验证真实页面交互、弹窗、表格和提示信息。
- API 客户端负责快速查询、详情校验和测试数据清理。
- 关键业务同时校验页面结果和接口/列表数据，降低误判概率。

### 可维护性

页面定位器和页面操作集中在 Page Object 中，测试用例只保留业务步骤和断言；接口请求统一封装鉴权、超时、JSON 解析和业务错误处理。

### 失败定位

测试失败时自动保留：

- pytest 控制台日志
- `reports/logs/pytest.log`
- `reports/screenshots/fail/` 失败截图
- Allure 附件
- `reports/junit.xml` 测试结果

## 环境要求

默认被测服务地址如下：

| 服务 | 默认地址 |
|---|---|
| RuoYi 前端 | `http://localhost:82` |
| RuoYi 后端 API | `http://localhost:8081` |
| Jenkins | `http://localhost:8080` |

Jenkins 端口仅作为 CI 服务示例，RuoYi 后端 API 使用 `8081` 端口。

## 安装依赖

在 `Ruoyi_full_auto_test` 目录执行：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m playwright install chromium
```

## 运行测试

### UI headed 调试

```powershell
pytest test_ui/test_ruoyi_login.py -s --headed --slowmo=600
pytest test_ui/test_ruoyi_user_add.py -s --headed --slowmo=600
pytest test_ui -s --headed --slowmo=600
```

### UI/API headless 回归

不传 `--headed` 即使用 headless 模式：

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

## 环境变量

可参考 `.env.example` 设置环境变量：

```powershell
$env:RUOYI_FRONTEND_BASE_URL = "http://localhost:82"
$env:RUOYI_API_BASE_URL = "http://localhost:8081"
$env:RUOYI_UI_USERNAME = "admin"
$env:RUOYI_UI_PASSWORD = "admin123"
$env:RUOYI_API_USERNAME = "admin"
$env:RUOYI_API_PASSWORD = "admin123"
```

真实账号密码只应通过本地环境变量或 Jenkins Credentials 注入，不要提交到 Git。

## Jenkins 持续集成

项目提供 `Jenkinsfile`，适用于 Windows Jenkins Agent，流水线包含：

1. 检查 RuoYi 前端和后端端口
2. 进入 `Ruoyi_full_auto_test` 子目录
3. 安装 Python 依赖和 Chromium
4. 以 headless 模式执行 UI/API 自动化测试
5. 生成并归档 JUnit、Allure、日志和失败截图

如果仓库根目录就是工作区，Jenkins Pipeline 的 Script Path 使用：

```text
Ruoyi_full_auto_test/Jenkinsfile
```

## JMeter 性能测试

性能测试计划位于：

```text
performance/RuoYi_login_user_list.jmx
```

覆盖接口：

- `POST /login`：登录并提取 token
- `GET /system/user/list`：携带 Bearer Token 查询用户列表

详细执行命令见：

```text
performance/README.md
```

默认线程组为 5 个并发用户、10 秒 ramp-up、每个用户循环 2 次，适合建立基础性能数据。性能结果不提交到 Git。

## 测试结果

在 RuoYi 前后端服务正常运行的环境中，UI/API 全量回归结果：

```text
13 passed
```

对应产物：

```text
reports/junit.xml
reports/allure-results/
reports/logs/pytest.log
```

## License

本项目仅用于自动化测试技术实践与项目展示。