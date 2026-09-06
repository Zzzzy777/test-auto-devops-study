"""
Pytest 全局配置。

这里不重新定义 page Fixture，
直接使用 pytest-playwright 提供的 page Fixture。

这样可以避免：

    def page(page, request)

这种同名 Fixture 递归问题。
"""

from __future__ import annotations

import re
from datetime import datetime

import allure
import pytest

from common.config import FAIL_SCREENSHOT_DIR


def _safe_filename(value: str) -> str:
    """
    将测试节点名称转换为安全文件名。
    """
    return re.sub(
        r"[^0-9A-Za-z._-]+",
        "_",
        value,
    )


@pytest.hookimpl(
    tryfirst=True,
    hookwrapper=True,
)
def pytest_runtest_makereport(item, call):
    """
    测试失败时自动保存 Playwright 页面截图。

    这里不创建 page Fixture，
    而是从当前测试的 funcargs 中获取
    pytest-playwright 提供的 page 对象。
    """
    outcome = yield
    report = outcome.get_result()

    # 只在测试主体阶段失败时截图
    if report.when != "call" or not report.failed:
        return

    page = item.funcargs.get("page")

    # API 测试没有 page 参数，直接跳过
    if page is None:
        return

    try:
        FAIL_SCREENSHOT_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S_%f"
        )

        filename = (
            f"{_safe_filename(item.nodeid)}_"
            f"{timestamp}.png"
        )

        screenshot_path = (
            FAIL_SCREENSHOT_DIR / filename
        )

        page.screenshot(
            path=str(screenshot_path),
            full_page=True,
        )

        allure.attach.file(
            str(screenshot_path),
            name="失败页面截图",
            attachment_type=allure.attachment_type.PNG,
        )

    except Exception as exc:
        # 截图失败不能覆盖原始测试失败
        allure.attach(
            str(exc),
            name="失败截图保存异常",
            attachment_type=allure.attachment_type.TEXT,
        )