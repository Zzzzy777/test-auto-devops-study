# 04 Fixture 与 Page Object

## 1. 为什么要分层

一个可维护的 UI 自动化项目通常分成四层：

```text
测试用例层     只描述业务步骤和断言
Page Object 层 封装页面定位器和页面操作
Fixture 层      管理登录、页面初始化、清理和测试上下文
公共能力层      配置、日志、数据工厂、API 客户端
```

如果把定位器、登录、数据生成和断言全部写在测试函数里，页面一改，很多用例都会一起修改。

## 2. Fixture 是什么

Fixture 是 pytest 提供的测试前置/后置能力。它可以把重复的准备动作提取出来：

```python
import pytest

@pytest.fixture
def user_page(page):
    LoginPage(page).login()
    users = UserPage(page)
    users.open()
    return users
```

用例直接使用：

```python
def test_search_user(user_page):
    user_page.search_username("ui_test_demo")
```

## 3. 项目中的 fixture 关系

项目使用 pytest-playwright 的 `page` fixture，再在根 `conftest.py` 中扩展它：

```python
@pytest.fixture(scope="function")
def page(page, request):
    page.goto(FRONTEND_LOGIN_URL, wait_until="domcontentloaded")
    yield page
    # 用例失败时保存截图
    page.close()
```

`test_ui/conftest.py` 再基于 `page` 提供用户管理页面：

```python
@pytest.fixture
def user_page(page: "Page"):
    LoginPage(page).login()
    users = UserPage(page)
    users.open()
    return users
```

这样测试用例不需要重复编写“登录 → 点击系统管理 → 点击用户管理”。

## 4. Fixture 作用域

| scope | 生命周期 | 适用场景 |
|---|---|---|
| `function` | 每条测试一次 | 页面、测试数据、独立业务状态 |
| `class` | 每个测试类一次 | 一组共享但不易污染的准备动作 |
| `module` | 每个模块一次 | 稳定的只读资源 |
| `session` | 整个测试会话一次 | 配置、连接池等全局资源 |

浏览器页面和用户数据通常使用 `function`，保证测试隔离。不要为了减少几秒执行时间就让多个用例共享会变化的页面状态。

## 5. Page Object 应该封装什么

适合放在 Page Object 中：

- 元素定位器
- 点击、输入、选择等页面操作
- 页面跳转
- 页面级业务动作
- 与页面结构强相关的断言辅助

不适合放在 Page Object 中：

- 多个模块组合的完整测试流程
- 测试数据生成策略
- 数据库清理实现
- Jenkins 命令

示例：

```python
class LoginPage:
    def __init__(self, page, timeout=UI_TIMEOUT):
        self.page = page
        self.timeout = timeout

    def login(self, username, password):
        self.page.locator('input[type="text"]').first.fill(username)
        self.page.locator('input[type="password"]').fill(password)
        self.page.locator("button.el-button--primary").click()
        self.page.wait_for_url("**/index", timeout=self.timeout)
```

## 6. 页面对象的设计原则

### 一个动作一个方法

```python
user_page.click_add()
user_page.fill_user_form(user)
user_page.submit_user()
```

比把所有动作写成一个巨大的 `add_user()` 更容易定位失败位置。对于稳定的业务动作，可以再提供组合方法：

```python
user_page.add_user(user)
```

### 定位器集中管理

不要在测试用例中散落大量 CSS：

```python
# 不推荐
page.locator(".el-dialog:visible input").nth(0).fill(username)
```

推荐：

```python
user_page.fill_user_form(user)
```

### 断言靠近业务结果

```python
user_page.search_username(user.username)
user_page.assert_user_visible(user.username)
```

测试函数读起来像测试步骤，而不是 DOM 操作脚本。

## 7. 测试数据工厂

项目中的 `build_unique_user()` 使用 UUID 生成唯一用户名：

```python
user = build_unique_user(prefix="ui_test_")
```

数据工厂的好处：

- 避免固定用户名冲突
- 支持并行执行
- 统一字段格式
- 用例只关心业务，不关心随机数据细节

## 8. 清理责任

创建数据的用例必须承担清理责任：

```python
api = RuoYiUserApi()
try:
    user_page.add_user(user)
    user_page.assert_user_visible(user.username)
finally:
    api.cleanup_user_by_username(user.username)
```

`finally` 能保证 UI 断言失败时仍然执行清理。清理失败时不能覆盖原始 UI 失败，应保留原始异常并记录清理异常。

## 9. 本章练习

1. 找到 `test_ui/conftest.py`，说明 `user_page` fixture 做了哪些动作。
2. 找到 `pages/user_page.py`，找出新增、搜索和编辑方法。
3. 将一条测试用例中的重复登录步骤改为 fixture。
4. 新增一个页面操作方法，但不在测试函数中直接写 CSS 定位器。
5. 让一个创建数据的用例在断言失败后仍然能删除测试数据。