"""
商城前台用户登录和购物车鉴权接口测试。
商城前台接口地址：
http://localhost:8085
测试账号：
用户名：test
密码：123456
"""
# 导入路径工具类，用于获取项目文件绝对路径
from pathlib import Path
# 类型注解，标记任意类型和字典类型，提升代码可读性
from typing import Any, Dict
# allure装饰器，用于生成可视化测试报告，标记模块、用例标题
import allure
# pytest自动化测试框架，用来执行测试用例
import pytest
# yaml库，用于读取yaml格式的配置文件
import yaml
# 导入自己封装的HTTP请求客户端，统一管理接口请求
from common.http_client import HttpClient

# 获取当前脚本所在目录的上级目录，作为API自动化项目根目录
# D:\ecommerce-test\automation\api
API_ROOT = Path(__file__).resolve().parents[1]
# 拼接配置文件config.yaml的完整路径
CONFIG_FILE = API_ROOT / "config" / "config.yaml"

# 以utf-8编码打开yaml配置文件
with CONFIG_FILE.open("r", encoding="utf-8") as file:
    # 将yaml文件内容加载为Python字典对象
    CONFIG = yaml.safe_load(file)

# 取出配置文件里商城前台portal模块的配置信息（地址、账号密码）
PORTAL_CONFIG = CONFIG["portal"]
# 实例化HTTP请求客户端，超时时间读取配置，默认15秒
client = HttpClient(timeout=CONFIG.get("timeout", 15))


def login_portal() -> Dict[str, Any]:
    """
    使用正确的商城账号登录。
    当前项目实际账号：
    test / 123456
    """
    # 发起POST登录请求
    response = client.request(
        method="POST",
        url=f"{PORTAL_CONFIG['base_url']}/sso/login", # 拼接前台单点登录接口地址
        headers={
            "Content-Type": "application/x-www-form-urlencoded", # 请求体为表单格式
        },
        data={ # 表单传参，传入用户名和密码
            "username": PORTAL_CONFIG["username"],
            "password": PORTAL_CONFIG["password"],
        },
    )
    # 断言HTTP状态码200，代表服务正常响应
    assert response.status_code == 200
    # 调用封装方法，把接口返回内容转为字典
    body = client.json_body(response)
    # 断言业务码200，代表登录业务成功
    assert body.get("code") == 200
    # 断言返回data字段存在
    assert body.get("data")
    # 断言data中包含token字段
    assert body["data"].get("token")
    # 返回登录完整响应数据，供其他用例获取token使用
    return body


@allure.feature("商城前台")          # allure报告大模块：商城前台
@allure.story("会员登录")            # allure报告子模块：会员登录功能
@allure.title("商城用户正确账号密码登录成功") # 测试用例标题，展示在allure报告
@pytest.mark.portal                  # 自定义标记portal，执行时可只筛选前台用例
@pytest.mark.auth                    # 标记鉴权相关用例
@pytest.mark.smoke                   # 冒烟用例标记，核心主流程
def test_portal_login_success():
    """验证商城用户使用正确账号密码可以登录。"""
    # 调用前台登录函数，获取登录返回数据
    body = login_portal()
    # 断言token存在
    assert body["data"].get("token")
    # 断言token前缀为Bearer
    assert body["data"].get("tokenHead") == "Bearer "


@allure.feature("商城前台")
@allure.story("会员登录")
@allure.title("商城用户错误密码登录失败")
@pytest.mark.portal
@pytest.mark.auth
def test_portal_login_wrong_password():
    """验证商城用户使用错误密码不能登录。"""
    # POST请求前台登录接口，密码传入错误值
    response = client.request(
        method="POST",
        url=f"{PORTAL_CONFIG['base_url']}/sso/login",
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data={
            "username": PORTAL_CONFIG["username"],
            "password": "wrong-password",
        },
    )
    # HTTP状态码200，后端业务失败不返回4xx，依靠业务code判断结果
    assert response.status_code == 200
    body = client.json_body(response)
    # 当前项目登录失败时 HTTP 状态码仍然是 200，
    # 需要通过业务 code 判断是否登录成功。
    assert body.get("code") != 200
    # 失败场景data为空
    assert body.get("data") is None
    # 校验返回提示消息存在
    assert body.get("message")


@allure.feature("商城前台")
@allure.story("会员登录")
@allure.title("商城用户用户名为空登录失败")
@pytest.mark.portal
@pytest.mark.auth
def test_portal_login_empty_username():
    """验证商城用户用户名为空时不能登录。"""
    response = client.request(
        method="POST",
        url=f"{PORTAL_CONFIG['base_url']}/sso/login",
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data={
            "username": "", # 用户名为空字符串
            "password": PORTAL_CONFIG["password"],
        },
    )
    assert response.status_code == 200
    body = client.json_body(response)
    assert body.get("code") != 200
    assert body.get("data") is None
    assert body.get("message")


@allure.feature("商城前台")
@allure.story("会员登录")
@allure.title("商城用户密码为空登录失败")
@pytest.mark.portal
@pytest.mark.auth
def test_portal_login_empty_password():
    """验证商城用户密码为空时不能登录。"""
    response = client.request(
        method="POST",
        url=f"{PORTAL_CONFIG['base_url']}/sso/login",
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data={
            "username": PORTAL_CONFIG["username"],
            "password": "", # 密码传空字符串
        },
    )
    assert response.status_code == 200
    body = client.json_body(response)
    assert body.get("code") != 200
    assert body.get("data") is None
    assert body.get("message")


@allure.feature("商城前台")
@allure.story("购物车鉴权")
@allure.title("不携带 Token 访问购物车失败")
@pytest.mark.portal
@pytest.mark.auth
def test_cart_list_without_token():
    """验证未登录用户不能访问购物车。"""
    # GET请求购物车列表接口，请求头不带token
    response = client.request(
        method="GET",
        url=f"{PORTAL_CONFIG['base_url']}/cart/list",
    )
    assert response.status_code == 200
    body = client.json_body(response)
    # 当前项目的实际返回：
    # HTTP 200 + 业务 code 401
    assert body.get("code") == 401 # 业务码401：未授权，缺少token
    assert body.get("data") is not None
    # 返回消息包含token关键词
    assert "token" in body.get("message", "").lower()


@allure.feature("商城前台")
@allure.story("购物车鉴权")
@allure.title("携带有效 Token 访问购物车成功")
@pytest.mark.portal
@pytest.mark.auth
@pytest.mark.smoke
def test_cart_list_with_valid_token():
    """验证登录后携带有效 Token 可以访问购物车。"""
    # 调用登录函数，获取登录返回数据和token
    login_body = login_portal()
    token = login_body["data"]["token"]
    token_head = login_body["data"].get("tokenHead", "Bearer ")
    # GET请求购物车接口，请求头带上鉴权token
    response = client.request(
        method="GET",
        url=f"{PORTAL_CONFIG['base_url']}/cart/list",
        headers={
            "Authorization": f"{token_head}{token}", # 拼接Bearer前缀+token
        },
    )
    assert response.status_code == 200
    body = client.json_body(response)
    # 业务码200，鉴权成功，可以读取购物车数据
    assert body.get("code") == 200
    assert body.get("data") is not None
