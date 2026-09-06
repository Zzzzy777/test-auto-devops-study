import allure
import requests
from config import BASE_URL

@allure.feature("权限校验模块")
class TestPermission:

    @allure.story("无token访问用户列表，校验鉴权拦截")
    def test_no_token_access_user_list(self):
        """反向用例：请求头不带token，访问需要鉴权的接口，应该返回未授权"""
        url = f"{BASE_URL}/system/user/list"
        # headers 故意不携带token
        print(f"\n【请求地址】:{url}")
        resp = requests.get(url=url, timeout=10)
        print(f"【响应状态码】:{resp.status_code}")
        print(f"【响应返回内容】:{resp.text}")

        assert resp.status_code == 200
        res = resp.json()
        # RuoYi无token返回code 401
        assert res["code"] == 401
