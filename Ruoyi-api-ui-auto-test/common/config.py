"""
项目统一配置模块。

所有 API、UI、数据库和报告路径配置都从这里读取。
优先读取系统环境变量；如果没有配置，则使用默认值。
"""

from __future__ import annotations

import os
from pathlib import Path


# =========================
# 项目路径配置
# =========================

# common/config.py 的上两级目录就是项目根目录
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# 测试报告根目录
REPORT_ROOT = Path(
    os.getenv(
        "RUOYI_REPORT_ROOT",
        str(PROJECT_ROOT / "reports"),
    )
)

# 日志目录
LOG_DIR = Path(
    os.getenv(
        "RUOYI_LOG_DIR",
        str(REPORT_ROOT / "logs"),
    )
)

# UI 失败截图目录
FAIL_SCREENSHOT_DIR = (
    REPORT_ROOT / "screenshots" / "fail"
)

# Allure 原始结果目录
ALLURE_RESULTS_DIR = (
    REPORT_ROOT / "allure-results"
)


# =========================
# UI 自动化配置
# =========================

# RuoYi 前端地址
FRONTEND_BASE_URL = os.getenv(
    "RUOYI_FRONTEND_BASE_URL",
    "http://localhost:82",
).rstrip("/")

# 登录页面地址
FRONTEND_LOGIN_URL = (
    f"{FRONTEND_BASE_URL}/login"
)

# 首页地址
FRONTEND_INDEX_URL = (
    f"{FRONTEND_BASE_URL}/index"
)

# UI 登录账号
UI_USERNAME = os.getenv(
    "RUOYI_UI_USERNAME",
    "admin",
)

# UI 登录密码
UI_PASSWORD = os.getenv(
    "RUOYI_UI_PASSWORD",
    "admin123",
)

# Playwright 操作超时时间，单位毫秒
UI_TIMEOUT = int(
    os.getenv(
        "RUOYI_UI_TIMEOUT",
        "15000",
    )
)


# =========================
# API 自动化配置
# =========================

# RuoYi 后端 API 地址
API_BASE_URL = os.getenv(
    "RUOYI_API_BASE_URL",
    "http://localhost:8081",
).rstrip("/")

# 兼容旧代码中的 BASE_URL
BASE_URL = API_BASE_URL

# API 登录账号
API_USERNAME = os.getenv(
    "RUOYI_API_USERNAME",
    "admin",
)

# API 登录密码
API_PASSWORD = os.getenv(
    "RUOYI_API_PASSWORD",
    "admin123",
)

# API 请求超时时间，单位秒
API_TIMEOUT = int(
    os.getenv(
        "RUOYI_API_TIMEOUT",
        "10",
    )
)

# ?????????????? ID???????????
DEFAULT_DEPT_ID = int(os.getenv("RUOYI_DEFAULT_DEPT_ID", "105"))


# =========================
# MySQL 数据库配置
# =========================

MYSQL_CFG = {
    "host": os.getenv(
        "MYSQL_HOST",
        "127.0.0.1",
    ),
    "port": int(
        os.getenv(
            "MYSQL_PORT",
            "3306",
        )
    ),
    "user": os.getenv(
        "MYSQL_USER",
        "root",
    ),
    "password": os.getenv(
        "MYSQL_PASSWORD",
        "",
    ),
    "database": os.getenv(
        "MYSQL_DATABASE",
        "ry_vue",
    ),
    "charset": os.getenv(
        "MYSQL_CHARSET",
        "utf8mb4",
    ),
}


# =========================
# 兼容旧测试数据
# =========================

TEST_USER = {
    "username": "test_auto001",
    "password": "123456",
    "phonenumber": "13800138000",
}