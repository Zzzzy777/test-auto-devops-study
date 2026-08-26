import pytest
from common_request import send_request
from config import BASE_URL

# @pytest.fixture(scope="session")
# def headers_with_token():
#     """
#     fixture夹具：获取带token的请求头
#     scope="session"：整个测试会话，**只执行一次登录**，所有用例共用这一个token，提升执行速度
#     """
#     #拼接登录接口完整url
#     login_url = f"{BASE_URL}/login"
#     # 登录接口请求体，json格式
#     login_data = {
#         "username": USERNAME,
#         "password": PASSWORD
#     }
#     # 发送post登录请求
#     resp = requests.post(url=login_url,json=login_data)

#     # 断言：http状态码200，代表网络层面请求成功
#     assert resp.status_code == 200

#     # 拿到接口返回json数据
#     res = resp.json()
#     # 若依业务码：code=200代表业务登录成功
#     assert res["code"] == 200

#     # 从返回结果取出token
#     token = res["token"]

#     # 组装鉴权请求头，若依要求 Authorization: Bearer token值
#     headers = {
#         "Authorization": f"Bearer {token}",
#         "Content-Type": "application/json"
#     }

#     #yield：把headers返回给测试用例使用
#     yield headers
#     # yield后面可以写后置清理代码，这里不需要，留空

# =====新增：数据清理夹具====
@pytest.fixture
def clean_test_user(scope="function"):
    """自动清理测试账号 testauto01"""
    # 前置清理
    query_url = f"{BASE_URL}/system/user/list"
    resp_before = send_request("GET", query_url, params={"userName": "testauto01"})
    res_before = resp_before.json()
    if len(res_before["rows"]) > 0:
        user_id = res_before["rows"][0]["userId"]
        send_request("DELETE", f"{BASE_URL}/system/user/{user_id}")

    yield

    # 后置清理，无论用例成败都会执行
    resp_after = send_request("GET", query_url, params={"userName": "testauto01"})
    res_after = resp_after.json()
    if len(res_after["rows"]) > 0:
        user_id = res_after["rows"][0]["userId"]
        send_request("DELETE", f"{BASE_URL}/system/user/{user_id}")

