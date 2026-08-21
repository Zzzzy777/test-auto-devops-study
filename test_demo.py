import re
from playwright.sync_api import expect

def test_baidu_demo(page):
    page.goto("https://www.baidu.com")
    expect(page).to_have_title(re.compile("百度"))

    # 使用name属性定位搜索框，比#kw稳定很多
    search_input = page.locator('[name="wd"]')
    search_input.fill("软件测试")

    # 定位“百度一下”按钮点击
    page.get_by_role("button", name="百度一下").click()

    # 断言搜索结果标题可见
    expect(page.locator("h3")).to_be_visible()
