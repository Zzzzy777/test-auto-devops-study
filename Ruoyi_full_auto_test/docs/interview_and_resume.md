# 秋招项目描述与面试提纲

## 一、简历项目描述（可直接改写）

### RuoYi 后台全链路自动化测试项目

- 基于 Python、pytest、Playwright、Requests 搭建 UI/API 自动化测试框架，覆盖登录、用户新增、必填校验、重复用户名、查询、编辑、删除等核心场景。
- 使用 Page Object 封装登录页和用户管理页，降低定位器与测试业务步骤耦合，提高脚本可维护性。
- 通过 Requests 封装登录、用户增删改查接口，使用 token 鉴权，并用 API 清理 UI 用例产生的测试数据，保证用例可重复执行。
- 引入 UUID 动态生成测试用户名，结合 `try/finally`、日志、失败截图、Allure 和 JUnit 报告提升问题定位效率。
- 编写 Jenkins Windows Agent 流水线，自动检查服务端口、安装依赖、headless 执行 UI/API 回归并归档测试产物。
- 使用 JMeter 建立登录和用户列表接口性能基线，记录平均响应时间、P95、吞吐量和错误率。

### 技术栈

`Python` `pytest` `Playwright` `Requests` `MySQL` `Allure` `Jenkins` `JMeter` `Git`

## 二、面试讲解顺序

1. **业务**：RuoYi 是后台管理系统，本项目选择用户管理作为高频且有增删改查风险的模块。
2. **框架**：公共配置、日志、数据工厂、Page Object、API Client、pytest fixture 分层组织。
3. **UI/API 分工**：UI 验证真实用户路径；API 用于快速校验和清理数据，减少 UI 删除操作带来的不稳定性。
4. **数据隔离**：用户名增加 `ui_test_`/`api_test_` 前缀和 UUID，结束后按用户名查询并删除。
5. **稳定性**：显式等待业务元素，不用固定 sleep 作为主要等待手段；断言当前 Toast、弹窗状态和列表数据。
6. **CI**：Jenkins 中使用 headless 浏览器，失败保留 JUnit、Allure、日志和截图。
7. **性能**：JMeter 先做小并发基线，再逐步增加并发，不能把一次本地测试结果直接说成生产容量。

## 三、AI 辅助如何诚实表达

可以这样说：

> 我使用 AI 作为编码和排错辅助工具，例如根据报错分析 Playwright 定位问题、生成重复代码初稿、协助检查 Jenkinsfile；但我自己负责场景设计、接口抓包确认、断言选择、数据清理策略、失败复现和最终回归验证。代码不是直接复制后提交，而是结合 RuoYi 实际页面和接口调试完成的。

面试官继续追问时，要能现场解释：

- 为什么使用 `get_by_role`/`get_by_text`/CSS 定位，以及定位不稳定时如何改进
- 登录 token 从哪里来、如何放入 `Authorization` 请求头
- 为什么测试数据一定要唯一、清理失败如何处理
- Jenkins 为什么不传 `--headed`，失败截图如何产生
- API 断言为什么同时检查 HTTP 状态和业务 `code`
- 性能报告中的平均值、P95、吞吐量和错误率分别说明什么

## 四、不要夸大的内容

- 没有真实 Jenkins 构建记录时，说“已编写并本地等价验证 Jenkinsfile”，不要说“已在线上 Jenkins 稳定运行数月”。
- 没有多轮压测和服务器监控时，说“建立接口性能基线”，不要说“系统支持多少并发”。
- 没有真实缺陷单时，将 `docs/defect_report.md` 作为缺陷报告模板，不要冒充生产缺陷。
