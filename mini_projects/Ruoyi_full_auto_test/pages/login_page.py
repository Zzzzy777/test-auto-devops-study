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