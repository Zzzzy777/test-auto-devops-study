import re
from playwright.sync_api import expect

def test_baidu_demo(page):
    # 访问百度
    page.goto("https://www.baidu.com")
    # 断言页面标题包含百度
    expect(page).to_have_title(re.compile("百度"))
    # 搜索框输入软件测试
    page.locator("#kw").fill("软件测试")
    # 点击搜索按钮
    page.locator("#su").click()
    # 断言搜索结果标题可见
    expect(page.locator("h3")).to_be_visible()
