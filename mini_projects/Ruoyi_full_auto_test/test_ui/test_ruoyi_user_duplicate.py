import allure

from common.logger import get_logger
from common.test_data import UserData, build_unique_user
from common.user_api import RuoYiUserApi


logger = get_logger(__name__)


@allure.feature("用户管理模块-UI")
@allure.story("重复用户名校验")
def test_ui_add_user_duplicate_username(user_page):
    """Verify that the UI rejects a duplicate login name."""
    user = build_unique_user()
    duplicate_data = build_unique_user()
    duplicate_data = UserData(
        username=user.username,
        nickname=duplicate_data.nickname,
        password=duplicate_data.password,
        phone=duplicate_data.phone,
    )
    api = RuoYiUserApi()

    try:
        user_page.add_user(user)
        user_page.click_add()
        user_page.fill_add_form(duplicate_data)
        user_page.submit_add_form_expect_error("登录账号已存在")
        logger.info("重复用户名校验通过: %s", user.username)
    finally:
        api.cleanup_user_by_username(user.username)