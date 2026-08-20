# pytest_api_demo 接口自动化项目

> 这是一个面向运维测试学习阶段的轻量级 pytest 接口自动化 demo，重点练习 `requests`、断言、fixture、Token 复用、请求头 / Cookie 校验、异常场景和测试报告生成。

## 项目定位

这个项目适合在面试里作为“完整闭环”来讲：

1. 先用 `requests` 完成接口调试。
2. 再把脚本改造成 `pytest` 用例。
3. 通过 `conftest.py` 复用 `session` 和 `token`。
4. 最后输出 `pytest-html` 和 `Allure` 报告。

## 覆盖内容

- GET 无参 / 带参数请求
- POST 表单 / JSON 请求体
- 状态码断言
- 返回字段断言
- 请求头断言
- Cookie 断言
- `pytest.fixture` 前置准备
- 全局 Token 复用
- 异常状态码校验
- 简单日志输出
- HTML / Allure 报告生成

## 项目结构

```text
pytest_api_demo/
├── conftest.py              # pytest 公共配置和 fixture
├── pytest.ini               # pytest 执行配置
├── requirements.txt         # 项目依赖
├── README.md                # 项目说明
├── common/
│   └── logger.py            # 简单日志工具
├── docs/
│   ├── images/              # 测试执行截图和 Allure 截图
│   ├── html_reports/        # 归档的 pytest-html 报告
│   └── 测试报告与截图说明.md
└── test_cases/
    ├── test_01_basic_api.py       # GET / POST 基础请求
    ├── test_02_headers_cookie.py  # 请求头和 Cookie 断言
    ├── test_03_auth_token.py      # fixture 获取 token 并复用
    └── test_04_negative_cases.py  # 异常场景与错误响应
```

## 面试时重点讲

- `conftest.py` 里用 `session` 级别 fixture 管理 `requests.Session()` 和 `api_token`，减少重复登录和重复建连。
- `pytest.ini` 里统一了用例发现规则、日志输出和 marker。
- `test_cases` 里既有正向请求，也有异常场景，能说明你不是只会跑通 happy path。
- 用例上加了 `allure.feature`、`allure.story` 和 `allure.title`，报告可读性更好。

## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行全部用例

```bash
pytest
```

## 生成 pytest-html 报告

```bash
pytest --html=reports/report.html --self-contained-html
```

本项目已归档一份 pytest-html 报告，可下载后用浏览器打开：

[pytest_api_demo_report.html](./docs/html_reports/pytest_api_demo_report.html)

## 生成 Allure 报告

先生成 Allure 原始结果：

```bash
pytest --alluredir=allure-results
```

再生成 HTML 报告：

```bash
allure generate allure-results -o allure-report --clean
```

打开报告：

```bash
allure open allure-report
```

## 测试报告截图

### pytest 终端执行结果

![pytest 终端执行结果](./docs/images/01_pytest_terminal_10_passed.png)

### pytest-html 报告摘要

![pytest-html 报告摘要](./docs/images/02_pytest_html_report_summary.png)

### Allure 报告总览

![Allure 报告总览](./docs/images/03_allure_report_overview.png)

### Allure Suites 分类

![Allure Suites 分类](./docs/images/04_allure_suites_summary.png)

### Token 鉴权用例详情

![Token 鉴权用例详情](./docs/images/05_allure_token_case_detail.png)

更多说明见：[测试报告与截图说明](./docs/测试报告与截图说明.md)。

## 测试环境

默认请求地址：

```text
https://httpbin.ceshiren.com
```

也可以通过环境变量或命令行参数覆盖：

```bash
set API_BASE_URL=https://httpbin.ceshiren.com
pytest
```

或者：

```bash
pytest --base-url=https://httpbin.ceshiren.com
```

## 可直接复述的面试话术

> 我做了一个 pytest + requests 的接口自动化 demo，覆盖 GET/POST、请求参数、请求头、Cookie、Token fixture 复用、异常场景断言，并能生成 pytest-html 和 Allure 报告。项目里用 `conftest.py` 管理公共 fixture，用 `pytest.ini` 统一执行规则，依赖写在 `requirements.txt` 中，方便别人复现。
