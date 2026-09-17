"""
项目2基础健康检查。

这一组测试用于确认：
1. mall-admin 后端可以访问；
2. mall-portal 后端可以访问；
3. pytest 和 requests 框架配置正确。
"""

import pytest

from common.http_client import HttpClient


client = HttpClient()


@pytest.mark.smoke
def test_admin_health():
    """验证后台管理服务健康状态。"""

    response = client.request(
        "GET",
        "http://localhost:8082/actuator/health",
    )

    assert response.status_code == 200

    body = client.json_body(response)

    assert body.get("status") == "UP"


@pytest.mark.smoke
def test_portal_health():
    """验证商城前台服务健康状态。"""

    response = client.request(
        "GET",
        "http://localhost:8085/actuator/health",
    )

    assert response.status_code == 200

    body = client.json_body(response)

    assert body.get("status") == "UP"