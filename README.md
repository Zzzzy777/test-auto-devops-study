# test-auto-devops-study

这是我的运维测试与接口自动化学习仓库，主要面向秋招复习和项目展示。仓库里分成两类内容：

- 学习笔记：测试基础、HTTP、Apifox、Python、Linux、Jenkins、Docker
- 项目实战：接口自动化持续集成框架、YAML 数据驱动工具

# 仓库重点
| 目录 | 作用 |
| --- | --- |
| [api_auto_ci_demo](./api_auto_ci_demo/) | 重点展示项目，Pytest + Allure + Jenkins 接口自动化持续集成框架 |
| [data_driven_test_tool](./data_driven_test_tool/) | 次重点项目，YAML 数据驱动接口自动化工具 |
| [05_Python接口自动化](./05_Python接口自动化/) | Python、requests、pytest、fixture、Allure 学习与实操 |
| [06_Linux运维实战](./06_Linux运维实战/) | Linux 命令、日志排查、Shell、MySQL、JMeter、Tomcat |
| [07_Jenkins_CI接口自动化流水线](./07_Jenkins_CI接口自动化流水线/) | Jenkins 流水线与 CI 实操笔记 |

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
├── api_auto_ci_demo/
├── data_driven_test_tool/
└── README.md
```

## 重点项目

### 1. `api_auto_ci_demo`

这是我秋招主推的接口自动化项目，项目口径统一为：

- 4 个正式测试模块
- 10 条自动化用例
- 7 类正反场景
- 6 个核心接口

项目覆盖 GET、POST、请求头、Cookie、Token 鉴权、404、超时等常见接口测试场景，并串通了 `pytest`、`Allure`、`Jenkins`、`Docker` 的基础流程。

入口文档：

- [项目说明](./api_auto_ci_demo/README.md)
- [测试报告与截图说明](./api_auto_ci_demo/docs/测试报告与截图说明.md)

### 2. `data_driven_test_tool`

这是补充项目，重点体现 YAML 数据驱动、接口封装和结果渲染能力，适合作为秋招中的第二项目。

入口文档：

- [项目说明](./data_driven_test_tool/README.md)

## 学习资料导航

### 基础能力

- [01_软件测试基础](./01_软件测试基础/)
- [02_缺陷管理](./02_缺陷管理/)
- [03_HTTP协议与接口调试](./03_HTTP协议与接口调试/)
- [04_Apifox接口测试](./04_Apifox接口测试/)

### 编程与自动化

- [05_Python接口自动化](./05_Python接口自动化/)
- [07_Jenkins_CI接口自动化流水线](./07_Jenkins_CI接口自动化流水线/)

### 运维与环境

- [06_Linux运维实战](./06_Linux运维实战/)
- [10_Docker](./10_Docker/)

### 其他练习

- [08_cursor学习实操](./08_cursor学习实操/)
- [09_playwright学习了解](./09_playwright学习了解/)

## 仓库约定

- `allure-results`、`allure-report`、`reports`、`logs`、`.pytest_cache`、`__pycache__` 这类内容属于临时产物
- 面试展示优先看项目 README、报告截图和总结文档
- 跟秋招无关的临时文件尽量不要堆在仓库首页
