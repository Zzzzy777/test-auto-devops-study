# Playwright 基础Demo实操记录
> 项目目录：`09_playwright学习了解`
> 技术栈：`pytest‑playwright`，复用pytest内置`page`夹具，实现简单Web自动化
> 学习定位：接口自动化方向，仅了解基础，不做复杂UI项目

## 文件
- `test_demo.py`：测试用例脚本

### test_demo.py 完整代码
```python
from playwright.sync_api import expect

def test_demo(page):
    """Playwright最小demo：Todomvc待办新增功能验证"""
    # 访问官方演示网站，设置超时时间
    page.goto("https://demo.playwright.dev/todomvc", timeout=20000)

    # 按占位符文本定位输入框
    input_box = page.get_by_placeholder("What needs to be done?")
    # 输入待办内容
    input_box.fill("学习Playwright")
    # 模拟键盘回车，提交新增待办
    input_box.press("Enter")

    # 断言：待办列表存在1条数据
    expect(page.locator(".todo-list li")).to_have_count(1)

    # 勾选第一条待办
    page.locator(".todo-list li .toggle").click()
    # 断言待办标记为已完成
    expect(page.locator(".todo-list li")).to_have_class("todo completed")
```

### Windows 运行命令
```cmd
# 无头模式，后台执行，不弹出浏览器
pytest test_demo.py -v

# 有头模式，弹出浏览器窗口
pytest test_demo.py -v --headed

# 有头模式 + 每步停顿1000ms，看清页面操作
pytest test_demo.py -v --headed --slowmo 1000

# PWDEBUG调试检查器，断点排错
set PWDEBUG=1
pytest test_demo.py -v -s

# 生成trace追踪包，可上传 trace.playwright.dev 回放执行全过程
pytest test_demo.py -v --tracing on

# codegen录制工具：手动操作网页自动生成Python测试代码
playwright codegen https://demo.playwright.dev/todomvc
```