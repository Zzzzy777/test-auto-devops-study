# test-auto-devops-study

面向测试工程师 / 测试开发工程师学习与项目展示的综合仓库，记录从软件测试基础、接口测试到接口/UI 自动化、性能测试、CI/CD、Docker 和 AI 辅助测试开发的学习过程与可运行项目。

## 仓库定位

- **学习笔记**：沉淀测试理论、HTTP、Apifox、Python、Linux、Docker、Playwright 等知识。
- **项目实践**：提供可运行的接口自动化、UI 自动化、性能测试和数据驱动工具。
- **工程化练习**：覆盖测试数据管理、报告生成、失败定位、Jenkins 持续集成和质量门禁。

## 推荐入口

| 项目 | 入口 | 适合了解的内容 |
| --- | --- | --- |
| RuoYi 一体化自动化测试 | [Ruoyi-api-ui-auto-test](./Ruoyi-api-ui-auto-test/) | API、Playwright UI、JMeter、Allure、Jenkins、测试数据清理 |
| YAML 数据驱动接口测试工具 | [data_driven_test_tool](./data_driven_test_tool/) | YAML 用例、请求执行、断言、统计和 HTML 质量看板 |
| RuoYi 接口自动化项目 | [mini_projects/RuoYi_api_test](./mini_projects/RuoYi_api_test/) | 登录鉴权、用户/角色/菜单/部门、权限和业务链路 |
| RuoYi 全量自动化练习 | [mini_projects/Ruoyi_full_auto_test](./mini_projects/Ruoyi_full_auto_test/) | UI、API、JMeter 与 Jenkins 的综合练习 |
| 接口自动化 CI 基础练习 | [mini_projects/api_auto_ci_demo](./mini_projects/api_auto_ci_demo/) | Pytest、Allure 和 Jenkins 基础流水线 |

如果只想快速查看一个完整项目，建议从 [Ruoyi-api-ui-auto-test/README.md](./Ruoyi-api-ui-auto-test/README.md) 开始；如果想先理解测试设计和接口自动化基础，再按下面的学习路线阅读。

## 学习路线

| 阶段 | 目录 | 主要内容 |
| --- | --- | --- |
| 01 | [软件测试基础](./01_软件测试基础/) | 测试流程、测试分类、质量模型、用例设计和接口测试用例 |
| 02 | [缺陷管理](./02_缺陷管理/) | Bug 生命周期、禅道实训、缺陷案例和接口缺陷分析 |
| 03 | [HTTP 协议与接口调试](./03_HTTP协议与接口调试/) | 请求/响应、状态码、抓包、鉴权和接口调试 |
| 04 | [Apifox 接口测试](./04_Apifox接口测试/) | 接口管理、断言、变量、数据驱动和自动化测试报告 |
| 05 | [Python 接口自动化](./05_Python接口自动化/) | Python、Requests、Pytest、Fixture、Token 和 Allure |
| 06 | [Linux 运维实战](./06_Linux运维实战/) | Linux、Shell、日志、服务管理、MySQL、Tomcat 和 JMeter |
| 07 | [Jenkins CI 接口自动化流水线](./07_Jenkins_CI接口自动化流水线/) | Jenkins、Pytest、Allure 和 Windows Agent 流水线 |
| 08 | [Cursor 学习实操](./08_cursor学习实操/) | AI 辅助编码、代码理解和测试开发实践 |
| 09 | [Playwright 基础](./09_playwright基础/) | Playwright 基础模型、定位器和 UI 自动化入门 |
| 10 | [Docker](./10_Docker/) | 镜像、容器、端口映射和 MySQL 容器部署 |
| 11 | [RuoYi 学习记录](./11_ruoyi/) | RuoYi 部署、接口自动化和问题复盘 |
| 12 | [Playwright UI 自动化实战](./12_Playwright_UI%20%E8%87%AA%E5%8A%A8%E5%8C%96%E5%AE%9E%E6%88%98/) | Page Object、Fixture、API 协同、报告、调试和 Jenkins |

## 根目录结构

```text
test-auto-devops-study/
├── 01_软件测试基础/                 # 测试理论与用例设计
├── 02_缺陷管理/                     # 缺陷管理与问题分析
├── 03_HTTP协议与接口调试/            # HTTP、抓包与接口调试
├── 04_Apifox接口测试/               # Apifox 接口测试实践
├── 05_Python接口自动化/              # Requests、Pytest 与 Allure
├── 06_Linux运维实战/                 # Linux、MySQL、Shell、JMeter
├── 07_Jenkins_CI接口自动化流水线/    # Jenkins 持续集成学习记录
├── 08_cursor学习实操/                # Cursor / AI 辅助测试开发
├── 09_playwright基础/                # Playwright 入门
├── 10_Docker/                        # Docker 基础实操
├── 11_ruoyi/                         # RuoYi 环境与问题复盘
├── 12_Playwright_UI 自动化实战/      # Playwright UI 自动化进阶
├── Ruoyi-api-ui-auto-test/           # 主推的一体化自动化测试项目
├── data_driven_test_tool/            # YAML 数据驱动接口测试工具
├── mini_projects/                    # 独立的小型练习项目
├── .gitignore                        # Git 忽略规则
└── README.md                         # 仓库总览
```

## 主项目能力概览

### Ruoyi-api-ui-auto-test

这是当前仓库的主推项目，围绕 RuoYi 后台管理系统构建一套可重复执行的质量保障工程：

- **接口自动化**：Requests + Pytest，覆盖登录、用户、角色、菜单、部门、权限和业务链路。
- **UI 自动化**：Playwright，覆盖登录、用户新增、查询、编辑、删除、重复数据和必填校验。
- **性能测试**：JMeter，提供登录和用户列表接口的性能测试计划与质量门禁脚本。
- **测试工程化**：Page Object、Fixture、动态测试数据、失败截图、日志、JUnit 和 Allure 报告。
- **持续集成**：Jenkins Windows Agent 流水线，可按参数执行 API、UI 和性能测试。

详细安装、环境变量和运行命令见 [项目 README](./Ruoyi-api-ui-auto-test/README.md)。

### data_driven_test_tool

这是一个轻量级本地接口测试工具：从 YAML 加载用例，发送 HTTP 请求，执行响应断言，统计成功/失败结果，并用 Jinja2 生成 HTML 质量看板。详细说明见 [项目 README](./data_driven_test_tool/README.md)。

## 基础环境

不同项目的依赖相互独立，请进入对应项目目录后再安装依赖。常见环境如下：

- Python 3.10+
- Pytest、Requests、Allure Pytest
- Playwright 和 Chromium
- Apache JMeter
- Jenkins（Windows Agent 场景）
- Docker Desktop（Docker 练习场景）

RuoYi 自动化项目默认使用以下本地服务地址，实际运行前请以对应项目 README 为准：

| 服务 | 默认地址 |
| --- | --- |
| RuoYi 前端 | `http://localhost:82` |
| RuoYi 后端 API | `http://localhost:8081` |
| Jenkins | `http://localhost:8080` |

不要把真实账号、密码、生产环境地址或个人凭据提交到公开仓库。优先使用 `.env.example`、环境变量和 Jenkins Credentials 管理敏感配置。

## GitHub 上传前检查

```powershell
# 查看当前分支和待提交文件
git status

# 确认运行环境没有被提交
git check-ignore -v venv .venv reports allure-results allure-report

# 提交前检查是否误包含密码、Token 或本地路径
git diff --cached
```

仓库已通过 `.gitignore` 忽略 `venv`、`.venv`、`__pycache__`、`.pytest_cache`、测试报告运行产物、日志和本地编辑器目录。HTML 报告、截图和示例数据是否提交，应以对应项目 README 的说明为准。

## 说明

这是一个持续更新的学习与实践仓库。README 中的用例数量、通过率和性能数据不作为固定承诺；运行结果应以本地环境和实际测试报告为准。
