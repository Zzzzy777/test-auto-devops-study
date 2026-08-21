import re
from playwright.sync_api import expect

def test_demo(page):
    page.goto("https://demo.playwright.dev/todomvc",timeout=20000)
    # 输入框新增todo
    input_box = page.get_by_placeholder("What needs to be done?")
    input_box.fill("学习Playwright")
    input_box.press("Enter")
    expect(page.locator(".todo-list li")).to_have_count(1)
