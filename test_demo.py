import re

def test_baidu_demo(page):
    page.goto("https://www.baidu.com")
    expect(page).to_have_title(re.compile("百度"))
    page.locator("#kw").fill("软件测试")
    page.locator("#su").click()
    expect(page.locator("h3")).to_be_visible()
