import json
import traceback
import uuid

import allure
from playwright.sync_api import Page, expect

from common.user_api import RuoYiUserApi


BASE_URL = "http://localhost:82"


@allure.feature("用户管理模块-UI")
@allure.story("新增用户正向用例")
@allure.description(
    "登录-进入用户管理-新增用户-提交-搜索校验-API清理测试数据"
)
def test_ui_add_user(page: Page):
    """验证管理员可以通过 UI 新增用户，并在 finally 中用 API 清理数据。"""
    username = f"ui_test_{uuid.uuid4().hex[:8]}"
    nickname = f"UI自动化_{uuid.uuid4().hex[:6]}"
    phone = f"139{uuid.uuid4().int % 100_000_000:08d}"
    api = RuoYiUserApi()
    test_error: BaseException | None = None

    try:
        # ---------------------- 登录 ----------------------
        page.goto(f"{BASE_URL}/login", wait_until="domcontentloaded", timeout=15000)
        page.locator('input[type="text"]').first.fill("admin")
        page.locator('input[type="password"]').fill("admin123")
        page.locator("button.el-button--primary").click()
        page.wait_for_url("**/index", timeout=15000)

        # ---------------------- 打开用户管理菜单 ----------------------
        page.get_by_text("系统管理", exact=True).click()
        page.get_by_text("用户管理", exact=True).click()
        page.wait_for_url("**/system/user", timeout=15000)
        page.locator(".el-table").wait_for(state="visible", timeout=12000)

        # ---------------------- 点击新增，弹出弹窗 ----------------------
        add_button = page.locator("button.el-button--primary").filter(
            has_text="新增"
        ).first
        expect(add_button).to_be_visible(timeout=10000)
        add_button.click()

        dialog = page.locator(".el-dialog:visible").filter(
            has_text="添加用户"
        ).first
        expect(dialog).to_be_visible(timeout=12000)

        # ---------------------- 填写表单 ----------------------
        def field_by_label(label_text: str):
            return dialog.locator(
                f'label:has-text("{label_text}")'
            ).locator("xpath=following-sibling::div[1]//input")

        field_by_label("用户昵称").fill(nickname)
        field_by_label("用户名").fill(username)
        field_by_label("用户密码").fill("123456")
        field_by_label("手机号码").fill(phone)

        # 选择归属部门：弹窗使用 vue-treeselect。
        department_input = field_by_label("归属部门")
        department_input.click()
        department_option = page.locator(
            ".vue-treeselect__menu:visible .vue-treeselect__option"
        ).first
        expect(department_option).to_be_visible(timeout=8000)
        department_option.click(force=True)
        expect(page.locator(".vue-treeselect__menu:visible")).to_have_count(
            0, timeout=5000
        )

        # ---------------------- 提交 ----------------------
        confirm_button = dialog.locator("button.el-button--primary").first
        expect(confirm_button).to_be_visible(timeout=10000)
        confirm_button.click(force=True)

        success_message = page.locator(".el-message.el-message--success")
        expect(success_message).to_be_visible(timeout=10000)

        # ---------------------- 查询并校验 ----------------------
        refresh_button = page.locator("button:has(i.el-icon-refresh)").first
        expect(refresh_button).to_be_visible(timeout=10000)
        refresh_button.click()

        username_input = page.locator("input.el-input__inner").nth(1)
        expect(username_input).to_be_visible(timeout=10000)
        username_input.fill(username)
        page.locator("button.el-button--primary.el-button--mini").first.click()
        expect(page.locator(".el-table")).to_contain_text(username, timeout=15000)

        allure.attach(
            json.dumps(
                {"username": username, "nickname": nickname, "phone": phone},
                ensure_ascii=False,
                indent=2,
            ),
            name="UI新增用户数据",
            attachment_type=allure.attachment_type.JSON,
        )
    except BaseException as exc:
        test_error = exc
        raise
    finally:
        try:
            cleanup_result = api.cleanup_user_by_username(username)
            allure.attach(
                json.dumps(cleanup_result, ensure_ascii=False, indent=2),
                name="API清理结果",
                attachment_type=allure.attachment_type.JSON,
            )
        except Exception as cleanup_error:
            allure.attach(
                traceback.format_exc(),
                name="API清理异常",
                attachment_type=allure.attachment_type.TEXT,
            )
            # If UI already failed, preserve the original failure as the primary error.
            if test_error is None:
                raise