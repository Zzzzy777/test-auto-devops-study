# api_auto_ci_demo 接口自动化持续集成项目

这是一个面向秋招展示的轻量级接口自动化项目，重点验证 `requests`、`pytest`、`Allure`、`Jenkins` 和 `Docker` 的基础闭环，而不是复杂业务本身。

## 项目定位

- 技术验证型项目
- 使用公共测试接口完成接口自动化练习
- 重点展示用例设计、Fixture 复用、报告生成和 CI 流水线

## 当前覆盖

- 4 个正式测试模块
- 10 条自动化用例
- 7 类正反场景
- 6 个核心接口

覆盖场景包括：

- GET 参数请求
- POST 表单提交
- POST JSON 请求体
- 自定义请求头
- Cookie 校验
- Token 鉴权
- 404 异常场景
- 超时异常场景

## 技术栈

- Python
- Requests
- Pytest
- Allure
- Jenkins
- Git
- Docker
- Linux

## 项目结构

```text
api_auto_ci_demo/
├── common/                    # 公共日志等工具
├── docs/                      # 测试报告说明与截图
├── test_cases/                # pytest 接口自动化用例
├── conftest.py                # base_url / session / token fixture
├── pytest.ini                 # pytest 执行配置
├── Jenkinsfile                # Jenkins CI 流水线
├── requirements.txt           # 项目依赖
└── README.md                  # 项目说明
```

## 面试时重点讲这几件事

### 1. `conftest.py`

- 统一管理 `base_url`
- 复用 `requests.Session()`
- 用 `session` 级 fixture 获取并复用 token

### 2. `pytest.ini`

- 统一用例发现规则
- 配置 marker
- 规范日志和输出格式

### 3. `test_cases/`

- 正向场景：GET、POST、请求头、Cookie、Token
- 反向场景：404、鉴权缺失、超时

### 4. `Allure`

- 生成可视化测试报告
- 分类展示模块和用例
- 方便快速定位失败步骤

### 5. `Jenkins`

- 拉取代码
- 安装依赖
- 执行测试
- 归档 Allure 结果

## 本地运行

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 执行用例

```bash
pytest test_cases/
```

### 3. 生成 pytest-html 报告

```bash
pytest test_cases/ --html=reports/report.html --self-contained-html
```

### 4. 生成 Allure 原始结果

```bash
pytest test_cases/ --alluredir=allure-results
```

### 5. 预览 Allure 报告

```bash
allure serve allure-results
```

## 报告说明

- [测试报告与截图说明](./docs/测试报告与截图说明.md)
- [pytest-html 报告](./docs/html_reports/pytest_api_demo_report.html)
- `docs/images/` 下保存了 pytest 执行结果和 Allure 截图

## 默认环境

- 默认请求地址：`https://httpbin.ceshiren.com`
- 可通过 `--base-url` 参数覆盖

示例：

```bash
pytest test_cases/ --base-url=https://httpbin.ceshiren.com
```

## 简历表达建议

> 我做了一个基于 Pytest + Requests + Allure + Jenkins 的接口自动化持续集成项目，覆盖 GET、POST、请求头、Cookie、Token 鉴权和异常场景。项目里通过 `conftest.py` 统一管理 `base_url`、`Session` 和 `Token` 复用，并能输出 pytest-html 和 Allure 报告，形成从脚本执行到报告展示的完整闭环。
