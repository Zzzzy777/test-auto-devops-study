"""\u7528\u6237\u7ba1\u7406\u53d6\u6d88\u64cd\u4f5c UI \u6d4b\u8bd5\u3002"""

import allure
from common.test_data import build_unique_user


@allure.feature("\u7528\u6237\u7ba1\u7406\u6a21\u5757-UI")
@allure.story("\u53d6\u6d88\u65b0\u589e\u7528\u6237")
def test_ui_cancel_add_user(user_page):
    """\u6253\u5f00\u65b0\u589e\u5f39\u7a97\u540e\u53d6\u6d88\uff0c\u786e\u8ba4\u4e0d\u4f1a\u521b\u5efa\u7528\u6237\u3002"""
    user = build_unique_user()
    user_page.click_add()
    user_page.fill_add_form(user)
    user_page.cancel_add()
