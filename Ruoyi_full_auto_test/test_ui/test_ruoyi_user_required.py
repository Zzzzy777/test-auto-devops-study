import allure

from common.logger import get_logger
from common.test_data import build_unique_user
from common.user_api import RuoYiUserApi


logger = get_logger(__name__)


@allure.feature("用户管理模块-UI")
@allure.story("新增用户必填校验")
def test_ui_add_user_required_validation(user_page):
    """Verify required validation for the add-user form."""
    user = build_unique_user()
    api = RuoYiUserApi()
    try:
        user_page.click_add()
        user_page.submit_add_form_expect_validation()
        logger.info("新增用户必填校验通过")
    finally:
        # The form should not create a user, but keep cleanup idempotent as a guard.
        api.cleanup_user_by_username(user.username)