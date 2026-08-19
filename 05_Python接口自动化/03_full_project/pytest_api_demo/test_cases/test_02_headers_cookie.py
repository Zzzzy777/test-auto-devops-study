import allure
import pytest


@allure.feature("请求头和 Cookie 校验")
class TestHeadersAndCookie:
    @pytest.mark.smoke
    @allure.story("请求头断言")
    @allure.title("校验自定义请求头是否被服务端接收")
    def test_custom_header(self, api_session, base_url):
        headers = {"X-Study-Source": "pytest-api-demo"}

        resp = api_session.get(f"{base_url}/headers", headers=headers, timeout=5)
        result = resp.json()

        assert resp.status_code == 200
        assert result["headers"]["X-Study-Source"] == "pytest-api-demo"

    @pytest.mark.smoke
    @allure.story("Cookie 断言")
    @allure.title("校验请求 Cookie 是否被服务端接收")
    def test_cookie_assert(self, api_session, base_url):
        cookies = {"session_id": "demo-session-001"}

        resp = api_session.get(f"{base_url}/cookies", cookies=cookies, timeout=5)
        result = resp.json()

        assert resp.status_code == 200
        assert result["cookies"]["session_id"] == "demo-session-001"

