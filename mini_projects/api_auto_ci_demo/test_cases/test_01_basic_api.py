import allure
import pytest


@allure.feature("基础接口请求")
class TestBasicApi:
    @pytest.mark.smoke
    @allure.story("GET 请求")
    @allure.title("GET 请求携带 params 参数")
    def test_get_with_params(self, api_session, base_url):
        params = {"username": "admin", "page": "1"}

        resp = api_session.get(f"{base_url}/get", params=params, timeout=5)
        result = resp.json()

        assert resp.status_code == 200
        assert result["args"]["username"] == "admin"
        assert result["args"]["page"] == "1"

    @pytest.mark.smoke
    @allure.story("POST 表单")
    @allure.title("POST 表单 data 提交")
    def test_post_form_data(self, api_session, base_url):
        data = {"username": "admin", "password": "123456"}

        resp = api_session.post(f"{base_url}/post", data=data, timeout=5)
        result = resp.json()

        assert resp.status_code == 200
        assert result["form"]["username"] == "admin"
        assert result["form"]["password"] == "123456"

    @pytest.mark.smoke
    @allure.story("POST JSON")
    @allure.title("POST JSON 请求体提交")
    def test_post_json_body(self, api_session, base_url):
        json_data = {"mobile": "13800000000", "code": "8888"}

        resp = api_session.post(f"{base_url}/post", json=json_data, timeout=5)
        result = resp.json()

        assert resp.status_code == 200
        assert result["json"]["mobile"] == "13800000000"
        assert result["json"]["code"] == "8888"

