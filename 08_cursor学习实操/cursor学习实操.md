# Cursor编辑器学习 + 数据驱动接口测试工具（项目二）完整笔记
## 一、Cursor安装与基础使用
### 1. Cursor安装
1. 官网下载Cursor安装包，完成Windows客户端安装
2. 本质基于VSCode二次开发的AI代码编辑器，兼容vscode全部插件
3. 基础设置：
- Python环境选择：切换本机已配置好的python解释器
- 插件：安装Python、Pylint、Pytest插件，和VSCode用法一致

### 2. Cursor常用操作
1. AI对话窗口：`Ctrl + L`唤起AI聊天框
2. 选中代码，直接让AI：解释代码、排查报错、重构代码、生成测试用例
3. 快捷键：`Ctrl + K` 对选中代码生成注释
4. 注意事项
- AI生成代码不能直接复制就跑，**必须逐行阅读理解+上机调试跑通**
- 项目依赖、文件路径、yaml语法、jinja2模板容易出现AI幻觉，需要人工校验
- 重要代码片段，自己动手改一遍，加深理解，面试能讲清楚原理

## 二、基于Cursor完成项目二：YAML数据驱动接口测试工具
>项目路径：`data_driven_test_tool`
>技术栈：Python + requests + PyYAML + Jinja2
>练习接口：jsonplaceholder公开REST接口

### 2.1 项目整体功能
1. 读取yaml格式接口测试用例文件
2. 发送http请求，支持get/post等请求
3. 实现状态码断言、响应json字段断言
4. 捕获接口执行异常
5. 通过Jinja2模板渲染，输出HTML可视化测试看板报告

### 2.2 关键文件说明
1. `cases/httpbin_cases.yaml`：存放所有接口测试用例，数据驱动用例文件
2. `src/main.py`：程序入口，读取用例、执行请求、执行断言
3. `src/yaml_parser.py`：yaml文件解析模块
4. `templates/dashboard.html.j2`：Jinja2 HTML报告模板
5. `output/`：脚本运行后，生成的html报告输出目录

### 2.3 Jinja2模板理解
- 文件：`templates/dashboard.html.j2`
- 作用：是html模板文件，占位符接收脚本传入的测试执行结果数据
- 脚本执行完成后，把执行结果传入模板，渲染生成最终可视化html报告
>面试关键点：模板只是外壳，所有测试数据由python脚本传入渲染。

### 2.4 运行流程
1. 读取yaml用例
2. 循环逐条解析每一条测试用例
3. requests发送http请求
4. 执行断言逻辑，记录成功/失败结果、错误信息
5. 收集全部用例执行数据，传给jinja2模板
6. 渲染输出html报告

## 三、遇到的问题与解决过程
### 1.全部用例返回 503，执行全部失败
- **现象**：运行脚本，所有用例状态码 503，通过率 0%
- **原因**：原始 yaml 用例使用[httpbin.org](https://httpbin.org)公共服务，外部公共服务不稳定，服务不可用，**不是我工具代码 bug**
- **排查**：查看报告里面响应内容，确认是服务端返回 503，不是请求、解析逻辑出错。
- **解决**：更换稳定公开测试接口 jsonplaceholder。

### 2.更换 base_url 之后接口报 404 Not Found
- **现象**：改完 yaml 的 base_url 之后，全部接口 404
- **原因**：旧 yaml 用例保留 httpbin 的路径`/get` `/post` `/status/xxx`，jsonplaceholder 没有这些路由，路径不匹配。只改 base_url，path 路径没有同步修改。
- 排查要点：
1. 脚本正常读取到 6 条用例 → yaml 解析模块正常，文件格式没问题。
2. 全部返回 404，字段全部 None → http 请求访问地址不存在。
3. 打印拼接后的完整请求 URL，核对目标接口文档，确认 path 路径不兼容。
- **解决**：重写整套 yaml 用例，使用 jsonplaceholder 原生路由`/posts/1`、`/posts`等。保留一条故意失败的用例，用来验证失败断言、报告标红功能。