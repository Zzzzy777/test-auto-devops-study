# RuoYi 后台管理系统接口自动化测试项目

本项目是基于开源 RuoYi 后台管理系统搭建的接口自动化测试项目，用于练习企业后台系统的登录鉴权、系统管理接口测试、业务链路回归和 CI 报告生成。

## 项目定位

- 简历项目一：基于 RuoYi 后台管理系统的接口自动化测试与持续集成项目
- 被测系统：RuoYi 后台管理系统后端接口
- 测试重点：登录鉴权、用户管理、角色管理、菜单管理、部门管理、权限校验
- 技术栈：Python、Requests、Pytest、Allure、Jenkins、Git、MySQL

## 项目亮点

- 使用 Requests + Pytest 编写接口自动化用例，覆盖正向、反向和业务链路场景。
- 封装公共请求方法 `send_request`，统一处理 Token、请求头、超时、网络异常和 401 自动重登。
- 使用 Pytest Fixture 和 `finally` 机制清理测试数据，避免测试用户、测试角色残留。
- 使用 Allure 标记 feature/story，生成按模块展示的可视化测试报告。
- 编写 Jenkinsfile，实现代码拉取、依赖安装、用例执行、Allure 报告生成的本地 CI 流程。

## 目录结构

```text
RuoYi_api_test/
├── common_request.py              # 公共请求封装：Token 获取、鉴权头、异常处理、401 重登
├── config.py                      # 被测系统地址和测试账号配置
├── conftest.py                    # Pytest 前后置夹具，清理测试用户数据
├── Jenkinsfile                    # Jenkins CI 流水线脚本
├── requirements.txt               # Python 依赖
└── test_cases/
    ├── test_login.py              # 登录鉴权用例
    ├── test_user.py               # 用户管理用例
    ├── test_role.py               # 角色管理用例
    ├── test_menu.py               # 菜单管理用例
    ├── test_dept.py               # 部门管理用例
    ├── test_permission.py         # 权限校验用例
    └── test_business_link.py      # 角色新增-查询-删除业务链路用例
```

## 当前覆盖范围

| 模块 | 覆盖内容 |
| --- | --- |
| 登录鉴权 | 登录成功、密码错误、账号为空、密码为空 |
| 权限校验 | 无 Token 访问受保护接口，校验鉴权拦截 |
| 用户管理 | 用户列表、用户详情、新增、编辑、删除、重复用户名、必填字段缺失、无效 ID |
| 角色管理 | 角色列表、新增角色、查询角色详情、删除角色、角色菜单异常场景 |
| 菜单管理 | 菜单树形列表查询 |
| 部门管理 | 部门树形列表查询 |
| 业务链路 | 角色新增 -> 查询列表 -> 查询详情 -> 自动删除 |

当前项目口径：6 个业务模块、20 条 Pytest 自动化用例、约 13 个接口调用。

## 快速运行

前置条件：本地 RuoYi 后端服务已启动，并确认 `config.py` 中地址、账号、密码正确。

```bash
pip install -r requirements.txt
pytest test_cases/ -v --alluredir=allure-results
```

生成并查看 Allure 报告：

```bash
allure serve allure-results
```

## 配置说明

`config.py` 中维护被测系统地址和登录账号：

```python
BASE_URL = "http://localhost:8081"
USERNAME = "admin"
PASSWORD = "admin123"
```

如果 RuoYi 后端端口或账号密码有变化，只需要修改这里即可。

## 面试说明口径

这个项目不是只测公开 demo 接口，而是接入了 RuoYi 后台管理系统，围绕真实后台常见的登录鉴权、用户管理、角色管理、权限校验等接口做自动化回归。项目重点不是改造 RuoYi 源码，而是从测试角度完成接口梳理、用例设计、请求封装、断言校验、测试数据清理、报告生成和 Jenkins 回归流程。
