# Pytest + Allure 接口自动化报告
## 1.学习目标
1. 使用pytest执行Python接口测试脚本
2. allure‑pytest生成原始测试结果 `allure‑results`
3. allure命令行生成可视化HTML测试报告

## 2.环境依赖安装
```bash
pip install requests
pip install pytest
pip install allure-pytest
```
>注意：allure‑pytest只是 Python 库，还需要单独下载 Allure 命令行工具才能生成网页。
- >1.allure-pytest：运行用例、收集用例数据，产出 allure-results
- >2.Allure 命令行工具：读取原始数据，生成可视化 HTML 报告

## 3.Allure 三大核心注解
### 层级关系：feature（模块） > story（子场景） > title（用例标题）
| 注解 | 作用 | 使用位置 |
| --- | --- | --- |
| @allure.feature ("模块名称") | 一级大功能模块，报告 Behaviors 分类 | 测试类上方 |
| @allure.story ("功能场景") |模块下细分业务场景 | 测试方法上方 |
| @allure.title ("用例名称") | 自定义报告展示的用例标题，替代默认函数名	| 测试方法上方 |

### 示例代码片段：
```pytho
@allure.feature("httpbin接口测试")
class TestHttpbinApi:
    @allure.story("get请求参数测试")
    @allure.title("测试get接口传参校验")
    def test_get_params(self):
        pass
```

## 4.执行步骤
1. 运行 pytest，产出 allure‑results 原始数据
```bash
pytest test_01_api_allure.py -s --alluredir=allure-results
```

2. 生成 allure 网页报告(本机 Path 环境变量异常，使用 allure.bat 完整路径执行)
```bash
D:\allure-2.45.0\bin\allure.bat generate allure-results -o allure-report --clean
```

3. 打开网页报告
>❗坑点：禁止直接双击 index.html，会报 500 Failed to fetch 跨域错误
```bash
D:\allure-2.45.0\bin\allure.bat open allure-report
```

## 5.日志脚本 simple_log.py 说明
### 作用
自动化测试不能只用 print 打印：print 仅临时输出控制台，无法留存；logging 可同时输出控制台 + 写入本地 log 文件，报错后可回溯排查问题。

### 核心知识点
1. 日志级别：INFO（正常信息）、WARNING（警告）、ERROR（错误）
2. handlers 配置：同时绑定控制台输出、文件输出
3. 自动生成run.log永久保存全部运行日志

### 运行命令：
```bash
python simple_log.py
```

## 6.遇到的问题总结
1. allure 不是内部或外部命令：allure 命令行未配置环境变量，改用完整 bat 路径运行。
2. 双击打开 index.html 出现500 Failed to fetch：allure 报告是前端服务，必须启动 web 服务访问。
3. JSONDecodeError：接口返回 503/404 等非 200 状态，先断言 status_code==200 再解析 json。