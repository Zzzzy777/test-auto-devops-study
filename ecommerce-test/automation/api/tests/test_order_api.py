"""
商城前台订单查询和确认单接口自动化测试。

本文件测试范围：

1. 登录用户查询订单列表；
2. 登录用户动态查询订单详情；
3. 根据购物车生成订单确认单；
4. 未登录查询订单列表失败；
5. 携带无效 Token 查询订单列表失败。

本文件暂时不执行真实下单。

原因：

真实下单会影响：

1. 商品库存；
2. 购物车数据；
3. 订单数据；
4. 订单状态。

后续会单独设计：

登录
    -> 加入购物车
    -> 选择收货地址
    -> 生成订单
    -> 动态获取订单 ID
    -> 取消订单
    -> 验证订单状态
"""

# 导入项目路径处理工具
from pathlib import Path

# 导入类型注解
from typing import Any, Dict, List

# 导入 Allure
import allure

# 导入 pytest
import pytest

# 导入 yaml 配置读取工具
import yaml

# 导入项目统一封装的 HTTP 客户端
from common.http_client import HttpClient


# ============================================================
# 一、读取项目配置
# ============================================================

# 当前文件位置：
# D:\ecommerce-test\automation\api\tests\test_order_api.py
#
# parents[1] 对应：
# D:\ecommerce-test\automation\api
API_ROOT = Path(__file__).resolve().parents[1]


# 配置文件路径
CONFIG_FILE = API_ROOT / "config" / "config.yaml"


# 读取 YAML 配置
with CONFIG_FILE.open("r", encoding="utf-8") as file:
    CONFIG = yaml.safe_load(file)


# 获取商城前台配置
PORTAL_CONFIG = CONFIG["portal"]


# 创建 HTTP 请求客户端
client = HttpClient(timeout=CONFIG.get("timeout", 15))


# ============================================================
# 二、公共方法
# ============================================================

def login_portal() -> Dict[str, Any]:
    """
    登录商城前台并获取登录结果。

    当前账号：

    用户名：test
    密码：123456
    """

    # 商城登录接口使用表单格式
    response = client.request(
        method="POST",
        url=f"{PORTAL_CONFIG['base_url']}/sso/login",
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data={
            "username": PORTAL_CONFIG["username"],
            "password": PORTAL_CONFIG["password"],
        },
    )

    # 校验 HTTP 状态码
    assert response.status_code == 200

    # 解析 JSON 响应
    body = client.json_body(response)

    # 校验登录业务成功
    assert body.get("code") == 200

    # 校验登录数据存在
    assert isinstance(body.get("data"), dict)

    # 校验 Token 存在
    assert body["data"].get("token")

    return body


def get_auth_headers() -> Dict[str, str]:
    """
    动态登录并生成商城接口请求头。
    """

    # 登录获取 Token
    login_body = login_portal()

    # 获取 Token
    token = login_body["data"]["token"]

    # 获取 Token 前缀
    token_head = login_body["data"].get("tokenHead", "Bearer ")

    # 返回 Authorization 请求头
    return {
        "Authorization": f"{token_head}{token}",
    }


def parse_json(response) -> Dict[str, Any]:
    """
    解析接口 JSON 响应。
    """

    # 通过公共客户端解析响应
    body = client.json_body(response)

    # 当前接口响应应该是字典
    assert isinstance(body, dict)

    return body


def assert_success(response) -> Dict[str, Any]:
    """
    统一断言接口成功。

    成功标准：

    1. HTTP 状态码为 200；
    2. 业务 code 为 200。
    """

    # 校验 HTTP 状态码
    assert response.status_code == 200

    # 解析响应
    body = parse_json(response)

    # 校验业务状态码
    assert body.get("code") == 200

    return body


def assert_unauthorized(response) -> Dict[str, Any]:
    """
    统一断言未登录或 Token 无效。

    项目通常返回：

    HTTP 200
    code 401
    """

    # 兼容项目返回 HTTP 200 或 HTTP 401 两种情况
    assert response.status_code in (200, 401)

    # 解析响应
    body = parse_json(response)

    # 鉴权失败不能返回业务成功
    assert body.get("code") != 200

    # 应该有错误提示
    assert body.get("message")

    return body


def get_cart_items(headers: Dict[str, str]) -> List[Dict[str, Any]]:
    """
    查询当前用户购物车商品。

    接口：

    GET /cart/list
    """

    # 查询购物车
    response = client.request(
        method="GET",
        url=f"{PORTAL_CONFIG['base_url']}/cart/list",
        headers=headers,
    )

    # 校验接口成功
    body = assert_success(response)

    # 获取购物车列表
    cart_items = body.get("data")

    # 购物车 data 应该是列表
    assert isinstance(cart_items, list)

    return cart_items


def get_order_page(
    headers: Dict[str, str],
    status: int = -1,
    page_num: int = 1,
    page_size: int = 5,
) -> Dict[str, Any]:
    """
    查询订单分页数据。

    接口：

    GET /order/list

    status 参数：

    -1：全部订单
     0：待付款
     1：待发货
     2：已发货
     3：已完成
     4：已关闭
    """

    # 查询订单分页列表
    response = client.request(
        method="GET",
        url=f"{PORTAL_CONFIG['base_url']}/order/list",
        headers=headers,
        params={
            "status": status,
            "pageNum": page_num,
            "pageSize": page_size,
        },
    )

    # 校验接口成功
    body = assert_success(response)

    # 获取分页数据
    data = body.get("data")

    # 分页数据应该是字典结构
    assert isinstance(data, dict)

    # 校验分页字段存在
    assert "list" in data
    assert "total" in data
    assert "pageNum" in data
    assert "pageSize" in data

    # list 必须是列表
    assert isinstance(data["list"], list)

    return data


def get_order_detail(
    headers: Dict[str, str],
    order_id: int,
) -> Dict[str, Any]:
    """
    根据订单 ID 查询订单详情。

    接口：

    GET /order/detail/{orderId}
    """

    # 查询订单详情
    response = client.request(
        method="GET",
        url=f"{PORTAL_CONFIG['base_url']}/order/detail/{order_id}",
        headers=headers,
    )

    # 校验接口成功
    body = assert_success(response)

    # 获取订单详情
    order_detail = body.get("data")

    # 订单详情应该是字典
    assert isinstance(order_detail, dict)

    return order_detail


def generate_confirm_order(
    headers: Dict[str, str],
    cart_ids: List[int],
) -> Dict[str, Any]:
    """
    根据购物车商品生成订单确认单。

    真实接口：

    POST /order/generateConfirmOrder

    请求体是购物车 ID 数组，例如：

    [120]
    """

    # 调用真实的确认单接口
    response = client.request(
        method="POST",
        url=f"{PORTAL_CONFIG['base_url']}/order/generateConfirmOrder",
        headers={
            **headers,
            "Content-Type": "application/json",
        },
        json=cart_ids,
    )

    # 校验接口成功
    body = assert_success(response)

    # 确认单数据应该是字典
    confirm_data = body.get("data")

    assert isinstance(confirm_data, dict)

    return confirm_data


# ============================================================
# 三、订单接口测试用例
# ============================================================

@allure.feature("商城前台")
@allure.story("订单查询")
@allure.title("登录用户查询全部订单列表成功")
@pytest.mark.portal
@pytest.mark.order
@pytest.mark.smoke
def test_order_list_success():
    """
    验证登录用户可以查询全部订单。

    接口：

    GET /order/list?status=-1&pageNum=1&pageSize=5
    """

    # 获取商城 Token
    headers = get_auth_headers()

    # 查询全部订单
    order_page = get_order_page(
        headers=headers,
        status=-1,
        page_num=1,
        page_size=5,
    )

    # 当前项目应该存在历史订单
    # 如果后续数据库被重置，也允许订单列表为空，
    # 但分页结构必须正确。
    assert order_page["total"] >= 0


@allure.feature("商城前台")
@allure.story("订单查询")
@allure.title("根据订单列表中的订单 ID 查询订单详情成功")
@pytest.mark.portal
@pytest.mark.order
def test_order_detail_success():
    """
    验证可以根据订单列表中动态获取的订单 ID 查询详情。

    注意：

    订单 ID 不写死，必须从订单列表接口动态获取。
    """

    # 获取商城 Token
    headers = get_auth_headers()

    # 查询全部订单
    order_page = get_order_page(
        headers=headers,
        status=-1,
        page_num=1,
        page_size=5,
    )

    # 当前测试环境应该存在历史订单
    assert order_page["list"], (
        "当前商城用户没有历史订单，无法执行订单详情测试。"
        "请先在商城中完成一笔测试订单，或者后续使用动态下单流程创建订单。"
    )

    # 获取第一条订单
    first_order = order_page["list"][0]

    # 订单必须包含 ID
    order_id = first_order.get("id")
    assert order_id is not None

    # 动态查询订单详情
    detail = get_order_detail(headers, order_id)

    # 校验详情中的订单 ID 与列表中的 ID 一致
    assert detail.get("id") == order_id

    # 订单必须有订单编号
    assert detail.get("orderSn")

    # 订单必须有订单状态
    assert detail.get("status") is not None


@allure.feature("商城前台")
@allure.story("订单确认")
@allure.title("根据购物车生成订单确认单成功")
@pytest.mark.portal
@pytest.mark.order
def test_generate_confirm_order_success():
    """
    验证可以根据购物车商品生成订单确认单。

    真实接口：

    POST /order/generateConfirmOrder

    该接口只生成确认单，不会真正生成订单。
    """

    # 获取商城 Token
    headers = get_auth_headers()

    # 查询当前购物车
    cart_items = get_cart_items(headers)

    # 当前测试环境中需要至少有一件购物车商品
    assert cart_items, (
        "当前购物车为空，无法生成订单确认单。"
        "请先在商城中加入一件商品后重新执行。"
    )

    # 取第一件购物车商品的购物车 ID
    cart_id = cart_items[0].get("id")

    # 购物车 ID 必须存在
    assert cart_id is not None

    # 生成确认单
    confirm_data = generate_confirm_order(
        headers=headers,
        cart_ids=[cart_id],
    )

    # 确认单应该包含购物车促销信息
    assert "cartPromotionItemList" in confirm_data

    # 确认单应该包含收货地址列表
    assert "memberReceiveAddressList" in confirm_data

    # 确认单应该包含优惠券信息列表
    assert "couponHistoryDetailList" in confirm_data

    # 确认单应该包含积分信息
    assert "memberIntegration" in confirm_data

    # 确认单应该包含金额计算信息
    assert isinstance(confirm_data.get("calcAmount"), dict)

    # 当前选中的购物车商品应该存在于确认单中
    promotion_items = confirm_data.get("cartPromotionItemList")
    assert isinstance(promotion_items, list)
    assert promotion_items


@allure.feature("商城前台")
@allure.story("订单鉴权")
@allure.title("未携带 Token 查询订单列表失败")
@pytest.mark.portal
@pytest.mark.order
@pytest.mark.auth
def test_order_list_without_token():
    """
    验证未登录用户不能查询订单列表。

    接口：

    GET /order/list
    """

    # 不携带 Authorization 请求头
    response = client.request(
        method="GET",
        url=f"{PORTAL_CONFIG['base_url']}/order/list",
        params={
            "status": -1,
            "pageNum": 1,
            "pageSize": 5,
        },
    )

    # 校验鉴权失败
    body = assert_unauthorized(response)

    # 当前项目通常返回业务码 401
    assert body.get("code") == 401


@allure.feature("商城前台")
@allure.story("订单鉴权")
@allure.title("携带无效 Token 查询订单列表失败")
@pytest.mark.portal
@pytest.mark.order
@pytest.mark.auth
def test_order_list_with_invalid_token():
    """
    验证携带无效 Token 不能查询订单列表。

    接口：

    GET /order/list
    """

    # 构造无效 Token
    invalid_headers = {
        "Authorization": "Bearer invalid-order-token",
    }

    # 携带无效 Token 查询订单列表
    response = client.request(
        method="GET",
        url=f"{PORTAL_CONFIG['base_url']}/order/list",
        headers=invalid_headers,
        params={
            "status": -1,
            "pageNum": 1,
            "pageSize": 5,
        },
    )

    # 校验鉴权失败
    body = assert_unauthorized(response)

    # 无效 Token 不能返回成功
    assert body.get("code") != 200