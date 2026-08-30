# 06 报告、调试与 Jenkins

## 1. 调试模式与 CI 模式

### headed：观察浏览器过程

```powershell
pytest test_ui/test_ruoyi_user_add.py -s --headed --slowmo=600
```

适合：

- 第一次开发用例
- 观察菜单、弹窗和表格
- 检查定位器是否点击到正确元素
- 复现页面交互问题

### headless：持续集成执行

```powershell
pytest test_ui test_api --browser chromium -ra --tb=short
```

当前 pytest-playwright 版本中，不传 `--headed` 就是 headless 模式，不要额外传不存在的 `--headless` 参数。

## 2. 日志设计

统一日志封装在：

```text
../Ruoyi_full_auto_test/common/logger.py
```

建议日志记录：

- 当前执行的业务动作
- 测试数据用户名
- 页面跳转结果
- API 清理结果
- 异常堆栈

示例：

```python
logger.info("开始执行新增用户用例: %s", user.username)
logger.exception("新增用户 UI 用例失败: %s", user.username)
```

日志要记录“发生了什么”，不要只打印“失败”。

## 3. 失败截图

全局钩子位于：

```text
../Ruoyi_full_auto_test/conftest.py
```

通过 `pytest_runtest_makereport` 获取测试结果：

```python
if request.node.rep_call.failed:
    page.screenshot(path=str(screenshot_path), full_page=True)
```

失败截图保存到：

```text
../Ruoyi_full_auto_test/reports/screenshots/fail/
```

文件名包含测试节点名称和时间戳，便于并发或多次执行时区分。

## 4. Allure 与 JUnit

生成 Allure 和 JUnit：

```powershell
pytest test_ui test_api `
  --browser chromium `
  --alluredir=reports/allure-results `
  --junitxml=reports/junit.xml `
  -ra --tb=short
```

查看 Allure：

```powershell
allure serve reports/allure-results
```

两种报告的定位不同：

| 报告 | 作用 |
|---|---|
| JUnit XML | Jenkins 识别通过/失败数量，适合趋势统计 |
| Allure | 查看用例、步骤、附件、截图和失败详情 |
| pytest.log | 查看完整运行日志和异常堆栈 |
| 失败截图 | 直观看到失败时页面状态 |

## 5. Jenkins 工作目录问题

本项目仓库结构是：

```text
仓库根目录/
└─ Ruoyi_full_auto_test/
   ├─ requirements.txt
   ├─ test_ui/
   ├─ test_api/
   └─ Jenkinsfile
```

Jenkins 默认工作目录是仓库根目录。如果直接执行：

```powershell
python -m pip install -r requirements.txt
pytest test_ui test_api
```

就会找不到文件。

项目 Jenkinsfile 使用：

```groovy
dir('Ruoyi_full_auto_test') {
    powershell {
        // 在项目子目录执行命令
    }
}
```

同时，Jenkins 的报告路径要从仓库根目录写：

```groovy
junit testResults: 'Ruoyi_full_auto_test/reports/junit.xml'
archiveArtifacts artifacts: 'Ruoyi_full_auto_test/reports/**/*'
```

## 6. Jenkins 流程

```text
Checkout SCM
  → 检查 82/8081 端口
  → 进入 Ruoyi_full_auto_test
  → 安装 Python 依赖
  → 安装 Chromium
  → headless 执行 UI/API
  → 发布 JUnit 和 Allure
  → 归档日志、截图和报告
```

Jenkins Script Path：

```text
Ruoyi_full_auto_test/Jenkinsfile
```

## 7. Jenkins 环境变量

Jenkinsfile 中可以配置默认值，也可以由 Job 环境变量覆盖：

```text
RUOYI_FRONTEND_BASE_URL
RUOYI_API_BASE_URL
RUOYI_UI_USERNAME
RUOYI_UI_PASSWORD
RUOYI_API_USERNAME
RUOYI_API_PASSWORD
RUOYI_UI_TIMEOUT
RUOYI_API_TIMEOUT
```

真实密码不要写进 Jenkinsfile。推荐通过 Jenkins Credentials 注入。

## 8. CI 失败排查顺序

### 第一步：看 Checkout

确认：

- 仓库地址正确
- 分支是 `main`
- Script Path 是 `Ruoyi_full_auto_test/Jenkinsfile`

### 第二步：看服务检查

确认：

```powershell
Test-NetConnection localhost -Port 82
Test-NetConnection localhost -Port 8081
```

### 第三步：看依赖安装

确认 Jenkins Agent 上：

```powershell
python --version
python -m pip --version
java -version
```

### 第四步：看测试收集

如果出现：

```text
file or directory not found: test_ui
```

优先检查当前目录和 `dir('Ruoyi_full_auto_test')` 是否存在。

### 第五步：看报告路径

测试失败时也要让 post action 能找到报告；路径必须和 Jenkins workspace 的层级一致。

## 9. 本章练习

- 先 headed 执行一条失败用例，观察页面。
- 再 headless 执行同一条用例，检查报告目录。
- 故意把 Jenkinsfile 中的工作目录改错，理解错误日志。
- 从 Allure 中找到失败截图和测试数据。