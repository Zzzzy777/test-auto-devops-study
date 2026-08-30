# Jenkins 配置说明

## 1. 前置条件

- Windows Jenkins Agent
- Agent 上可执行 `python`、`pip`、`java`
- RuoYi 前端监听 `82` 端口，后端监听 `8081` 端口
- Jenkins 已安装 Pipeline、JUnit、Allure 相关插件

## 2. 创建 Job

1. Jenkins 首页选择 **新建任务**。
2. 选择 **Pipeline**，例如命名为 `ruoyi-full-auto-test`。
3. 在 Pipeline 定义中选择 **Pipeline script from SCM**。
4. SCM 选择 Git，填写项目仓库地址和凭据。
5. Script Path 填写：`Ruoyi_full_auto_test/Jenkinsfile`。
6. 保存后先手动执行一次，确认 Agent 标签和工作目录权限。

## 3. 推荐凭据

不要把密码写入 Jenkinsfile。可以创建 Username with password 类型凭据，例如：

- ID：`ruoyi-test-account`
- 用户名：`admin`
- 密码：测试环境密码

然后在流水线环境中绑定为 `RUOYI_UI_USERNAME`、`RUOYI_UI_PASSWORD`。当前 Jenkinsfile 使用默认测试账号也可以直接运行，但正式展示时应改成 Credentials 注入。

## 4. 构建后查看

- **Test Result**：`reports/junit.xml`
- **Allure Report**：结果目录 `reports/allure-results`
- **构建产物**：`reports/**/*`
- **失败截图**：`reports/screenshots/fail/`
- **运行日志**：`reports/logs/pytest.log`

## 5. 常见失败排查

| 现象 | 排查方法 |
|---|---|
| 82/8081 端口检查失败 | 确认 RuoYi 服务已启动，并检查端口是否被防火墙拦截 |
| Chromium 启动失败 | 执行 `python -m playwright install chromium` |
| 登录失败 | 核对环境变量和测试账号，确认前后端地址没有写反 |
| 只有 Jenkins 失败 | 检查 Agent 使用的 Python、工作目录和权限 |
| Allure 没有页面 | 确认安装 Allure Jenkins 插件，并检查结果目录是否有文件 |

## 6. 面试中的 CI 说法

“我把测试入口统一放在 Jenkinsfile 中，构建时先检查被测服务，再安装依赖并以 headless 模式执行 UI/API 回归；失败时保留 JUnit、Allure、日志和截图，方便开发按构建号定位问题。”
