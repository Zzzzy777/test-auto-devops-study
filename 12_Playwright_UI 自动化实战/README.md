# Playwright UI 自动化实战笔记

这是一套围绕 RuoYi 后台用户管理模块整理的 Playwright 实战笔记，目标是把“会录制几个操作”提升为“能够设计、编写、调试和维护 UI 自动化测试”。

## 学习主线

```mermaid
flowchart LR
    A[测试环境准备] --> B[Playwright 核心模型]
    B --> C[定位器与页面操作]
    C --> D[等待与断言]
    D --> E[fixture 与 Page Object]
    E --> F[RuoYi 用户管理实战]
    F --> G[API 清理测试数据]
    G --> H[Allure/JUnit/Jenkins]
    H --> I[稳定性与进阶能力]
```

## 推荐阅读顺序

| 顺序 | 笔记 | 重点 |
|---|---|---|
| 1 | [前置准备](./前置准备.md) | 环境、依赖、浏览器和服务检查 |
| 2 | [01 Playwright 核心模型](./01_Playwright核心模型.md) | Browser、Context、Page、Locator |
| 3 | [02 定位器与元素操作](./02_定位器与元素操作.md) | 稳定定位、表格、弹窗、表单 |
| 4 | [03 等待、断言与稳定性](./03_等待断言与稳定性.md) | 自动等待、显式等待、反向断言 |
| 5 | [04 Fixture 与 Page Object](./04_Fixture与PageObject.md) | 测试分层、复用和清理 |
| 6 | [05 RuoYi UI 新增与 API 清理](./05_RuoYi_UI新增与API清理.md) | 完整项目用例拆解 |
| 7 | [06 报告、调试与 Jenkins](./06_报告调试与Jenkins.md) | 失败截图、Allure、CI |
| 8 | [07 API 协同与性能测试](./07_API协同与性能测试.md) | API 清理、JMeter 基线 |
| 9 | [08 踩坑记录](./08_踩坑记录.md) | 根据实际报错总结解决套路 |
| 10 | [09 进阶练习](./09_进阶练习.md) | trace、并行、网络拦截、参数化 |
| 11 | [10 复习问答](./10_复习问答.md) | 用自己的话解释项目设计 |

## 对应项目代码

项目代码位于同级目录：

```text
../Ruoyi_full_auto_test/
```

建议边看笔记边打开以下文件：

| 代码 | 对应内容 |
|---|---|
| `../Ruoyi_full_auto_test/pages/login_page.py` | 登录 Page Object |
| `../Ruoyi_full_auto_test/pages/user_page.py` | 用户管理 Page Object |
| `../Ruoyi_full_auto_test/common/test_data.py` | 动态测试数据 |
| `../Ruoyi_full_auto_test/common/user_api.py` | API 鉴权、查询和清理 |
| `../Ruoyi_full_auto_test/conftest.py` | fixture、失败截图和日志 |
| `../Ruoyi_full_auto_test/test_ui/` | UI 自动化用例 |
| `../Ruoyi_full_auto_test/test_api/` | API 自动化用例 |
| `../Ruoyi_full_auto_test/Jenkinsfile` | Windows Agent CI 流水线 |

## 环境和运行命令

### 默认服务

| 服务 | 地址 |
|---|---|
| RuoYi 前端 | `http://localhost:82` |
| RuoYi 后端 API | `http://localhost:8081` |
| Jenkins | `http://localhost:8080` |

### 安装

在 `Ruoyi_full_auto_test` 目录执行：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m playwright install chromium
```

### headed 调试

```powershell
pytest test_ui/test_ruoyi_login.py -s --headed --slowmo=600
pytest test_ui/test_ruoyi_user_add.py -s --headed --slowmo=600
```

### 全量 headless 回归

```powershell
pytest test_ui test_api `
  --browser chromium `
  --alluredir=reports/allure-results `
  --junitxml=reports/junit.xml `
  -ra --tb=short
```

## 截图目录

`screenshots/` 保存了本次实战中的关键过程和错误现象：

- `01_fixture_page_not_found.png`：fixture 找不到
- `02_assert_username_not_found.png`：列表查询断言失败
- `03_strict_mode_2elements.png`：定位到多个元素
- `04_menu_text_multi_match.png`：菜单文本重复匹配
- `05_wait_for_timeout_add_btn.png`：不推荐用固定等待解决问题
- `06_wait_dialog_pop_timeout.png`：弹窗等待超时
- `07_overlay_block_click.png`：遮罩层阻挡点击
- `08_form_required_no_tip.png`：必填校验断言不准确
- `01_login_case_pass.png`：登录用例通过
- `02_ui_add_user_pass.png`：新增用户用例通过
- `03_Jenkins.png`：Jenkins 执行过程
- `04_final_Allure.png`：Allure 测试报告

## 学习成果检查

完成每一章后，不要只看代码，至少完成一个动作：

- 能说明这项技术解决什么问题
- 能在项目代码中指出它的使用位置
- 能故意制造一次失败并根据日志定位
- 能不用复制粘贴，重新写出最小示例
- 能解释为什么当前方案比简单的 `sleep + CSS` 更可靠

## 常用命令速查

```powershell
# 查看所有测试
pytest --collect-only -q

# 只跑 UI
pytest test_ui -s --headed --slowmo=300

# 只跑 API
pytest test_api -s

# 失败时显示短堆栈
pytest test_ui -s --tb=short

# 生成 Allure 结果
pytest test_ui test_api --alluredir=reports/allure-results

# 查看单个测试的帮助
pytest --help
```