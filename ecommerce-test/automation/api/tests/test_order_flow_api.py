"""
商城前台真实订单业务流程自动化测试。

测试范围：

1. 缺少收货地址生成订单失败；
2. 真实下单；
3. 动态获取订单 ID；
4. 查询订单详情；
5. 用户取消订单；
6. 验证订单状态变为已关闭；
7. 删除测试订单；
8. 恢复测试前的购物车数据。

重要说明：

1. 不写死订单 ID；
2. 不写死购物车 ID；
3. 不写死收货地址 ID；
4. 所有 ID 都通过接口动态获取；
5. 真实下单会将下单商品从购物车中删除；
6. 测试完成后会重新加入原购物车商品；
7. 取消订单会释放锁定库存；
8. 删除订单只执行逻辑删除，不会影响其他历史订单。
"""

# 导入项目路径处理工具
from pathlib import Path

# 导入类型注解
from typing import Any, Dict, List, Optional

# 导入 Allure
import allure

# 导入 pytest
import pytest

# 导入 YAML
import yaml

# 导入项目统一封装的 HTTP 客户端
from common.http_client import HttpClient


# ============================================================
# 一、读取项目配置
# ============================================================

# 当前文件：
# D:\ecommerce-test\automation\api\tests\test_order_flow_api.py
#
# parents[1]：
# D:\ecommerce-test\automation\api
API_ROOT = Path(__file__).resolve().parents[1]

# 配置文件路径
CONFIG_FILE = API_ROOT / "config" / "config.yaml"

# 读取配置文件
with CONFIG_FILE.open("r", encoding="utf-8") as file:
    CONFIG = yaml.safe_load(file)

# 商城前台配置
PORTAL_CONFIG = CONFIG["portal"]

# 创建 HTTP 客户端
client = HttpClient(timeout=CONFIG.get("timeout", 15))


# ============================================================
# 二、公共方法
# ============================================================

def login_portal() -> Dict[str, Any]:
    """
    登录商城前台。

    当前账号：

    用户名：test
    密码：123456
    """

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

    # 解析响应
    body = client.json_body(response)

    # 校验登录成功
    assert body.get("code") == 200
    assert isinstance(body.get("data"), dict)
    assert body["data"].get("token")

    return body


def get_auth_headers() -> Dict[str, str]:
    """
    动态登录并生成商城鉴权请求头。
    """

    login_body = login_portal()

    token = login_body["data"]["token"]
    token_head = login_body["data"].get("tokenHead", "Bearer ")

    return {
        "Authorization": f"{token_head}{token}",
    }


def parse_json(response) -> Dict[str, Any]:
    """
    解析接口 JSON 响应。
    """

    body = client.json_body(response)

    assert isinstance(body, dict)

    return body


def assert_success(response) -> Dict[str, Any]:
    """
    统一断言接口成功。

    成功标准：

    HTTP 状态码为 200；
    业务 code 为 200。
    """

    assert response.status_code == 200

    body = parse_json(response)

    assert body.get("code") == 200

    return body


# ============================================================
# 三、购物车公共方法
# ============================================================

def get_cart_items(
    headers: Dict[str, str],
) -> List[Dict[str, Any]]:
    """
    查询当前用户购物车。

    接口：

    GET /cart/list
    """

    response = client.request(
        method="GET",
        url=f"{PORTAL_CONFIG['base_url']}/cart/list",
        headers=headers,
    )

    body = assert_success(response)

    cart_items = body.get("data")

    assert isinstance(cart_items, list)

    return cart_items


def find_cart_item_by_sku(
    cart_items: List[Dict[str, Any]],
    product_sku_id: int,
) -> Optional[Dict[str, Any]]:
    """
    根据商品 SKU ID 查找购物车商品。
    """

    for cart_item in cart_items:
        if cart_item.get("productSkuId") == product_sku_id:
            return cart_item

    return None


def cart_item_to_add_payload(
    cart_item: Dict[str, Any],
) -> Dict[str, Any]:
    """
    将购物车查询结果转换成加入购物车的请求体。

    不传入：

    id
    memberId
    memberNickname
    createDate
    modifyDate
    deleteStatus

    这些字段应该由后端自动生成或维护。
    """

    return {
        "productId": cart_item.get("productId"),
        "productSkuId": cart_item.get("productSkuId"),
        "quantity": cart_item.get("quantity", 1),
        "price": cart_item.get("price"),
        "productPic": cart_item.get("productPic"),
        "productName": cart_item.get("productName"),
        "productSubTitle": cart_item.get("productSubTitle"),
        "productSkuCode": cart_item.get("productSkuCode"),
        "productCategoryId": cart_item.get("productCategoryId"),
        "productBrand": cart_item.get("productBrand"),
        "productSn": cart_item.get("productSn"),
        "productAttr": cart_item.get("productAttr"),
    }


def add_cart_item(
    headers: Dict[str, str],
    payload: Dict[str, Any],
) -> Dict[str, Any]:
    """
    将商品重新加入购物车。

    接口：

    POST /cart/add
    """

    response = client.request(
        method="POST",
        url=f"{PORTAL_CONFIG['base_url']}/cart/add",
        headers={
            **headers,
            "Content-Type": "application/json",
        },
        json=payload,
    )

    return assert_success(response)


def update_cart_quantity(
    headers: Dict[str, str],
    cart_id: int,
    quantity: int,
) -> Dict[str, Any]:
    """
    修改购物车商品数量。

    接口：

    GET /cart/update/quantity
    """

    response = client.request(
        method="GET",
        url=f"{PORTAL_CONFIG['base_url']}/cart/update/quantity",
        headers=headers,
        params={
            "id": cart_id,
            "quantity": quantity,
        },
    )

    return assert_success(response)


def restore_cart_item(
    headers: Dict[str, str],
    original_cart_item: Dict[str, Any],
) -> Dict[str, Any]:
    """
    恢复测试前的购物车商品。

    如果商品不存在：

    重新调用加入购物车接口。

    如果商品已经存在，但数量不一致：

    将数量恢复成原来的数量。
    """

    # 查询当前购物车
    current_items = get_cart_items(headers)

    # 获取原商品 SKU ID
    product_sku_id = original_cart_item["productSkuId"]

    # 查询该 SKU 当前是否已经存在
    current_item = find_cart_item_by_sku(
        current_items,
        product_sku_id,
    )

    # 原购物车数量
    original_quantity = original_cart_item.get("quantity", 1)

    if current_item is None:
        # 下单后原购物车商品已被删除，
        # 因此重新加入购物车。
        payload = cart_item_to_add_payload(original_cart_item)

        add_cart_item(
            headers=headers,
            payload=payload,
        )

    elif current_item.get("quantity") != original_quantity:
        # 如果商品存在但数量不一致，
        # 则将其恢复为测试前数量。
        update_cart_quantity(
            headers=headers,
            cart_id=current_item["id"],
            quantity=original_quantity,
        )

    # 再次查询并返回恢复后的商品
    restored_items = get_cart_items(headers)

    restored_item = find_cart_item_by_sku(
        restored_items,
        product_sku_id,
    )

    assert restored_item is not None
    assert restored_item.get("quantity") == original_quantity

    return restored_item


# ============================================================
# 四、收货地址公共方法
# ============================================================

def get_address_list(
    headers: Dict[str, str],
) -> List[Dict[str, Any]]:
    """
    查询当前用户收货地址。

    接口：

    GET /member/address/list
    """

    response = client.request(
        method="GET",
        url=f"{PORTAL_CONFIG['base_url']}/member/address/list",
        headers=headers,
    )

    body = assert_success(response)

    address_list = body.get("data")

    assert isinstance(address_list, list)

    return address_list


def select_receive_address(
    headers: Dict[str, str],
) -> Dict[str, Any]:
    """
    动态选择一个收货地址。

    优先选择默认地址；
    如果没有默认地址，则使用第一条地址。
    """

    address_list = get_address_list(headers)

    assert address_list, (
        "当前商城用户没有收货地址，无法执行真实下单测试。"
        "请先登录商城添加一个收货地址。"
    )

    # 优先查找默认地址
    for address in address_list:
        if address.get("defaultStatus") == 1:
            return address

    # 没有默认地址时使用第一条
    return address_list[0]


# ============================================================
# 五、订单公共方法
# ============================================================

def generate_order(
    headers: Dict[str, str],
    cart_id: int,
    address_id: Optional[int],
):
    """
    生成真实订单。

    接口：

    POST /order/generateOrder
    """

    payload = {
        # 收货地址 ID
        "memberReceiveAddressId": address_id,

        # 不使用优惠券
        "couponId": None,

        # 不使用积分
        "useIntegration": 0,

        # 支付方式 0：未支付
        "payType": 0,

        # 被选中的购物车商品 ID
        "cartIds": [cart_id],
    }

    return client.request(
        method="POST",
        url=f"{PORTAL_CONFIG['base_url']}/order/generateOrder",
        headers={
            **headers,
            "Content-Type": "application/json",
        },
        json=payload,
    )


def get_order_detail(
    headers: Dict[str, str],
    order_id: int,
) -> Dict[str, Any]:
    """
    查询订单详情。

    接口：

    GET /order/detail/{orderId}
    """

    response = client.request(
        method="GET",
        url=f"{PORTAL_CONFIG['base_url']}/order/detail/{order_id}",
        headers=headers,
    )

    body = assert_success(response)

    order_detail = body.get("data")

    assert isinstance(order_detail, dict)

    return order_detail


def cancel_user_order(
    headers: Dict[str, str],
    order_id: int,
) -> Dict[str, Any]:
    """
    用户取消待付款订单。

    接口：

    POST /order/cancelUserOrder
    """

    response = client.request(
        method="POST",
        url=f"{PORTAL_CONFIG['base_url']}/order/cancelUserOrder",
        headers=headers,
        params={
            "orderId": order_id,
        },
    )

    return assert_success(response)


def delete_user_order(
    headers: Dict[str, str],
    order_id: int,
) -> Dict[str, Any]:
    """
    用户删除已关闭订单。

    接口：

    POST /order/deleteOrder

    当前项目只允许删除：

    status = 3：已完成；
    status = 4：已关闭。
    """

    response = client.request(
        method="POST",
        url=f"{PORTAL_CONFIG['base_url']}/order/deleteOrder",
        headers=headers,
        params={
            "orderId": order_id,
        },
    )

    return assert_success(response)


def get_all_order_ids(
    headers: Dict[str, str],
) -> List[int]:
    """
    查询当前用户订单列表并返回订单 ID。

    接口：

    GET /order/list
    """

    response = client.request(
        method="GET",
        url=f"{PORTAL_CONFIG['base_url']}/order/list",
        headers=headers,
        params={
            "status": -1,
            "pageNum": 1,
            "pageSize": 100,
        },
    )

    body = assert_success(response)

    page_data = body.get("data")

    assert isinstance(page_data, dict)
    assert isinstance(page_data.get("list"), list)

    return [
        order["id"]
        for order in page_data["list"]
        if order.get("id") is not None
    ]


def safe_cleanup_order(
    headers: Dict[str, str],
    order_id: Optional[int],
) -> None:
    """
    测试异常时安全清理测试订单。

    处理流程：

    1. 查询订单详情；
    2. 如果订单为待付款，先取消；
    3. 如果订单为已关闭，再删除；
    4. 清理失败时写入 Allure 附件。
    """

    if order_id is None:
        return

    try:
        # 查询订单详情
        detail = get_order_detail(headers, order_id)

        # 获取当前订单状态
        status = detail.get("status")

        # 状态 0：待付款，需要先取消
        if status == 0:
            cancel_user_order(headers, order_id)

            # 重新查询状态
            detail = get_order_detail(headers, order_id)
            status = detail.get("status")

        # 状态 4：已关闭，可以删除
        if status == 4:
            delete_user_order(headers, order_id)

    except Exception as error:
        # 清理失败时写入 Allure 报告
        allure.attach(
            str(error),
            name=f"测试订单清理失败，order_id={order_id}",
            attachment_type=allure.attachment_type.TEXT,
        )


def safe_restore_cart(
    headers: Dict[str, str],
    original_cart_item: Dict[str, Any],
) -> None:
    """
    测试异常时安全恢复购物车。

    恢复失败时写入 Allure 附件，
    避免覆盖测试过程中真正的报错。
    """

    try:
        restore_cart_item(headers, original_cart_item)

    except Exception as error:
        allure.attach(
            str(error),
            name="购物车数据恢复失败",
            attachment_type=allure.attachment_type.TEXT,
        )


# ============================================================
# 六、订单业务测试用例
# ============================================================

@allure.feature("商城前台")
@allure.story("订单异常场景")
@allure.title("缺少收货地址生成订单失败且购物车数据不变")
@pytest.mark.portal
@pytest.mark.order
def test_generate_order_without_address():
    """
    验证未选择收货地址时不能生成订单。

    同时验证失败后购物车中的商品没有被删除。
    """

    # 获取商城 Token
    headers = get_auth_headers()

    # 查询测试前的购物车
    before_cart_items = get_cart_items(headers)

    assert before_cart_items, (
        "当前购物车为空，无法执行缺少收货地址的下单测试。"
    )

    # 选择第一条购物车数据
    cart_item = before_cart_items[0]

    cart_id = cart_item["id"]
    original_quantity = cart_item["quantity"]

    # 不传收货地址 ID
    response = generate_order(
        headers=headers,
        cart_id=cart_id,
        address_id=None,
    )

    # 业务失败通常仍然返回 HTTP 200；
    # 同时兼容后端直接返回 HTTP 500。
    assert response.status_code in (200, 500)

    body = parse_json(response)

    # 缺少地址不能返回业务成功
    assert body.get("code") != 200

    # 应该返回错误信息
    assert body.get("message")

    # 再次查询购物车
    after_cart_items = get_cart_items(headers)

    # 失败后原购物车商品仍然应该存在
    after_cart_item = next(
        (
            item
            for item in after_cart_items
            if item.get("id") == cart_id
        ),
        None,
    )

    assert after_cart_item is not None

    # 商品数量也不应该发生变化
    assert after_cart_item.get("quantity") == original_quantity


@allure.feature("商城前台")
@allure.story("订单完整流程")
@allure.title("真实下单取消删除并恢复购物车成功")
@pytest.mark.portal
@pytest.mark.order
@pytest.mark.smoke
def test_order_create_cancel_delete_flow():
    """
    验证真实订单完整业务闭环。

    流程：

    1. 查询购物车；
    2. 动态选择收货地址；
    3. 生成真实订单；
    4. 动态获取订单 ID；
    5. 查询订单详情；
    6. 验证购物车商品已删除；
    7. 取消订单；
    8. 验证订单状态为已关闭；
    9. 删除测试订单；
    10. 恢复测试前购物车商品。
    """

    # 获取商城 Token
    headers = get_auth_headers()

    # 查询测试前购物车
    original_cart_items = get_cart_items(headers)

    assert original_cart_items, (
        "当前购物车为空，无法执行真实下单测试。"
        "请先在商城中加入一件商品。"
    )

    # 选择第一条购物车商品作为下单商品
    original_cart_item = original_cart_items[0]

    # 动态获取购物车 ID
    cart_id = original_cart_item["id"]

    # 动态选择收货地址
    receive_address = select_receive_address(headers)

    # 动态获取地址 ID
    address_id = receive_address["id"]

    # 保存测试过程中生成的订单 ID
    order_id = None

    # 标记正常清理是否已经完成
    cleanup_completed = False

    try:
        # ----------------------------------------------------
        # 第一步：生成真实订单
        # ----------------------------------------------------

        response = generate_order(
            headers=headers,
            cart_id=cart_id,
            address_id=address_id,
        )

        body = assert_success(response)

        # 下单接口响应 data 应该是字典
        order_result = body.get("data")
        assert isinstance(order_result, dict)

        # 获取订单对象
        order = order_result.get("order")
        assert isinstance(order, dict)

        # 动态获取订单 ID
        order_id = order.get("id")
        assert order_id is not None

        # 校验订单编号
        assert order.get("orderSn")

        # 新订单应该为待付款状态
        assert order.get("status") == 0

        # 校验订单商品列表
        order_item_list = order_result.get("orderItemList")
        assert isinstance(order_item_list, list)
        assert order_item_list

        # ----------------------------------------------------
        # 第二步：查询订单详情
        # ----------------------------------------------------

        order_detail = get_order_detail(
            headers=headers,
            order_id=order_id,
        )

        # 详情中的订单 ID 应与下单响应一致
        assert order_detail.get("id") == order_id

        # 详情中的订单编号应与下单响应一致
        assert order_detail.get("orderSn") == order.get("orderSn")

        # 新订单状态应为待付款
        assert order_detail.get("status") == 0

        # 收货地址信息应该正确
        assert order_detail.get("receiverName") == receive_address.get(
            "name"
        )

        # ----------------------------------------------------
        # 第三步：验证下单商品已从购物车删除
        # ----------------------------------------------------

        after_order_cart_items = get_cart_items(headers)

        assert all(
            item.get("id") != cart_id
            for item in after_order_cart_items
        )

        # ----------------------------------------------------
        # 第四步：取消订单
        # ----------------------------------------------------

        cancel_user_order(
            headers=headers,
            order_id=order_id,
        )

        # 重新查询订单详情
        cancelled_detail = get_order_detail(
            headers=headers,
            order_id=order_id,
        )

        # 状态 4 代表订单已关闭
        assert cancelled_detail.get("status") == 4

        # ----------------------------------------------------
        # 第五步：删除已关闭订单
        # ----------------------------------------------------

        delete_user_order(
            headers=headers,
            order_id=order_id,
        )

        # 查询当前可见订单 ID
        visible_order_ids = get_all_order_ids(headers)

        # 逻辑删除后的订单不应继续出现在订单列表中
        assert order_id not in visible_order_ids

        # ----------------------------------------------------
        # 第六步：恢复购物车
        # ----------------------------------------------------

        restored_cart_item = restore_cart_item(
            headers=headers,
            original_cart_item=original_cart_item,
        )

        # 恢复后的 SKU 应与测试前一致
        assert restored_cart_item.get(
            "productSkuId"
        ) == original_cart_item.get("productSkuId")

        # 恢复后的数量应与测试前一致
        assert restored_cart_item.get(
            "quantity"
        ) == original_cart_item.get("quantity")

        # 正常流程和数据恢复均已完成
        cleanup_completed = True

    finally:
        # 如果测试中途失败，尝试清理订单并恢复购物车。
        #
        # 如果整个流程已经正常完成，则不需要重复清理。
        if not cleanup_completed:
            safe_cleanup_order(
                headers=headers,
                order_id=order_id,
            )

            safe_restore_cart(
                headers=headers,
                original_cart_item=original_cart_item,
            )