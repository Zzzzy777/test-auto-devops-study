# 01 Playwright 核心模型

## 1. Playwright 解决什么问题

Playwright 是浏览器自动化工具。它不仅能点击和输入，还能控制浏览器上下文、监听网络、截取页面、保存 trace，并通过自动等待降低 UI 测试的不稳定性。

UI 自动化的核心不是“把鼠标操作录下来”，而是用代码验证业务结果：

```text
打开登录页
  → 输入账号密码
  → 点击登录
  → 等待页面进入首页
  → 断言 URL、用户昵称和关键元素
```

## 2. Browser、Context、Page、Locator

```text
Browser
└─ BrowserContext  测试隔离环境，类似一个独立浏览器用户
   └─ Page         一个标签页
      └─ Locator   对元素的延迟定位和操作入口
```

| 对象 | 作用 | 项目中的体现 |
|---|---|---|
| Browser | 浏览器进程 | pytest-playwright 管理 |
| BrowserContext | Cookie、Storage、权限隔离 | 每条用例独立上下文 |
| Page | 当前页面或标签页 | `page.goto()`、`page.locator()` |
| Locator | 稳定查找元素 | `page.get_by_text()`、`page.locator()` |
| Expect | 自动重试断言 | `expect(locator).to_be_visible()` |

## 3. 为什么推荐 Locator

不推荐先查找 ElementHandle 再手工操作：

```python
# 不推荐：元素可能在查找后、操作前发生变化
handle = page.query_selector("button")
handle.click()
```

推荐使用 Locator：

```python
from playwright.sync_api import expect

button = page.get_by_role("button", name="登录")
expect(button).to_be_visible()
button.click()
```

Locator 会在真正执行操作时重新解析元素，并且 Playwright 会自动等待元素满足可操作条件。

## 4. 同步 API 与异步 API

本项目使用同步 API：

```python
from playwright.sync_api import Page

def test_login(page: Page):
    page.goto("http://localhost:82/login")
```

异步 API 写法：

```python
from playwright.async_api import Page

async def test_login(page: Page):
    await page.goto("http://localhost:82/login")
```

两种 API 不要混用。同步项目中不要写 `await`，异步项目中要保证所有 Playwright 调用都 `await`。

## 5. Page 的常用能力

```python
# 页面跳转
page.goto(url, wait_until="domcontentloaded")

# 元素操作
page.get_by_label("用户名").fill("admin")
page.get_by_role("button", name="登录").click()
page.get_by_text("用户管理", exact=True).click()

# 获取结果
text = page.locator(".el-table").inner_text()
value = page.locator("input").input_value()

# 等待
page.wait_for_url("**/index")
page.wait_for_load_state("networkidle")

# 调试
page.screenshot(path="debug.png", full_page=True)
page.pause()
```

## 6. Context 隔离的意义

每条测试最好拥有独立的 Cookie、LocalStorage 和页面状态：

```text
用例 A 登录 → 用例 A 的 Context
用例 B 登录 → 用例 B 的 Context
```

这样一条用例失败，不会把登录状态、弹窗状态或搜索条件污染给下一条用例。不要依赖测试执行顺序，也不要让一条测试必须依赖另一条测试先执行。

## 7. 本章练习

1. 用 `page.goto()` 打开 RuoYi 登录页。
2. 使用 `page.get_by_text()` 定位一个菜单。
3. 使用 `expect(page).to_have_url()` 断言页面地址。
4. 分别用 headed 和 headless 执行同一条用例。
5. 故意把 URL 写错，观察 Playwright 的超时信息。

## 8. 对照项目代码

- 登录封装：`../Ruoyi_full_auto_test/pages/login_page.py`
- 用户页面封装：`../Ruoyi_full_auto_test/pages/user_page.py`
- 全局页面 fixture：`../Ruoyi_full_auto_test/conftest.py`