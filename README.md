# test-auto-devops-study 运维测试学习仓库

> 面向秋招与日常练习的运维测试学习资料库，覆盖软件测试基础、接口测试、缺陷管理、HTTP 抓包、Apifox 实操、Python requests 与 pytest 接口自动化。

## 仓库结构

```text
test-auto-devops-study/
├── 01_软件测试基础/             # 测试流程、用例设计、基础测试用例
├── 02_缺陷管理/                 # Bug 生命周期、禅道实训、接口缺陷练习
├── 03_HTTP协议与接口调试/        # HTTP 协议、抓包、接口调试记录
├── 04_Apifox接口测试/            # Apifox 笔记、JSON 项目、自动化测试报告
├── 05_Python接口自动化/          # Python、requests、pytest、自动化代码
├── 第一周复盘.md
├── 第二周复盘.md
├── README.md
└── .gitattributes
```

## 学习路线

建议按这个顺序学习：

1. [软件测试基础](#1-软件测试基础)：先理解测试流程、测试分类、质量模型和用例编写。
2. [缺陷管理](#2-缺陷管理)：掌握 Bug 生命周期、缺陷提交规范和禅道实操。
3. [HTTP 协议与接口调试](#3-http-协议与接口调试)：理解请求响应、状态码、报文结构和抓包排查。
4. [Apifox 接口测试](#4-apifox-接口测试)：练习接口调试、断言、鉴权、接口关联和自动化场景。
5. [Python 接口自动化](#5-python-接口自动化)：使用 `requests` 编写接口脚本，再用 `pytest` 管理自动化用例。
6. [阶段复盘](#阶段复盘)：按周整理完成内容、实操产出、踩坑和后续补强。

## 内容导航

### 阶段复盘

| 文件 | 内容 |
| --- | --- |
| [第一周复盘](./第一周复盘.md) | 8.6-8.12 测试基础、用例设计、接口测试、HTTP 抓包和 Apifox 自动化复盘 |
| [第二周复盘](./第二周复盘.md) | 8.13-8.19 禅道、Python、requests、pytest、fixture、Allure 和 demo 项目复盘 |

### 1. 软件测试基础

| 文件 | 内容 |
| --- | --- |
| [软件测试全流程笔记](./01_软件测试基础/软件测试全流程笔记.md) | 软件测试基础、测试分类、质量模型、测试流程、用例基础、缺陷基础 |
| [用例设计思路总结](./01_软件测试基础/用例设计思路总结.md) | 等价类划分、边界值分析、判定表、场景法、错误推测法、组合策略 |
| [登录注册查询测试用例](./01_软件测试基础/登录注册查询测试用例.md) | 登录、注册、查询模块的测试用例设计 |
| [接口测试用例](./01_软件测试基础/接口测试用例.md) | 用户登录、用户注册接口测试用例集合 |

### 2. 缺陷管理

| 文件 | 内容 |
| --- | --- |
| [bug缺陷管理笔记](./02_缺陷管理/bug缺陷管理笔记.md) | Bug 生命周期、缺陷状态、禅道格式缺陷案例 |
| [禅道缺陷管理实训笔记](./02_缺陷管理/禅道缺陷管理实训笔记.md) | 禅道部署流程、提 Bug 操作、接口 Bug 清单、字段规范 |
| [接口缺陷实战练习](./02_缺陷管理/接口缺陷实战练习.md) | Token 为空、越权访问、空用户名等接口缺陷练习 |

### 3. HTTP 协议与接口调试

| 文件 | 内容 |
| --- | --- |
| [HTTP 协议与抓包实战](./03_HTTP协议与接口调试/HTTP%20协议与抓包实战.md) | HTTP 请求响应流程、状态码、报文结构、Token 鉴权、Fiddler 抓包与排查 |
| [接口调试记录](./03_HTTP协议与接口调试/接口调试记录.md) | GET、POST、form-data、x-www-form-urlencoded、PUT、DELETE 接口调试记录 |

### 4. Apifox 接口测试

| 文件 | 内容 |
| --- | --- |
| [Apifox接口测试操作手册](./04_Apifox接口测试/Apifox接口测试操作手册.md) | Apifox 界面、请求方法、Params、Headers、Body、状态码、响应解析、报错排查 |
| [Apifox接口进阶](./04_Apifox接口测试/Apifox接口进阶.md) | Token、Session-Cookie、JWT、API-Key、接口关联、变量提取 |
| [Apifox断言](./04_Apifox接口测试/Apifox断言.md) | 断言对象、断言条件、JSONPath、断言失败排查 |
| [Apifox测试实操记录](./04_Apifox接口测试/Apifox测试实操记录.md) | 单接口调试、后置操作、Token 鉴权、登录异常场景实操 |

#### Apifox JSON 项目

| 文件 | 内容 |
| --- | --- |
| [7个简易接口调试.json](./04_Apifox接口测试/apifox_json/7个简易接口调试%20.json) | 基础接口调试项目 |
| [Apifox接口自动化完整实训项目.json](./04_Apifox接口测试/apifox_json/Apifox接口自动化完整实训项目.json) | Apifox 自动化完整实训项目 |
| [Apifox接口自动化实战(token自动传递).json](./04_Apifox接口测试/apifox_json/Apifox接口自动化实战%28token自动传递%29.json) | Token 自动传递接口自动化项目 |
| [CSV 文件数据驱动.json](./04_Apifox接口测试/apifox_json/CSV%20文件数据驱动.json) | CSV 数据驱动项目 |

#### Apifox 测试报告

> GitHub 不能直接渲染 HTML 报告页面。查看 `.html` 报告时，建议下载到本地后用浏览器打开。

| 文件 | 内容 |
| --- | --- |
| [01_登录 Token 自动传递自动化测试](./04_Apifox接口测试/apifox_report/01_登录%20Token%20自动传递自动化测试.md) | 登录鉴权 Token 自动传递实操记录 |
| [01_单用例自动化测试报告_全通过.html](./04_Apifox接口测试/apifox_report/01_单用例自动化测试报告_全通过.html) | 单用例自动化测试 HTML 报告 |
| [01_单用例自动化测试报告_全通过.jpeg](./04_Apifox接口测试/apifox_report/01_单用例自动化测试报告_全通过.jpeg) | 单用例报告截图 |
| [02_多数据集数据驱动自动化测试](./04_Apifox接口测试/apifox_report/02_多数据集数据驱动自动化测试.md) | 多数据集数据驱动实操记录 |
| [02_多数据集数据驱动自动化测试报告_含失败用例.html](./04_Apifox接口测试/apifox_report/02_多数据集数据驱动自动化测试报告_含失败用例.html) | 数据驱动 HTML 报告 |
| [02_多数据集数据驱动自动化测试报告_含失败用例.png](./04_Apifox接口测试/apifox_report/02_多数据集数据驱动自动化测试报告_含失败用例.png) | 数据驱动报告截图 |
| [03_用户 CRUD 完整流程自动化实战](./04_Apifox接口测试/apifox_report/03_用户%20CRUD%20完整流程自动化实战.md) | 用户 CRUD 完整流程自动化实战记录 |
| [03_用户管理CRUD完整流程自动化测试报告_全部通过.html](./04_Apifox接口测试/apifox_report/03_用户管理CRUD完整流程自动化测试报告_全部通过.html) | 用户 CRUD HTML 报告 |
| [03_用户管理CRUD完整流程自动化测试报告_全部通过.png](./04_Apifox接口测试/apifox_report/03_用户管理CRUD完整流程自动化测试报告_全部通过.png) | 用户 CRUD 报告截图 |

### 5. Python 接口自动化

| 文件 | 内容 |
| --- | --- |
| [python核心知识点](./05_Python接口自动化/python核心知识点.md) | 注释、运行模式、变量、数据类型、字符串、字典、模块导入、函数、循环、常见报错 |
| [requests学习笔记](./05_Python接口自动化/requests学习笔记.md) | requests 安装、GET/POST 请求模板、响应数据提取、timeout、异常捕获、断言 |
| [Pytest知识笔记](./05_Python接口自动化/Pytest知识笔记.md) | pytest 基础、用例识别规则、常用命令 |
| [Pytest Fixture 学习笔记](./05_Python接口自动化/Pytest‑Fixture%20学习笔记.md) | fixture 前置准备、作用域、Token 复用 |
| [Pytest + Allure 接口自动化](./05_Python接口自动化/Pytest+Allure%20接口自动化.md) | Allure 注解、报告生成、日志脚本和常见问题 |

#### 代码目录

```text
05_Python接口自动化/
├── python_requests_api_learning/
│   ├── 01_basic_requests/        # requests 基础请求练习
│   ├── 02_assert_practice/       # requests + assert 断言练习
│   ├── 03_pytest_api_cases/      # pytest 接口自动化用例与测试报告
│   ├── 04_pytest_fixture_token/  # fixture 和 token 复用练习
│   └── 05_allure_log_demo/       # Allure 报告和日志练习
└── pytest_api_demo/              # 标准 pytest 接口自动化 demo
```

#### requests 基础请求练习

| 文件 | 练习点 |
| --- | --- |
| [01_get_no_params.py](./05_Python接口自动化/python_requests_api_learning/01_basic_requests/01_get_no_params.py) | GET 无参请求 |
| [02_get_with_params.py](./05_Python接口自动化/python_requests_api_learning/01_basic_requests/02_get_with_params.py) | GET 携带 `params` 参数 |
| [03_post_form.py](./05_Python接口自动化/python_requests_api_learning/01_basic_requests/03_post_form.py) | POST 表单提交 |
| [04_post_json_body.py](./05_Python接口自动化/python_requests_api_learning/01_basic_requests/04_post_json_body.py) | POST JSON 请求体提交 |

#### requests 断言练习

| 文件 | 练习点 |
| --- | --- |
| [01_get_no_params_assert.py](./05_Python接口自动化/python_requests_api_learning/02_assert_practice/01_get_no_params_assert.py) | GET 无参请求断言 |
| [02_get_with_params_assert.py](./05_Python接口自动化/python_requests_api_learning/02_assert_practice/02_get_with_params_assert.py) | GET 参数断言 |
| [03_post_form_data_assert.py](./05_Python接口自动化/python_requests_api_learning/02_assert_practice/03_post_form_data_assert.py) | POST 表单断言 |
| [04_post_json_body_assert.py](./05_Python接口自动化/python_requests_api_learning/02_assert_practice/04_post_json_body_assert.py) | POST JSON 断言 |

#### pytest 接口自动化用例

| 文件 | 练习点 |
| --- | --- |
| [test_01_get_no_params.py](./05_Python接口自动化/python_requests_api_learning/03_pytest_api_cases/test_01_get_no_params.py) | GET 无参接口自动化用例 |
| [test_02_get_with_params.py](./05_Python接口自动化/python_requests_api_learning/03_pytest_api_cases/test_02_get_with_params.py) | GET 参数接口自动化用例 |
| [test_03_post_form_data.py](./05_Python接口自动化/python_requests_api_learning/03_pytest_api_cases/test_03_post_form_data.py) | POST 表单接口自动化用例 |
| [test_04_post_json_body.py](./05_Python接口自动化/python_requests_api_learning/03_pytest_api_cases/test_04_post_json_body.py) | POST JSON 接口自动化用例 |
| [test_05_get_no_token.py](./05_Python接口自动化/python_requests_api_learning/03_pytest_api_cases/test_05_get_no_token.py) | 未携带 Token 异常场景 |
| [test_06_post_form_wrong_pwd.py](./05_Python接口自动化/python_requests_api_learning/03_pytest_api_cases/test_06_post_form_wrong_pwd.py) | 表单密码错误异常场景 |
| [test_07_post_json_empty_phone.py](./05_Python接口自动化/python_requests_api_learning/03_pytest_api_cases/test_07_post_json_empty_phone.py) | JSON 手机号为空异常场景 |
| [test_08_get_timeout.py](./05_Python接口自动化/python_requests_api_learning/03_pytest_api_cases/test_08_get_timeout.py) | timeout 超时异常场景 |
| [test_09_post_no_headers.py](./05_Python接口自动化/python_requests_api_learning/03_pytest_api_cases/test_09_post_no_headers.py) | 缺少请求头异常场景 |
| [test_10_get_wrong_param.py](./05_Python接口自动化/python_requests_api_learning/03_pytest_api_cases/test_10_get_wrong_param.py) | 参数错误异常场景 |
| [report.html](./05_Python接口自动化/python_requests_api_learning/03_pytest_api_cases/report.html) | pytest HTML 测试报告 |

#### 标准 pytest 接口自动化 demo

| 文件 | 说明 |
| --- | --- |
| [pytest_api_demo README](./05_Python接口自动化/pytest_api_demo/README.md) | demo 项目说明、运行命令、报告生成方式 |
| [requirements.txt](./05_Python接口自动化/pytest_api_demo/requirements.txt) | 项目依赖 |
| [pytest.ini](./05_Python接口自动化/pytest_api_demo/pytest.ini) | pytest 用例发现和执行配置 |
| [conftest.py](./05_Python接口自动化/pytest_api_demo/conftest.py) | 公共 fixture、base_url、session、token 复用 |
| [test_01_basic_api.py](./05_Python接口自动化/pytest_api_demo/test_cases/test_01_basic_api.py) | GET / POST 基础请求 |
| [test_02_headers_cookie.py](./05_Python接口自动化/pytest_api_demo/test_cases/test_02_headers_cookie.py) | 请求头和 Cookie 断言 |
| [test_03_auth_token.py](./05_Python接口自动化/pytest_api_demo/test_cases/test_03_auth_token.py) | Token fixture 复用 |
| [test_04_negative_cases.py](./05_Python接口自动化/pytest_api_demo/test_cases/test_04_negative_cases.py) | 404、鉴权缺失、超时异常场景 |

## 本地运行 Python 接口自动化

### 安装依赖

```bash
cd 05_Python接口自动化/pytest_api_demo
pip install -r requirements.txt
```

### 运行 requests 脚本

```bash
cd 05_Python接口自动化/python_requests_api_learning/01_basic_requests
python 01_get_no_params.py
```

### 运行 pytest 用例

```bash
cd 05_Python接口自动化/python_requests_api_learning/03_pytest_api_cases
pytest -q
```

生成 HTML 测试报告：

```bash
pytest -q --html=report.html --self-contained-html
```

### 运行标准 pytest demo

```bash
cd 05_Python接口自动化/pytest_api_demo
pytest
```

生成 pytest-html 报告：

```bash
pytest --html=reports/report.html --self-contained-html
```

生成 Allure 原始结果：

```bash
pytest --alluredir=allure-results
```

## 当前学习覆盖能力

- 软件测试基础理论与完整测试流程
- 测试用例设计方法与模块用例编写
- 缺陷生命周期、Bug 提交规范与禅道实操
- HTTP 请求响应、状态码、报文结构和抓包排查
- Apifox 单接口调试、断言、鉴权、接口关联和自动化测试
- Python 基础语法、requests 请求封装、异常捕获和响应解析
- pytest 自动化用例编写、异常场景覆盖和 HTML 报告生成
- fixture 管理公共前置条件，复用 Token
- Allure 注解、日志输出和可视化报告生成
- 标准 pytest demo 项目结构、依赖管理和执行配置

## GitHub 查看说明

- Markdown 文件可直接在 GitHub 页面阅读。
- 图片报告可直接预览，例如 `.png`、`.jpeg` 文件。
- HTML 报告建议下载到本地后用浏览器打开。
- Apifox JSON 文件可导入 Apifox 查看完整接口项目。
