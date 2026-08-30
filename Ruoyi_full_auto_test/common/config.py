import os

# Frontend addresses used by Playwright UI tests.
FRONTEND_BASE_URL = os.getenv("RUOYI_FRONTEND_BASE_URL", "http://localhost:82")
FRONTEND_LOGIN_URL = f"{FRONTEND_BASE_URL}/login"
FRONTEND_INDEX_URL = f"{FRONTEND_BASE_URL}/index"

# Backend API address. 8080 is Jenkins in this environment; RuoYi API listens on 8081.
API_BASE_URL = os.getenv("RUOYI_API_BASE_URL", "http://localhost:8081").rstrip("/")
API_USERNAME = os.getenv("RUOYI_API_USERNAME", "admin")
API_PASSWORD = os.getenv("RUOYI_API_PASSWORD", "admin123")
API_TIMEOUT = int(os.getenv("RUOYI_API_TIMEOUT", "10"))

# Kept for backward compatibility with older scripts. New API code should use API_BASE_URL.
BASE_URL = API_BASE_URL

# MySQL connection settings for optional database checks.
MYSQL_CFG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "你的mysql密码",
    "database": "ry_vue",
    "charset": "utf8mb4",
}

# Static data kept for legacy examples. UI tests should generate unique data instead.
TEST_USER = {
    "username": "test_auto001",
    "password": "123456",
    "phonenumber": "13800138000",
}