import requests
import allure
from config import BASE_URL

@allure.feature("登录鉴权模块")  # allure报告大模块标签
#创建测试类
class Testlogin:

    @allure.story("正常登录-账号密码正确") # 报告里面小场景标签
    def test_login_successful(self):
        """正向用例：账号密码正确，成功拿到token"""
        #拼接登录接口地址
        url = f"{BASE_URL}/login"
        #请求体
        data = {
            "username": "admin",
            "password": "admin123"
        }
        #post发送登录请求
        resp = requests.post(url=url,json=data,timeout=10)

        #http状态码断言：网络请求成功
        assert resp.status_code == 200
        # 获取返回json
        res = resp.json()
        # 业务状态码200代表登录业务成功
        assert res["code"] == 200
        # 判断返回结果里面存在token字段
        assert "token" in res


    @allure.story("登录失败-密码错误")
    def test_login_wrong_pwd(self):
        """反向用例：密码错误，登录失败"""
        url = f"{BASE_URL}/login"
        # 错误密码
        data = {
            "username":"admin",
            "password":"wrong123"
            }
        resp = requests.post(url,json=data,timeout=10)

        #http状态码断言：网络请求成功
        assert resp.status_code == 200
        # 获取返回json
        res = resp.json()
        #业务码不等于200，代表登录业务失败
        assert res["code"] != 200