"""
权限校验接口测试。

注意：

权限测试不能使用已经登录的 user_api，
否则请求会自动携带 Token，测试就失去意义。

因此这里使用 auth=False 的原始 HTTP 请求。
"""

import allure
import pytest

from common.config import API_BASE_URL
from common.http_client import RuoYiHttpClient


@pytest.mark.api
@allure.feature("权限校验模块")
class TestPermissionApi:
    """权限校验测试类。"""

    @allure.story("无 Token 访问受保护接口")
    def test_no_token_access_user_list(self) -> None:
        """
        不携带 Authorization 请求头，
        访问需要登录的用户列表接口。
        """
        client = RuoYiHttpClient(
            base_url=API_BASE_URL
        )

        response = client.request_raw(
            "GET",
            "/system/user/list",
            auth=False,
        )

        data = response.json()

        assert response.status_code == 200
        assert data["code"] == 401

    @allure.story("错误 Token 访问受保护接口")
    def test_invalid_token_access_user_list(self) -> None:
        """
        携带错误 Token 访问接口，
        应返回未授权结果。
        """
        client = RuoYiHttpClient(
            base_url=API_BASE_URL
        )

        response = client.request_raw(
            "GET",
            "/system/user/list",
            auth=False,
            headers={
                "Authorization": "Bearer invalid-token",
            },
        )

        data = response.json()

        assert response.status_code == 200
        assert data["code"] == 401