from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

import allure
import pytest

from common.config import FRONTEND_LOGIN_URL, PROJECT_ROOT


FAIL_SCREENSHOT_DIR = PROJECT_ROOT / "reports" / "screenshots" / "fail"


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Expose phase reports to fixtures so failed UI tests can be captured."""
    outcome = yield
    report = outcome.get_result()
    setattr(item, "rep_" + report.when, report)


def _safe_filename(value: str) -> str:
    return re.sub(r"[^0-9A-Za-z._-]+", "_", value)


@pytest.fixture(scope="function")
def page(page, request):
    """Open the RuoYi login page and save a screenshot when the test fails."""
    page.goto(FRONTEND_LOGIN_URL, wait_until="domcontentloaded", timeout=15000)
    yield page

    try:
        if getattr(request.node, "rep_call", None) and request.node.rep_call.failed:
            FAIL_SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            filename = f"{_safe_filename(request.node.nodeid)}_{timestamp}.png"
            screenshot_path = FAIL_SCREENSHOT_DIR / filename
            try:
                page.screenshot(path=str(screenshot_path), full_page=True)
                allure.attach.file(
                    str(screenshot_path),
                    name="失败页面截图",
                    attachment_type=allure.attachment_type.PNG,
                )
            except Exception as screenshot_error:
                allure.attach(
                    str(screenshot_error),
                    name="失败截图保存异常",
                    attachment_type=allure.attachment_type.TEXT,
                )
    finally:
        page.close()