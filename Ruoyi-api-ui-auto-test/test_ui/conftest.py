"""
UI 自动化测试专用 Fixture。
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page

from pages.login_page import LoginPage
from pages.user_page import UserPage


@pytest.fixture
def user_page(page: Page) -> UserPage:
    """
    登录后打开用户管理页面，
    向 UI 测试用例返回 UserPage 页面对象。
    """
    LoginPage(page).login()

    users = UserPage(page)
    users.open()

    return users