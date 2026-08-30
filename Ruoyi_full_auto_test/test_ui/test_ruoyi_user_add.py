import json
import traceback

import allure
from playwright.sync_api import Page

from common.logger import get_logger
from common.test_data import build_unique_user
from common.user_api import RuoYiUserApi
from pages.login_page import LoginPage
from pages.user_page import UserPage


logger = get_logger(__name__)


@allure.feature("用户管理模块-UI")
@allure.story("新增用户正向用例")
@allure.description(
    "登录-进入用户管理-新增用户-提交-搜索校验-API清理测试数据"
)
def test_ui_add_user(page: Page):
    """Verify UI user creation and API cleanup in finally."""
    user = build_unique_user()
    api = RuoYiUserApi()
    test_error: BaseException | None = None
    logger.info("开始执行新增用户用例: %s", user.username)

    try:
        LoginPage(page).login()
        user_page = UserPage(page)
        user_page.open()
        user_page.add_user(user)
        user_page.search_username(user.username)
        user_page.assert_user_visible(user.username)

        allure.attach(
            json.dumps(user.to_dict(), ensure_ascii=False, indent=2),
            name="UI新增用户数据",
            attachment_type=allure.attachment_type.JSON,
        )
    except BaseException as exc:
        test_error = exc
        logger.exception("新增用户 UI 用例失败: %s", user.username)
        raise
    finally:
        try:
            cleanup_result = api.cleanup_user_by_username(user.username)
            logger.info("API清理完成: %s", cleanup_result)
            allure.attach(
                json.dumps(cleanup_result, ensure_ascii=False, indent=2),
                name="API清理结果",
                attachment_type=allure.attachment_type.JSON,
            )
        except Exception:
            logger.exception("API清理失败: %s", user.username)
            allure.attach(
                traceback.format_exc(),
                name="API清理异常",
                attachment_type=allure.attachment_type.TEXT,
            )
            # Preserve the original UI failure. If UI passed, expose cleanup failure.
            if test_error is None:
                raise