from __future__ import annotations

import re

from playwright.sync_api import Page, expect

from common.config import FRONTEND_LOGIN_URL, UI_PASSWORD, UI_TIMEOUT, UI_USERNAME
from common.logger import get_logger


class LoginPage:
    """Page Object for the RuoYi login page."""

    def __init__(self, page: Page, timeout: int = UI_TIMEOUT) -> None:
        self.page = page
        self.timeout = timeout
        self.logger = get_logger(self.__class__.__name__)

    def login(
        self,
        username: str = UI_USERNAME,
        password: str = UI_PASSWORD,
    ) -> None:
        self.logger.info("打开登录页并登录账号: %s", username)
        self.page.goto(
            FRONTEND_LOGIN_URL,
            wait_until="domcontentloaded",
            timeout=self.timeout,
        )
        self.page.locator('input[type="text"]').first.fill(username)
        self.page.locator('input[type="password"]').fill(password)
        self.page.locator("button.el-button--primary").click()
        self.page.wait_for_url("**/index", timeout=self.timeout)
        self.logger.info("登录成功，当前地址: %s", self.page.url)

    def assert_login_success(self) -> None:
        expect(self.page).to_have_url(
            re.compile(r"/index(?:\?.*)?/?$"),
            timeout=self.timeout,
        )
        expect(self.page.locator(".user-nickname")).to_be_visible(timeout=8000)
        self.logger.info("登录成功断言通过")


    def login_expect_error(self, username: str, password: str, message: str) -> None:
        """\u63d0\u4ea4\u9519\u8bef\u8d26\u53f7\u6216\u5bc6\u7801\uff0c\u5e76\u6821\u9a8c\u9519\u8bef\u63d0\u793a\u3002"""
        self.page.goto(
            FRONTEND_LOGIN_URL,
            wait_until="domcontentloaded",
            timeout=self.timeout,
        )
        self.page.locator('input[type="text"]').first.fill(username)
        self.page.locator('input[type="password"]').fill(password)
        self.page.locator("button.el-button--primary").click()
        error = self.page.locator(".el-message.el-message--error").filter(
            has_text=message
        ).last
        expect(error).to_be_visible(timeout=8000)
        expect(self.page).to_have_url(re.compile(r"/login(?:\?.*)?/?$"))

    def login_expect_validation(self, username: str, password: str, message: str) -> None:
        """\u63d0\u4ea4\u7a7a\u8d26\u53f7\u6216\u7a7a\u5bc6\u7801\uff0c\u5e76\u6821\u9a8c\u8868\u5355\u5fc5\u586b\u63d0\u793a\u3002"""
        self.page.goto(
            FRONTEND_LOGIN_URL,
            wait_until="domcontentloaded",
            timeout=self.timeout,
        )
        self.page.locator('input[type="text"]').first.fill(username)
        self.page.locator('input[type="password"]').fill(password)
        self.page.locator("button.el-button--primary").click()
        validation = self.page.locator(".el-form-item__error").filter(
            has_text=message
        ).last
        expect(validation).to_be_visible(timeout=5000)
        expect(self.page).to_have_url(re.compile(r"/login(?:\?.*)?/?$"))
