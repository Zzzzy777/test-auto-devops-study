"""\u7528\u6237\u5220\u9664 UI \u6d4b\u8bd5\u3002"""

import allure
from playwright.sync_api import expect

from common.test_data import build_unique_user
from common.user_api import RuoYiUserApi


@allure.feature("\u7528\u6237\u7ba1\u7406\u6a21\u5757-UI")
@allure.story("\u5220\u9664\u7528\u6237")
def test_ui_delete_user(user_page):
    """\u65b0\u589e\u6d4b\u8bd5\u7528\u6237\u540e\u901a\u8fc7 UI \u5220\u9664\u3002"""
    user = build_unique_user()
    api = RuoYiUserApi()
    try:
        user_page.add_user(user)
        user_page.search_username(user.username)
        # ????????? DELETE ??????????????????????
        user_page.delete_user(user.username)
        rows = user_page.page.locator(
            ".el-table__body-wrapper tbody tr"
        ).filter(has_text=user.username)
        expect(rows).to_have_count(0, timeout=8000)
    finally:
        api.cleanup_user_by_username(user.username)
