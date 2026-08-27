# test-auto-devops-study

这是一个面向秋招测试工程师 / 测试开发工程师岗位的学习与项目展示仓库，内容包含软件测试基础、接口测试、接口自动化、Linux/MySQL、Jenkins CI、Docker 基础和 AI 辅助测试开发实践。

## 仓库重点

| 类型 | 目录 | 说明 |
| --- | --- | --- |
| 简历项目一 | [RuoYi_api_test](./RuoYi_api_test/) | 基于 RuoYi 后台管理系统的接口自动化测试项目，覆盖登录鉴权、用户、角色、菜单、部门、权限校验等模块 |
| 简历项目二 | [data_driven_test_tool](./data_driven_test_tool/) | YAML 数据驱动接口测试工具，体现用例与代码解耦、报告生成和 AI 辅助测试开发实践 |
| 历史练习项目 | [api_auto_ci_demo](./api_auto_ci_demo/) | Pytest + Allure + Jenkins 接口自动化基础练习项目 |
| RuoYi 学习记录 | [11_ruoyi](./11_ruoyi/) | RuoYi 环境部署、接口自动化踩坑和复盘笔记 |
| 自动化学习 | [05_Python接口自动化](./05_Python接口自动化/) | Python、Requests、Pytest、Fixture、Allure 学习与实操 |
| 环境与运维 | [06_Linux运维实战](./06_Linux运维实战/) | Linux 命令、日志排查、Shell、MySQL、JMeter、Tomcat 等基础实操 |

## 简历项目

### 1. RuoYi 后台管理系统接口自动化测试项目

- 技术栈：Python、Requests、Pytest、Allure、Jenkins、Git、MySQL
- 被测系统：开源 RuoYi 后台管理系统
- 覆盖范围：登录鉴权、用户管理、角色管理、菜单管理、部门管理、权限校验、角色业务链路
- 项目成果：6 个业务模块、20 条自动化用例、约 13 个接口调用，支持接口断言、测试数据清理、Allure 报告和 Jenkins 本地 CI 回归

入口文档：[RuoYi_api_test/README.md](./RuoYi_api_test/README.md)

### 2. YAML 数据驱动接口测试工具

- 技术栈：Python、Requests、PyYAML、Jinja2
- 项目定位：轻量级本地接口测试工具，通过 YAML 管理接口用例，降低新增用例对 Python 源码的依赖
- 核心模块：YAML 解析、请求发送、断言校验、结果统计、HTML 报告渲染
- 项目特点：适合展示 AI 辅助测试开发、代码阅读理解、问题排查和工具化思维

入口文档：[data_driven_test_tool/README.md](./data_driven_test_tool/README.md)

## 学习笔记导航

| 目录 | 内容 |
| --- | --- |
| [01_软件测试基础](./01_软件测试基础/) | 测试流程、测试用例设计、接口测试用例 |
| [02_缺陷管理](./02_缺陷管理/) | 缺陷生命周期、禅道实训、接口缺陷记录 |
| [03_HTTP协议与接口调试](./03_HTTP协议与接口调试/) | HTTP 协议、请求响应、抓包与接口调试 |
| [04_Apifox接口测试](./04_Apifox接口测试/) | Apifox 接口管理、断言、数据驱动、自动化测试 |
| [05_Python接口自动化](./05_Python接口自动化/) | Requests、Pytest、Fixture、Allure、接口自动化项目 |
| [06_Linux运维实战](./06_Linux运维实战/) | Linux、Shell、MySQL、JMeter、Tomcat、故障排查 |
| [07_Jenkins_CI接口自动化流水线](./07_Jenkins_CI接口自动化流水线/) | Jenkins、Pytest、Allure 持续集成流程 |
| [08_cursor学习实操](./08_cursor学习实操/) | Cursor / AI 辅助编码学习记录 |
| [09_playwright学习了解](./09_playwright学习了解/) | Playwright Web 自动化基础了解 |
| [10_Docker](./10_Docker/) | Docker 镜像、容器、端口映射、MySQL 容器部署练习 |
| [11_ruoyi](./11_ruoyi/) | RuoYi 后端部署与接口自动化问题复盘 |

## 仓库结构

```text
test-auto-devops-study/
├── 01_软件测试基础/
├── 02_缺陷管理/
├── 03_HTTP协议与接口调试/
├── 04_Apifox接口测试/
├── 05_Python接口自动化/
├── 06_Linux运维实战/
├── 07_Jenkins_CI接口自动化流水线/
├── 08_cursor学习实操/
├── 09_playwright学习了解/
├── 10_Docker/
├── 11_ruoyi/
├── RuoYi_api_test/               # 简历项目一
├── data_driven_test_tool/        # 简历项目二
├── api_auto_ci_demo/             # 历史练习项目
└── README.md
```

## 仓库说明

- `RuoYi_api_test` 是当前秋招主推项目，优先用于简历和面试讲解。
- `data_driven_test_tool` 是第二项目，重点体现数据驱动和 AI 辅助测试开发能力。
- `api_auto_ci_demo` 保留为接口自动化和 CI 的基础练习项目，不再作为主推项目。
- `venv`、`__pycache__`、`.pytest_cache`、`allure-results`、`allure-report`、`reports` 等运行产物不建议提交到 GitHub。
