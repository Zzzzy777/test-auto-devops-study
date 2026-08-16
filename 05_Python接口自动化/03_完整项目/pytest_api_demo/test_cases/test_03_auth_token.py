import allure
import pytest


@allure.feature("Token 鉴权")
class TestAuthToken:
    @pytest.mark.auth
    @allure.story("fixture 复用 token")
    @allure.title("使用全局 token fixture 发送鉴权请求")
    def test_authorization_header(self, api_session, base_url, api_token):
        headers = {"Authorization": f"Bearer {api_token}"}

        resp = api_session.get(f"{base_url}/headers", headers=headers, timeout=5)
        result = resp.json()

        assert resp.status_code == 200
        assert result["headers"]["Authorization"] == f"Bearer {api_token}"

    @pytest.mark.auth
    @allure.story("token 非空校验")
    @allure.title("校验 fixture 返回的 token 非空")
    def test_token_not_empty(self, api_token):
        assert api_token
        assert api_token.startswith("mock-token")

