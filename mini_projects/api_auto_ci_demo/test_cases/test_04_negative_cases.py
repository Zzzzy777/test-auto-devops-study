import allure
import pytest
import requests


@allure.feature("异常场景")
class TestNegativeCases:
    @pytest.mark.negative
    @allure.story("错误状态码")
    @allure.title("请求不存在资源返回 404")
    def test_status_404(self, api_session, base_url):
        resp = api_session.get(f"{base_url}/status/404", timeout=5)

        assert resp.status_code == 404

    @pytest.mark.negative
    @allure.story("鉴权缺失")
    @allure.title("本地校验未传 Authorization 请求头")
    def test_missing_authorization_header(self):
        headers = {}

        assert "Authorization" not in headers

    @pytest.mark.negative
    @allure.story("超时异常")
    @allure.title("请求超时时能捕获 Timeout 异常")
    def test_timeout_exception(self, api_session, base_url):
        with pytest.raises(requests.exceptions.Timeout):
            api_session.get(f"{base_url}/delay/3", timeout=0.001)

