"""\u767b\u5f55\u6a21\u5751\u5f02\u5e38\u573a\u666f UI \u6d4b\u8bd5\u3002"""

import allure
from playwright.sync_api import Page

from pages.login_page import LoginPage


@allure.feature("UI\u767b\u5f55\u6a21\u5751")
class TestLoginErrorUi:
    """\u8986\u76d6\u9519\u8bef\u5bc6\u7801\u3001\u7a7a\u8d26\u53f7\u548c\u7a7a\u5bc6\u7801\u3002"""

    @allure.story("\u9519\u8bef\u5bc6\u7801\u767b\u5f55")
    def test_login_wrong_password(self, page: Page) -> None:
        LoginPage(page).login_expect_error(
            "admin", "wrong_password", "\u7528\u6237\u4e0d\u5b58\u5728/\u5bc6\u7801\u9519\u8bef"
        )

    @allure.story("\u7a7a\u8d26\u53f7\u767b\u5f55")
    def test_login_empty_username(self, page: Page) -> None:
        LoginPage(page).login_expect_validation(
            "", "admin123", "\u8bf7\u8f93\u5165\u60a8\u7684\u8d26\u53f7"
        )

    @allure.story("\u7a7a\u5bc6\u7801\u767b\u5f55")
    def test_login_empty_password(self, page: Page) -> None:
        LoginPage(page).login_expect_validation(
            "admin", "", "\u8bf7\u8f93\u5165\u60a8\u7684\u5bc6\u7801"
        )
