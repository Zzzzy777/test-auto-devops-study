# 方案B：Playwright UI 新增 + API 清理测试数据

## 1. 方案目标

本项目采用“UI 负责真实业务操作，API 负责测试数据清理”的组合方案：

- 使用 Playwright 从登录开始，真实操作 RuoYi 管理后台。
- 通过 UI 新增一个带 UUID 的唯一用户，并在页面上搜索校验新增结果。
- 无论 UI 用例成功还是失败，都在 `finally` 中调用后端 API 清理这个测试用户。
- 清理后再次查询用户名，确认数据库中不再残留测试数据。

这种设计比完全依赖数据库删除更贴近真实业务，也比完全使用 UI 删除更快、更稳定，适合作为中小厂测试开发岗位的综合自动化项目。

## 2. 测试流程

```mermaid
flowchart TD
    A[生成唯一用户名和手机号] --> B[Playwright 登录后台]
    B --> C[进入系统管理-用户管理]
    C --> D[UI 新增用户]
    D --> E[UI 搜索并校验用户存在]
    E --> F{测试是否成功}
    F -->|是| G[finally 调用 API 查询 userId]
    F -->|否| G
    G --> H[DELETE /system/user/{userId}]
    H --> I[API 再次查询用户名]
    I --> J{是否还有残留}
    J -->|否| K[清理完成]
    J -->|是| L[清理失败并让用例失败]
```

## 3. 为什么不直接用 UI 删除

UI 删除通常需要重新定位表格行、点击删除、处理确认弹窗、等待刷新，步骤更多，执行时间更长，也更容易受到分页、动画和 DOM 变化影响。

API 清理只需要：

1. 登录获取 Token。
2. 根据精确用户名查询 `userId`。
3. 调用删除接口。
4. 再次查询确认没有残留。

因此，UI 流程保留业务价值，API 流程承担高效、可靠的环境恢复职责。

## 4. API 登录与请求封装

RuoYi 后端地址为 `http://localhost:8081`，不是前端地址 `http://localhost:82`，也不是本机 Jenkins 使用的 `http://127.0.0.1:8080`。

登录接口：

```http
POST /login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}
```

登录成功后返回 Token，后续请求添加：

```http
Authorization: Bearer <token>
```

项目中的 `common/user_api.py` 使用 `requests.Session` 统一保存请求头，并在收到 401 时重新登录后重试一次。

## 5. 根据用户名查询并删除

查询接口：

```http
GET /system/user/list?userName=<username>&pageNum=1&pageSize=100
```

注意：接口返回的是用户列表，不能只判断接口 `code == 200`，还要对返回的 `rows` 做精确匹配：

```python
if row.get("userName") == username:
    user_id = row.get("userId")
```

删除接口：

```http
DELETE /system/user/{userId}
```

删除后必须再次查询同一个用户名。如果仍然查到用户，应该把它视为清理失败，而不是直接结束测试。

## 6. `try-finally` 保证清理

UI 用例的核心结构如下：

```python
test_error = None
try:
    # UI 登录、新增、搜索校验
    ...
except BaseException as exc:
    test_error = exc
    raise
finally:
    try:
        cleanup_result = api.cleanup_user_by_username(username)
        allure.attach(str(cleanup_result), "API清理结果")
    except Exception:
        allure.attach(traceback.format_exc(), "API清理异常")
        if test_error is None:
            raise
```

这里有两个关键点：

- UI 失败时仍然执行清理。
- 如果 UI 已经失败，清理失败不能覆盖原始 UI 异常；如果 UI 通过但清理失败，则必须让用例失败，防止测试数据污染环境。

## 7. 防止误删真实用户

UI 测试用户名统一使用：

```text
ui_test_<uuid>
```

API 清理方法只接受 `ui_test_` 前缀的用户名，并且根据完整用户名精确查询。这两层保护可以避免把 `admin` 或已有业务用户误当成测试数据删除。

## 8. 面试话术

> 我的项目采用 UI 和 API 结合的自动化策略。新增用户属于核心业务流程，所以从登录、菜单、弹窗填写到列表查询都使用 Playwright 完整覆盖，保证真实验证前端和后端联调结果。测试数据清理不使用 UI，而是在 `finally` 中调用 RuoYi 用户接口，根据唯一用户名查询 `userId` 后删除，并再次查询确认没有残留。这样既保留了 UI 自动化的业务价值，也提高了执行速度和稳定性。为了避免清理异常覆盖原始断言失败，我在 finally 中区分了 UI 原始异常和清理异常；UI 失败时保留原始错误，UI 通过但清理失败时则让用例失败，避免污染测试环境。

## 9. 本地运行

在项目根目录执行：

```powershell
cd D:\运维测试\test-auto-devops-study\Ruoyi_full_auto_test
pytest test_ui/test_ruoyi_user_add.py -s --headed --slowmo=600
```

也可以通过环境变量切换 API 地址或账号：

```powershell
$env:RUOYI_API_BASE_URL = "http://localhost:8081"
$env:RUOYI_API_USERNAME = "admin"
$env:RUOYI_API_PASSWORD = "admin123"
```