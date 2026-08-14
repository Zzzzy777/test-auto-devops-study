import pytest
import requests

# module：整个py文件夹具只执行1次
@pytest.fixture(scope="module")
def get_token():
    # ========== 前置：用例执行之前运行 ==========
    print("\n===== 【前置】执行登录，获取token =====")
    login_url = "https://httpbin.ceshiren.com/post"
    login_data = {
        "userid":"007",
        "password":"123456"
    }
    resp = requests.post(login_url, json=login_data, timeout=10)

    # 模拟token；真实项目这里写 resp.json()["data"]["token"]
    token = "mock_abc123456_token"
    print(f"拿到token：{token}")

    yield token   # 把token传给测试用例

    # ========== 后置：全部用例跑完之后才运行 ==========
    print("\n===== 【后置】全部用例结束，执行清理 =====")


# 用例1：参数写夹具名字 get_token，自动拿到token
def test_user_info(get_token):
    token = get_token
    headers = {"Authorization": f"Bearer {token}"}
    url = "https://httpbin.ceshiren.com/get"
    resp = requests.get(url, headers=headers, timeout=10)
    assert resp.status_code == 200


# 用例2：复用同一个token，不会再次登录
def test_user_list(get_token):
    token = get_token
    headers = {"Authorization": f"Bearer {token}"}
    url = "https://httpbin.ceshiren.com/get"
    resp = requests.get(url, headers=headers, timeout=10)
    assert resp.status_code == 200