"""
后台管理系统登录和 Token 鉴权接口测试。
测试范围：
1. 正确账号密码登录；
2. 错误密码登录；
3. 用户名为空；
4. 密码为空；
5. 不携带 Token 访问需要登录的接口；
6. 携带无效 Token 访问需要登录的接口；
7. 携带有效 Token 访问需要登录的接口。
后台接口地址：
http://localhost:8082
"""
# 导入路径处理模块，用来获取项目文件绝对路径
from pathlib import Path
# 类型注解，Any任意类型，Dict字典类型，方便代码阅读
from typing import Any, Dict
# allure装饰器，用于生成allure测试报告，标记模块、用例标题等
import allure
# pytest测试框架，用来执行测试用例
import pytest
# yaml库，读取yaml格式配置文件
import yaml
# 导入自定义封装的http请求客户端，统一处理http请求
from common.http_client import HttpClient

# 获取当前脚本上级目录，定位到api项目根目录
# D:\ecommerce-test\automation\api
API_ROOT = Path(__file__).resolve().parents[1]
# 拼接配置文件完整路径：config/config.yaml
CONFIG_FILE = API_ROOT / "config" / "config.yaml"

# 打开yaml配置文件，utf-8编码读取
with CONFIG_FILE.open("r", encoding="utf-8") as file:
    # 将yaml文件内容加载为python字典对象
    CONFIG = yaml.safe_load(file)

# 取出配置文件中admin后台相关配置（地址、账号密码）
ADMIN_CONFIG = CONFIG["admin"]
# 实例化http请求客户端，超时时间读取配置，默认15秒
client = HttpClient(timeout=CONFIG.get("timeout", 15))


def login_admin() -> Dict[str, Any]:
    """
    使用正确的后台账号登录，并返回完整响应数据。
    当前项目实际账号：
    username：admin
    password：macro123
    """
    # 发起POST登录请求
    response = client.request(
        method="POST",  # 请求方法POST
        url=f"{ADMIN_CONFIG['base_url']}/admin/login",  # 拼接登录接口地址
        headers={
            "Content-Type": "application/json",  # 请求体格式为json
        },
        json={  # POST请求json请求体，传入账号密码
            "username": ADMIN_CONFIG["username"],
            "password": ADMIN_CONFIG["password"],
        },
    )
    # 断言HTTP响应状态码200，代表服务正常返回
    assert response.status_code == 200
    # 调用封装方法，把响应内容转成字典
    body = client.json_body(response)
    # 断言业务码200，代表登录业务成功
    assert body.get("code") == 200
    # 断言返回data字段存在
    assert body.get("data")
    # 断言data里面包含token字段
    assert body["data"].get("token")
    # 返回完整响应字典，供其他用例获取token使用
    return body


@allure.feature("后台管理系统")  # allure大模块：后台管理系统
@allure.story("后台登录")        # allure子模块：后台登录功能
@allure.title("正确账号密码登录成功") # 测试用例标题，展示在报告
@pytest.mark.admin               # 自定义标记admin，执行时可筛选admin相关用例
@pytest.mark.auth                # 标记鉴权相关用例
@pytest.mark.smoke               # 冒烟测试标记，核心主流程用例
def test_admin_login_success():
    """验证后台使用正确账号密码可以登录。"""
    # 调用登录函数，拿到登录返回数据
    body = login_admin()
    # 提取token
    token = body["data"]["token"]
    # 提取token前缀 Bearer
    token_head = body["data"].get("tokenHead", "")
    # 断言token不为空
    assert token
    # 断言token前缀是Bearer
    assert token_head == "Bearer "


@allure.feature("后台管理系统")
@allure.story("后台登录")
@allure.title("错误密码登录失败")
@pytest.mark.admin
@pytest.mark.auth
def test_admin_login_wrong_password():
    """验证输入错误密码时登录失败。"""
    # POST请求登录接口，密码传错误值
    response = client.request(
        method="POST",
        url=f"{ADMIN_CONFIG['base_url']}/admin/login",
        headers={
            "Content-Type": "application/json",
        },
        json={
            "username": ADMIN_CONFIG["username"],
            "password": "wrong-password",
        },
    )
    # HTTP状态码仍然200，后端业务错误不返回4xx，统一200返回业务code
    assert response.status_code == 200
    body = client.json_body(response)
    # 业务码不等于200，代表登录业务失败
    assert body.get("code") != 200
    # 失败场景data为空
    assert body.get("data") is None
    # 校验返回提示消息message存在
    assert body.get("message")


@allure.feature("后台管理系统")
@allure.story("后台登录")
@allure.title("用户名为空时登录失败")
@pytest.mark.admin
@pytest.mark.auth
def test_admin_login_empty_username():
    """验证用户名为空时不能登录。"""
    response = client.request(
        method="POST",
        url=f"{ADMIN_CONFIG['base_url']}/admin/login",
        headers={
            "Content-Type": "application/json",
        },
        json={
            "username": "",  # 用户名为空字符串
            "password": ADMIN_CONFIG["password"],
        },
    )
    assert response.status_code == 200
    body = client.json_body(response)
    assert body.get("code") != 200
    assert body.get("data") is None
    assert body.get("message")


@allure.feature("后台管理系统")
@allure.story("后台登录")
@allure.title("密码为空时登录失败")
@pytest.mark.admin
@pytest.mark.auth
def test_admin_login_empty_password():
    """验证密码为空时不能登录。"""
    response = client.request(
        method="POST",
        url=f"{ADMIN_CONFIG['base_url']}/admin/login",
        headers={
            "Content-Type": "application/json",
        },
        json={
            "username": ADMIN_CONFIG["username"],
            "password": "", # 密码传空字符串
        },
    )
    assert response.status_code == 200
    body = client.json_body(response)
    assert body.get("code") != 200
    assert body.get("data") is None
    assert body.get("message")


@allure.feature("后台管理系统")
@allure.story("Token 鉴权")
@allure.title("不携带 Token 访问商品列表失败")
@pytest.mark.admin
@pytest.mark.auth
def test_product_list_without_token():
    """
    验证没有携带 Token 时不能访问商品列表接口。
    当前项目实际返回：
    HTTP 200
    body.code = 401
    """
    # GET请求商品列表接口，不传入Authorization头（不带token）
    response = client.request(
        method="GET",
        url=f"{ADMIN_CONFIG['base_url']}/product/list",
        params={ # url查询参数：页码、每页条数
            "pageNum": 1,
            "pageSize": 5,
        },
    )
    assert response.status_code == 200
    body = client.json_body(response)
    # 业务码401：未授权，缺少token
    assert body.get("code") == 401
    assert body.get("data") is not None
    # 返回消息中包含token关键词
    assert "token" in body.get("message", "").lower()


@allure.feature("后台管理系统")
@allure.story("Token 鉴权")
@allure.title("携带无效 Token 访问商品列表失败")
@pytest.mark.admin
@pytest.mark.auth
def test_product_list_with_invalid_token():
    """验证携带无效 Token 时不能访问商品列表接口。"""
    response = client.request(
        method="GET",
        url=f"{ADMIN_CONFIG['base_url']}/product/list",
        headers={
            "Authorization": "Bearer invalid-token", # 传入伪造无效token
        },
        params={
            "pageNum": 1,
            "pageSize": 5,
        },
    )
    assert response.status_code == 200
    body = client.json_body(response)
    assert body.get("code") == 401
    assert body.get("data") is not None
    assert "token" in body.get("message", "").lower()


@allure.feature("后台管理系统")
@allure.story("Token 鉴权")
@allure.title("携带有效 Token 访问商品列表成功")
@pytest.mark.admin
@pytest.mark.auth
@pytest.mark.smoke
def test_product_list_with_valid_token():
    """验证携带有效 Token 可以访问商品列表接口。"""
    # 调用登录方法获取登录结果，拿到真实token
    login_body = login_admin()
    token = login_body["data"]["token"]
    token_head = login_body["data"].get("tokenHead", "Bearer ")
    response = client.request(
        method="GET",
        url=f"{ADMIN_CONFIG['base_url']}/product/list",
        headers={
            "Authorization": f"{token_head}{token}", # 拼接Bearer+真实token
        },
        params={
            "pageNum": 1,
            "pageSize": 5,
        },
    )
    assert response.status_code == 200
    body = client.json_body(response)
    # 业务码200代表鉴权成功，拿到商品数据
    assert body.get("code") == 200
    assert body.get("data")
    # 校验返回列表list字段存在
    assert body["data"].get("list") is not None
    # 校验总条数total字段存在
    assert body["data"].get("total") is not None
