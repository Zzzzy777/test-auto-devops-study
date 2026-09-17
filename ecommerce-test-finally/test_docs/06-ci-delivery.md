# Jenkins CI 配置说明

## Jenkins 节点

本项目的 Jenkinsfile 按 Windows Agent 编写，节点需要安装并配置 PATH：

```text
Python 3.10+
Node.js 20+
JDK 17+
Maven 3.9+
Apache JMeter 5.6+
```

在 Jenkins 节点命令行验证：

```powershell
python --version
node --version
npm --version
java -version
mvn --version
jmeter -v
```

## Jenkins 插件

安装：

- Pipeline
- Git
- Allure Jenkins Plugin
- HTML Publisher Plugin

## 创建任务

1. 新建 Pipeline 任务；
2. 选择 Pipeline script from SCM；
3. SCM 选择 Git；
4. 填写 GitHub 仓库地址和凭据；
5. 分支填写 `*/main` 或实际默认分支；
6. Script Path 填写 `Jenkinsfile`；
7. 点击 Build Now。

## 服务前置条件

Jenkinsfile 默认不负责启动 Docker 和前后端服务，而是在 `Check Application Services` 阶段检查以下地址：

```text
http://127.0.0.1:8082/actuator/health
http://127.0.0.1:8085/actuator/health
http://127.0.0.1:8090/
http://127.0.0.1:8060/
```

因此 Jenkins Agent 与被测服务应在同一台机器，或者将配置改为可访问的测试环境地址。

## 报告

- Allure 结果目录：`reports/allure-results`
- JMeter HTML 报告：`reports/jmeter/mall_product_flow/index.html`
- JMeter 原始结果：`reports/jmeter/mall_product_flow.jtl`

测试失败时 Jenkins 构建失败，同时仍会尝试归档已经生成的日志和报告。
