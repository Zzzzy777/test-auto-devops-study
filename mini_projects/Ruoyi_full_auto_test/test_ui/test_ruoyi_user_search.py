import allure

from common.logger import get_logger
from common.test_data import build_unique_user
from common.user_api import RuoYiUserApi


logger = get_logger(__name__)


@allure.feature("用户管理模块-UI")
@allure.story("用户搜索")
def test_ui_search_user(user_page):
    """Verify that a newly created user can be found by exact username."""
    user = build_unique_user()
    api = RuoYiUserApi()
    try:
        user_page.add_user(user)
        user_page.search_username(user.username)
        user_page.assert_user_visible(user.username)
        user_page.assert_user_row_contains(user.username, user.nickname, user.phone)
        logger.info("用户搜索和结果字段校验通过: %s", user.username)
    finally:
        api.cleanup_user_by_username(user.username)