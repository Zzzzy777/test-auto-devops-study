import allure

from common.logger import get_logger
from common.test_data import build_unique_user
from common.user_api import RuoYiUserApi


logger = get_logger(__name__)


@allure.feature("用户管理模块-UI")
@allure.story("编辑用户")
def test_ui_edit_user(user_page):
    """Verify that nickname and phone can be edited and queried again."""
    user = build_unique_user()
    edited_nickname = f"编辑后_{user.username[-6:]}"
    edited_phone = "13812345678"
    api = RuoYiUserApi()

    try:
        user_page.add_user(user)
        user_page.edit_user(user.username, edited_nickname, edited_phone)
        user_page.search_username(user.username)
        user_page.assert_user_row_contains(
            user.username,
            edited_nickname,
            edited_phone,
        )
        logger.info("编辑用户校验通过: %s", user.username)
    finally:
        api.cleanup_user_by_username(user.username)