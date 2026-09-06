"""\u7528\u6237\u67e5\u8be2\u6761\u4ef6\u91cd\u7f6e UI \u6d4b\u8bd5\u3002"""

import allure
from playwright.sync_api import expect


@allure.feature("\u7528\u6237\u7ba1\u7406\u6a21\u5757-UI")
@allure.story("\u91cd\u7f6e\u67e5\u8be2\u6761\u4ef6")
def test_ui_reset_user_search(user_page):
    """\u8f93\u5165\u67e5\u8be2\u6761\u4ef6\u540e\u70b9\u51fb\u91cd\u7f6e\u3002"""
    user_page.search_username("not_exist_test_user")
    search_input = user_page.page.locator("input.el-input__inner").nth(1)
    user_page.reset_search()
    expect(search_input).to_have_value("", timeout=5000)
