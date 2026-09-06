from __future__ import annotations

from playwright.sync_api import Locator, Page, expect

from common.config import UI_TIMEOUT
from common.logger import get_logger
from common.test_data import UserData


class UserPage:
    """Page Object for RuoYi system user management."""

    def __init__(self, page: Page, timeout: int = UI_TIMEOUT) -> None:
        self.page = page
        self.timeout = timeout
        self.logger = get_logger(self.__class__.__name__)

    @property
    def table(self) -> Locator:
        return self.page.locator(".el-table")

    @property
    def add_dialog(self) -> Locator:
        return self.page.locator(".el-dialog:visible").filter(
            has_text="添加用户"
        ).first

    @property
    def edit_dialog(self) -> Locator:
        return self.page.locator(".el-dialog:visible").filter(
            has_text="修改用户"
        ).first

    @property
    def dialog(self) -> Locator:
        """Backward-compatible alias for the add-user dialog."""
        return self.add_dialog

    def open(self) -> None:
        self.logger.info("进入系统管理-用户管理")
        self.page.get_by_text("系统管理", exact=True).click()
        self.page.get_by_text("用户管理", exact=True).click()
        self.page.wait_for_url("**/system/user", timeout=self.timeout)
        self.table.wait_for(state="visible", timeout=12000)
        self.logger.info("用户管理页面打开成功")

    def click_add(self) -> None:
        self.logger.info("点击新增用户")
        add_button = self.page.locator("button.el-button--primary").filter(
            has_text="新增"
        ).first
        expect(add_button).to_be_visible(timeout=10000)
        add_button.click()
        expect(self.add_dialog).to_be_visible(timeout=12000)

    def _field_by_label(self, label_text: str, dialog: Locator | None = None) -> Locator:
        target_dialog = dialog or self.add_dialog
        return target_dialog.locator(
            f'label:has-text("{label_text}")'
        ).locator("xpath=following-sibling::div[1]//input")

    def fill_add_form(self, user: UserData) -> None:
        self.logger.info("填写新增用户表单: %s", user.username)
        self._field_by_label("用户昵称").fill(user.nickname)
        self._field_by_label("用户名称").fill(user.username)
        self._field_by_label("用户密码").fill(user.password)
        self._field_by_label("手机号码").fill(user.phone)
        self._select_first_department(self.add_dialog)

    def _select_first_department(self, dialog: Locator) -> None:
        # The department field uses vue-treeselect rather than a normal el-tree.
        self._field_by_label("归属部门", dialog).click()
        department_option = self.page.locator(
            ".vue-treeselect__menu:visible .vue-treeselect__option"
        ).first
        expect(department_option).to_be_visible(timeout=8000)
        department_option.click(force=True)
        expect(self.page.locator(".vue-treeselect__menu:visible")).to_have_count(
            0, timeout=5000
        )

    def _expect_success_message(self, text: str) -> None:
        message = self.page.locator(".el-message.el-message--success").filter(
            has_text=text
        ).last
        expect(message).to_be_visible(timeout=10000)

    def submit_add_form(self) -> None:
        self.logger.info("提交新增用户表单")
        confirm_button = self.add_dialog.locator("button.el-button--primary").first
        expect(confirm_button).to_be_visible(timeout=10000)
        confirm_button.click(force=True)
        # A successful request closes the dialog. This prevents an old success
        # toast from making a duplicate-user test look successful.
        expect(self.add_dialog).to_be_hidden(timeout=10000)
        self._expect_success_message("新增成功")
        self.logger.info("新增用户成功提示已出现")

    def submit_add_form_expect_validation(self) -> None:
        self.logger.info("提交空白新增用户表单，校验必填提示")
        confirm_button = self.add_dialog.locator("button.el-button--primary").first
        expect(confirm_button).to_be_visible(timeout=10000)
        confirm_button.click(force=True)
        expect(self.add_dialog).to_be_visible(timeout=5000)
        errors = self.add_dialog.locator(".el-form-item__error")
        expect(errors).to_have_count(2, timeout=5000)
        expect(self.add_dialog).to_contain_text("用户昵称不能为空")
        expect(self.add_dialog).to_contain_text("用户名称不能为空")

    def submit_add_form_expect_error(self, message: str) -> None:
        self.logger.info("提交新增用户表单，校验业务错误: %s", message)
        confirm_button = self.add_dialog.locator("button.el-button--primary").first
        expect(confirm_button).to_be_visible(timeout=10000)
        confirm_button.click(force=True)
        expect(self.add_dialog).to_be_visible(timeout=10000)
        error_message = self.page.locator(".el-message.el-message--error").filter(
            has_text=message
        ).last
        expect(error_message).to_be_visible(timeout=10000)

    def add_user(self, user: UserData) -> None:
        self.click_add()
        self.fill_add_form(user)
        self.submit_add_form()

    def search_username(self, username: str) -> None:
        self.logger.info("按用户名搜索: %s", username)
        refresh_button = self.page.locator("button:has(i.el-icon-refresh)").first
        expect(refresh_button).to_be_visible(timeout=10000)
        refresh_button.click()

        username_input = self.page.locator("input.el-input__inner").nth(1)
        expect(username_input).to_be_visible(timeout=10000)
        username_input.fill(username)
        self.page.locator("button.el-button--primary.el-button--mini").first.click()

    def user_row(self, username: str) -> Locator:
        row = self.page.locator(".el-table__body-wrapper tbody tr").filter(
            has_text=username
        ).first
        expect(row).to_be_visible(timeout=self.timeout)
        return row

    def assert_user_visible(self, username: str) -> None:
        expect(self.table).to_contain_text(username, timeout=self.timeout)
        self.logger.info("用户搜索断言通过: %s", username)

    def assert_user_row_contains(
        self,
        username: str,
        *expected_texts: str,
    ) -> None:
        row = self.user_row(username)
        for expected_text in expected_texts:
            expect(row).to_contain_text(expected_text)
        self.logger.info("用户行字段断言通过: %s", username)

    def click_edit_for_user(self, username: str) -> None:
        self.logger.info("打开用户编辑弹窗: %s", username)
        row = self.user_row(username)
        row.locator("button").first.click()
        expect(self.edit_dialog).to_be_visible(timeout=10000)

    def fill_edit_form(self, nickname: str, phone: str) -> None:
        self.logger.info("填写编辑用户表单")
        self._field_by_label("用户昵称", self.edit_dialog).fill(nickname)
        self._field_by_label("手机号码", self.edit_dialog).fill(phone)

    def submit_edit_form(self) -> None:
        self.logger.info("提交编辑用户表单")
        confirm_button = self.edit_dialog.locator("button.el-button--primary").first
        expect(confirm_button).to_be_visible(timeout=10000)
        confirm_button.click(force=True)
        expect(self.edit_dialog).to_be_hidden(timeout=10000)
        self._expect_success_message("修改成功")
        self.logger.info("编辑用户成功")

    def edit_user(self, username: str, nickname: str, phone: str) -> None:
        self.search_username(username)
        self.click_edit_for_user(username)
        self.fill_edit_form(nickname, phone)
        self.submit_edit_form()