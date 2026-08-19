import requests
import allure

@allure.feature("httpbin接口测试")
class TestHttpbinApi:

    @allure.story("get请求参数测试")
    @allure.title("测试get传参")
    def test_get_params(self):
        url = "https://httpbin.ceshiren.com/get"
        params = {
            "name":"demo",
            "age":"18"
        }
        resp = requests.get(url,params=params,timeout=10)
        # 先判断状态码！！
        assert resp.status_code == 200
        res = resp.json()
        assert res["args"]["name"] == "demo"


    @allure.story("post json请求测试")
    @allure.title("测试post‑json提交")
    def test_post_json(self):
        url = "https://httpbin.ceshiren.com/post"
        body = {
            "id":107,
            "title":"allure测试"
        }
        resp = requests.post(url,json=body,timeout=10)
        assert resp.status_code == 200
        res = resp.json()
        assert res["json"]["id"] == 107