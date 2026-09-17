# Mall 电商系统自动化测试项目

这是一个可本地运行、可接入 Jenkins CI 的电商测试项目，包含 Mall 电商系统源码、部署脚本和三类自动化测试：

- 接口自动化测试：Python + pytest + requests + Allure
- UI 自动化测试：Python + Playwright + pytest + Allure
- 性能测试：Apache JMeter + HTML Dashboard
- 持续集成：Jenkins Pipeline

## 1. 项目结构

```text
.
├── automation
│   ├── api                         # 接口自动化测试
│   │   ├── common                  # HTTP 客户端等公共代码
│   │   ├── config                  # 接口测试配置
│   │   ├── tests                   # 接口测试用例
│   │   └── requirements.txt
│   └── ui                          # UI 自动化和性能测试
│       ├── config                  # UI 测试配置
│       ├── performance             # JMeter .jmx 脚本和性能基线
│       ├── tests                   # Playwright UI 用例
│       └── requirements.txt
├── source
│   ├── mall-backend                # Mall 后端源码
│   ├── mall-admin-web              # 后台前端源码
│   └── mall-app-web                # 商城 H5 前端源码
├── test_docs                       # 测试计划、用例、测试总结
├── Jenkinsfile                     # Jenkins CI 流水线
├── DEPLOYMENT.md                   # 本地部署说明
├── setup-and-build.ps1             # 构建后端和两个前端
├── start-all.ps1                   # 启动项目服务
├── stop-all.ps1                    # 停止项目服务
└── check-all.ps1                   # 检查容器、端口和健康接口
```

仓库默认忽略 `node_modules`、Maven `target`、Python 虚拟环境、测试报告、截图和运行日志。克隆后执行安装和构建命令即可恢复这些文件。

## 2. 环境要求

建议使用以下版本或兼容版本：

- Windows 10/11
- JDK 17
- Maven 3.9+
- Node.js 20+
- Python 3.10+
- Docker Desktop
- Apache JMeter 5.6+
- Jenkins（Windows Agent）

## 3. 本地启动

先启动 Docker Desktop，然后在仓库根目录执行：

```powershell
powershell -ExecutionPolicy Bypass -File .\setup-and-build.ps1
powershell -ExecutionPolicy Bypass -File .\start-all.ps1
powershell -ExecutionPolicy Bypass -File .\check-all.ps1
```

停止服务：

```powershell
powershell -ExecutionPolicy Bypass -File .\stop-all.ps1 -KeepInfrastructure
```

端口和账号请查看 [DEPLOYMENT.md](DEPLOYMENT.md)。启动脚本使用 `$PSScriptRoot`，因此项目复制到其他目录后不需要修改 D 盘路径；Java、Maven、Node.js 从系统 `PATH` 查找。

## 4. 执行接口测试

```powershell
cd automation\api
python -m pip install -r requirements.txt
python -m pytest -q
```

接口测试结果默认生成在：

```text
automation/api/reports/allure-results
```

## 5. 执行 UI 测试

```powershell
cd automation\ui
python -m pip install -r requirements.txt
python -m playwright install chromium
python -m pytest -q --browser chromium --headless
```

UI 测试默认访问：

```text
http://localhost:8060
```

## 6. 执行 JMeter 性能测试

单用户调试时可以打开 JMeter GUI；正式测试使用非 GUI 模式：

```powershell
New-Item -ItemType Directory -Force .\automation\ui\performance\results | Out-Null
jmeter -n `
  -t .\automation\ui\performance\mall_product_flow.jmx `
  -l .\automation\ui\performance\results\mall_product_flow.jtl `
  -e `
  -o .\automation\ui\performance\reports\mall_product_flow
```

JMeter 报告入口为：

```text
automation/ui/performance/reports/mall_product_flow/index.html
```

## 7. Jenkins CI

Jenkins 节点必须能够执行以下命令：

```text
python
node
npm
java
mvn
jmeter
```

Jenkins 还需要安装：

- Allure Jenkins Plugin
- HTML Publisher Plugin
- Pipeline 相关插件

创建 Pipeline 任务，选择 **Pipeline script from SCM**，填写 GitHub 仓库地址，脚本路径填写：

```text
Jenkinsfile
```

流水线会依次执行：

```text
Checkout
→ 工具检查
→ 安装测试依赖
→ 检查前后端服务
→ 接口自动化测试
→ UI 自动化测试
→ JMeter 性能测试
→ 发布 Allure 报告和 JMeter HTML 报告
```

当前 Jenkinsfile 默认测试已经启动的本地服务。如果 Jenkins 与服务不在同一台机器，需要把测试配置中的 `localhost` 改为测试环境地址，或在流水线前增加部署/启动阶段。

## 8. GitHub 上传前检查

不要提交以下内容：

- `node_modules`
- Maven `target`
- Python `.venv`
- 测试报告和运行日志
- 个人机器专属路径
- 真实生产密码、Token、OSS 密钥

本项目已经提供 `.env.example` 模板。公开仓库前请再次检查配置文件和提交内容：

```powershell
git status --short
git diff --check
git grep -n -I -E 'AKIA|accessKeySecret|password:.*[^0-9]'
```

示例账号仅用于本地测试环境，不要将生产环境凭据写入仓库。
