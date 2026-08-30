# 05 RuoYi UI 新增用户与 API 清理实战

## 1. 实战目标

本章把前面学习的定位器、等待、断言、fixture 和 Page Object 串成一条完整业务链：

```text
生成唯一数据
  → Playwright 登录 RuoYi
  → 进入系统管理/用户管理
  → UI 新增用户
  → UI 搜索并校验用户
  → finally 调用 API 查询并删除用户
  → API 再次查询确认无残留
```

这是一种常见的 UI/API 协同方案：UI 验证真实业务流程，API 负责高效、稳定的数据准备和清理。

## 2. 被测业务

RuoYi 用户管理页面主要包含：

- 用户名
- 用户昵称
- 手机号码
- 密码
- 性别、状态等选项
- 新增、修改、删除、搜索操作

本项目默认地址：

```text
前端：http://localhost:82
后端：http://localhost:8081
```

## 3. 用例设计

### 正向用例

| 编号 | 场景 | 关键断言 |
|---|---|---|
| UI-USER-001 | 新增用户成功 | 成功提示、弹窗关闭、列表出现用户 |
| UI-USER-002 | 用户搜索 | 搜索后目标用户行可见 |
| UI-USER-003 | 编辑用户 | 昵称和手机号变更后列表显示新值 |

### 异常用例

| 编号 | 场景 | 关键断言 |
|---|---|---|
| UI-USER-004 | 空表单提交 | 必填字段出现校验提示 |
| UI-USER-005 | 重复用户名 | 出现当前操作对应的错误提示，不能误判成功 |

## 4. 测试数据设计

数据工厂位于：

```text
../Ruoyi_full_auto_test/common/test_data.py
```

核心思路：

```python
user = build_unique_user(prefix="ui_test_")
```

生成的数据具有以下特征：

- 用户名包含 `ui_test_` 前缀
- 后缀使用 UUID，降低冲突概率
- 手机号由唯一值计算生成
- 每条用例独立生成，不依赖数据库中的固定用户名

不要使用这种固定数据作为新增用户用例唯一数据：

```python
username = "test001"
```

固定数据可能已经存在，也可能被其他人修改，导致用例无法重复执行。

## 5. Page Object 业务封装

用户页面对象位于：

```text
../Ruoyi_full_auto_test/pages/user_page.py
```

测试用例不直接操作大量 CSS，而是调用页面业务方法：

```python
LoginPage(page).login()
user_page = UserPage(page)
user_page.open()
user_page.add_user(user)
user_page.search_username(user.username)
user_page.assert_user_visible(user.username)
```

典型的页面对象方法职责：

| 方法 | 职责 |
|---|---|
| `open()` | 进入用户管理页面并等待表格 |
| `click_add()` | 打开新增用户弹窗 |
| `fill_user_form()` | 填写用户表单 |
| `submit_user()` | 提交表单并验证业务结果 |
| `search_username()` | 输入用户名并执行查询 |
| `assert_user_visible()` | 校验目标用户行 |
| `edit_user()` | 打开编辑弹窗、修改并保存 |

## 6. 正向用例结构

实际测试文件：

```text
../Ruoyi_full_auto_test/test_ui/test_ruoyi_user_add.py
```

核心结构如下：

```python
user = build_unique_user()
api = RuoYiUserApi()
test_error = None

try:
    LoginPage(page).login()
    user_page = UserPage(page)
    user_page.open()
    user_page.add_user(user)
    user_page.search_username(user.username)
    user_page.assert_user_visible(user.username)
except BaseException as exc:
    test_error = exc
    raise
finally:
    try:
        api.cleanup_user_by_username(user.username)
    except Exception:
        # UI 已失败时保留 UI 原始异常；UI 通过时才暴露清理异常
        if test_error is None:
            raise
```

## 7. 为什么清理放在 finally

如果把清理写在测试最后：

```python
user_page.add_user(user)
assert_user_visible(user.username)
api.cleanup_user_by_username(user.username)
```

当中间断言失败时，最后一行不会执行，测试数据就会残留。

放到 `finally` 后：

```text
业务通过 → 清理
业务失败 → 清理
定位器超时 → 清理
断言失败 → 清理
```

这是自动化测试中非常重要的数据生命周期设计。

## 8. 为什么用 API 清理，而不是 UI 删除

UI 删除通常需要：

1. 重新定位目标行
2. 点击删除按钮
3. 处理确认弹窗
4. 等待表格刷新
5. 再次确认数据消失

API 清理只需要：

```text
登录获取 token
  → 根据用户名查询 userId
  → DELETE /system/user/{userId}
  → GET 列表确认不存在
```

这样做的好处：

- 清理速度快
- 不依赖分页和表格动画
- 不受 UI 定位器变化影响
- 测试失败后仍然更容易执行

注意：API 清理不是为了绕过 UI 测试，而是把 UI 验证和环境恢复分工处理。

## 9. API 接口链路

### 登录

```http
POST http://localhost:8081/login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}
```

登录成功后，客户端保存 token：

```http
Authorization: Bearer <token>
```

### 查询用户

```http
GET /system/user/list?userName=ui_test_xxx&pageNum=1&pageSize=100
```

### 删除用户

```http
DELETE /system/user/{userId}
```

API 客户端位于：

```text
../Ruoyi_full_auto_test/common/user_api.py
```

## 10. 重复用户名的特殊问题

重复用户名用例中容易出现一种误判：

```text
第一次新增成功留下 Toast
  → 第二次提交重复用户名
  → 测试读到了旧的成功 Toast
  → 错误地认为第二次新增成功
```

更可靠的判断顺序：

1. 提交重复用户名
2. 判断新增弹窗没有被错误关闭
3. 读取当前操作产生的错误提示
4. 查询列表，确认没有新增重复数据
5. 用 API 清理原始测试用户

这也是为什么业务断言不能只依赖一条固定的 Toast 文本。

## 11. 运行和验证

```powershell
Set-Location 'D:\运维测试\test-auto-devops-study\Ruoyi_full_auto_test'
pytest test_ui/test_ruoyi_user_add.py -s --headed --slowmo=600
pytest test_ui/test_ruoyi_user_duplicate.py -s --headed --slowmo=600
pytest test_ui test_api --browser chromium -ra --tb=short
```

验证完成后检查是否残留测试用户：

```text
ui_test_*
api_test_*
```

## 12. 本章输出

完成本章后，应能独立解释：

- 为什么用户名要动态生成
- 为什么使用 Page Object
- 为什么清理放在 `finally`
- 为什么 UI 和 API 要协同
- 如何避免旧 Toast 导致误判
- UI 失败后如何保留原始异常并执行清理