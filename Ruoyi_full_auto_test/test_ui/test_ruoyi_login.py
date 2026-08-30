import allure

@allure.feature("UI登录模块")
@allure.story("管理员正常登录")
def test_login(page):
    page.goto("http://localhost:82/login")
    # 输入账号密码
    page.locator('input[type="text"]').first.fill("admin")
    page.locator('input[type="password"]').fill("admin123")

    # 点击登录，等待跳转
    with page.expect_navigation():
        page.locator("button.el-button--primary").click()

    # 断言1：URL跳转到首页
    assert "/index" in page.url, f"登录失败，当前url：{page.url}"
    # 断言2：右上角用户昵称
    assert page.locator(".user-nickname").is_visible(timeout=8000), "未找到右上角用户名"