import allure
from playwright.sync_api import Page

from common.logger import get_logger
from pages.login_page import LoginPage


logger = get_logger(__name__)


@allure.feature("UI登录模块")
@allure.story("管理员正常登录")
def test_login(page: Page):
    """Verify that the administrator can log in normally."""
    logger.info("开始执行登录用例")
    login_page = LoginPage(page)
    login_page.login()
    login_page.assert_login_success()