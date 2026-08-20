# Python 接口自动化

> 本目录用于归档 Python 接口自动化学习资料。为了避免内容重复，当前按“学习笔记、阶段练习、完整项目”三类整理。

## 推荐阅读顺序

1. 先看 [01_学习笔记](./01_学习笔记/)：理解 Python、requests、pytest、fixture、Allure 的基础概念。
2. 再看 [02_阶段练习](./02_阶段练习/)：查看早期 GET/POST、断言、pytest 改造过程。
3. 最后看 [03_完整项目](./03_完整项目/)：重点看可写进简历的 `pytest_api_demo`。

## 目录结构

```text
05_Python接口自动化/
├── 01_学习笔记/
│   ├── python核心知识点.md
│   ├── requests学习笔记.md
│   ├── Pytest知识笔记.md
│   ├── Pytest‑Fixture 学习笔记.md
│   └── Pytest+Allure 接口自动化.md
├── 02_阶段练习/
│   └── python_requests_api_learning/
└── 03_完整项目/
    └── pytest_api_demo/
```

## 内容说明

| 分类 | 作用 | 是否重点 |
| --- | --- | --- |
| `01_学习笔记` | 放基础知识笔记，适合复习概念和面试口述 | 需要看懂 |
| `02_阶段练习` | 放学习过程中的小脚本，记录从 requests 到 pytest 的过渡 | 用来回顾 |
| `03_完整项目` | 放完整可运行 demo，适合 GitHub 展示和简历项目 | 重点掌握 |

## 简历项目入口

重点看这个项目：

[pytest_api_demo 接口自动化项目](./03_完整项目/pytest_api_demo/README.md)

该项目覆盖：

- GET / POST 接口请求
- 请求参数、请求头、Cookie 校验
- Token fixture 复用
- 异常场景断言
- pytest-html 报告
- Allure 报告截图

报告说明：

[测试报告与截图说明](./03_完整项目/pytest_api_demo/docs/测试报告与截图说明.md)\




## 🚨 项目踩坑与复盘记录
> 记录实操过程中遇到的真实问题、排查思路与解决方案

1. **Allure 命令无法识别**
- 现象：已pip安装allure‑pytest，可生成allure结果数据，但cmd执行allure提示不是内部命令。
- 根因：`allure‑pytest`仅为pytest插件，Allure命令行工具需要独立安装，需要配置系统环境变量。
- 解决：配置环境变量，也可以直接调用allure.bat完整路径执行，绕过环境变量。
- 经验：修改环境变量后需要重启终端才能生效。

2. **Ubuntu配置静态IP，重启后IP被重置**
- 现象：netplan apply后静态IP生效，虚拟机重启IP变回自动获取，Xshell断开。
- 根因：`cloud‑init`云初始化服务会覆盖netplan网络配置。
- 解决：关闭cloud‑init服务，重新应用netplan配置，重启验证IP持久生效。

3. **MySQL 1045登录拒绝访问**
- 现象：root账号密码遗忘，无法登录MySQL。
- 解决：修改配置开启免密登录，登录后重置root密码；**操作完成必须关闭免密配置，规避安全漏洞**。

4. **Shell脚本语法报错**
- 现象：Windows复制粘贴Shell脚本到Linux，执行报语法异常。
- 根因：Windows特殊符号、换行符、emoji乱码。
- 解决：直接在Xshell的nano编辑器编写shell脚本，避免跨操作系统复制带来的异常。

5. **Pytest Fixture重复获取Token**
- 现象：每条接口用例都重复调用登录接口获取token。
- 解决：修改fixture `scope="session"`，整个测试会话仅执行一次登录，全部用例复用token，减少接口重复请求。

6. **Jenkins拉取GitHub仓库网络超时**
- 现象：虚拟机环境访问GitHub网络不稳定，git clone连接重置。
- 处理：区分脚本问题与网络问题，本地调试阶段可以手动上传代码包进行测试。

7. **Jenkins JDK版本不兼容，服务启动失败**
- 现象：Jenkins安装完成后服务无法正常启动，Web页面访问失败。
- 根因：高版本Jenkins不再支持JDK8，系统预装JDK版本过低，依赖版本不匹配。
- 解决：卸载旧版JDK8，安装JDK17，配置`JAVA_HOME`系统环境变量，重启Jenkins服务后恢复正常。
- 经验：部署服务前，优先查阅官方文档确认依赖版本，避免版本兼容问题。

8. **Apifox调试时公共测试接口突然无法访问**
- 现象：之前调试正常的接口，未修改请求参数，再次调用直接访问超时失败。
- 根因：使用互联网免费公开测试接口，第三方服务不稳定，存在限流、关停服务的情况，并非请求代码错误。
- 解决：更换稳定可用的测试接口，同步更新自动化脚本内所有URL地址，重新执行全部用例验证。
- 经验：自动化项目尽量规避依赖随时会失效的外部公共接口，提前准备备选接口。