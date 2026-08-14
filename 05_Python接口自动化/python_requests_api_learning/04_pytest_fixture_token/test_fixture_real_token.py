import pytest
import requests

@pytest.fixture(scope="module")
def get_token():
    print("\n===== 执行登录，获取token【前置操作】 =====")
    # 真实业务登录接口地址
    login_url = "http://xxx/api/login"
    login_data = {
        "username": "admin",
        "password": "123456"
    }
    # 发送登录post请求
    resp = requests.post(login_url, json=login_data, timeout=10)

    # ==========这里是和练习代码最大区别==========
    # 解析接口返回json，取出token字段
    res_json = resp.json()
    # 真实后端返回 { "code":200, "data":{"token":"xxxxxx"} } 看后端返回结构
    token = res_json["data"]["token"]
    # 有的接口直接返回 {"token":"xxx"} → token = res_json["token"]
    # ===========================================

    print(f"登录成功，获取真实token：{token}")

    yield token   # 把真实token交给各个测试用例

    # 后置：全部用例跑完，执行退出登录
    print("\n===== 全部用例执行完毕，后置清理：调用退出登录接口 =====")
    logout_url = "http://xxx/api/logout"
    requests.post(logout_url, headers={"Authorization": f"Bearer {token}"})


# 业务用例，自动拿到登录返回的真实token
def test_user_info(get_token):
    token = get_token
    headers = {"Authorization": f"Bearer {token}"}
    url = "http://xxx/api/user/info"
    resp = requests.get(url, headers=headers, timeout=10)
    assert resp.status_code == 200