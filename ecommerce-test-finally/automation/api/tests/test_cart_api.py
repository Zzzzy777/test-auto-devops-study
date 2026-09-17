"""
商城前台购物车业务接口自动化测试。

测试范围：

1. 查询购物车促销信息；
2. 加入购物车并查询加入结果；
3. 修改购物车商品数量；
4. 清空购物车并验证清空结果；
5. 测试结束后尽量恢复测试前的数据。

说明：

1. 商城后端地址：http://localhost:8085；
2. 每次测试都会动态登录获取 Token；
3. 不使用固定旧 Token；
4. 加入购物车、修改数量、清空购物车等操作完成后，
   会尽量恢复测试前的购物车数据；
5. 清空购物车和“清空后验证”合并为一个测试用例，
   避免重复统计测试数量。
"""

# 导入路径处理工具
from pathlib import Path

# 导入深拷贝工具，防止修改测试前的数据快照
from copy import deepcopy

# 导入类型注解
from typing import Any, Dict, List, Optional

# 导入 Allure，用于生成测试报告
import allure

# 导入 pytest 测试框架
import pytest

# 导入 yaml，用于读取项目配置
import yaml

# 导入项目中封装的 HTTP 客户端
from common.http_client import HttpClient


# ============================================================
# 一、读取项目配置
# ============================================================

# 当前文件位置：
# D:\ecommerce-test\automation\api\tests\test_cart_api.py
#
# parents[1] 对应：
# D:\ecommerce-test\automation\api
API_ROOT = Path(__file__).resolve().parents[1]


# 配置文件路径
CONFIG_FILE = API_ROOT / "config" / "config.yaml"


# 读取 YAML 配置文件
with CONFIG_FILE.open("r", encoding="utf-8") as file:
    CONFIG = yaml.safe_load(file)


# 获取商城前台配置
PORTAL_CONFIG = CONFIG["portal"]


# 创建统一 HTTP 客户端
client = HttpClient(timeout=CONFIG.get("timeout", 15))


# ============================================================
# 二、测试商品配置
# ============================================================

# 使用项目中已经验证过的商品 29 和 SKU 106。
#
# 商品信息来源于 mall 项目 Postman 接口示例，
# 以及前面实际查询到的商城商品数据。
TEST_PRODUCT = {
    "price": 5499,
    "productId": 29,
    "productName": "Apple iPhone 8 Plus",
    "productSkuCode": "201808270029001",
    "productSkuId": 106,
    "productSubTitle": (
        "【限时限量抢购】Apple产品年中狂欢节，好物尽享，美在智慧！"
        "速来 >> 勾选[保障服务][原厂保2年]，获得AppleCare+全方位服务计划，"
        "原厂延保售后无忧。"
    ),
    "quantity": 1,
    "sp1": "金色",
    "sp2": "32G",
    "sp3": None,
}


# ============================================================
# 三、公共方法
# ============================================================

def login_portal() -> Dict[str, Any]:
    """
    登录商城前台并返回登录响应。

    当前账号：

    用户名：test
    密码：123456
    """

    # 商城前台登录接口使用表单格式提交
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

    # 登录接口 HTTP 状态码应该为 200
    assert response.status_code == 200

    # 解析响应 JSON
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
    动态登录并生成商城接口鉴权请求头。

    返回示例：

    {
        "Authorization": "Bearer xxxxxx"
    }
    """

    # 每次动态登录获取 Token
    login_body = login_portal()

    # 获取 Token
    token = login_body["data"]["token"]

    # 获取 Token 前缀
    # 当前项目通常返回：Bearer 空格
    token_head = login_body["data"].get("tokenHead", "Bearer ")

    # 返回请求头
    return {
        "Authorization": f"{token_head}{token}",
    }


def parse_json(response) -> Dict[str, Any]:
    """
    解析接口返回 JSON。
    """

    body = client.json_body(response)

    # 当前 mall 项目接口一般都会返回 JSON 对象
    assert isinstance(body, dict)

    return body


def assert_success(response) -> Dict[str, Any]:
    """
    统一断言接口调用成功。

    成功标准：

    1. HTTP 状态码为 200；
    2. 业务 code 为 200。
    """

    # 校验 HTTP 状态码
    assert response.status_code == 200

    # 解析响应内容
    body = parse_json(response)

    # 校验业务状态码
    assert body.get("code") == 200

    return body


def get_cart_items(headers: Dict[str, str]) -> List[Dict[str, Any]]:
    """
    查询当前商城用户购物车列表。

    接口：

    GET /cart/list
    """

    # 调用购物车查询接口
    response = client.request(
        method="GET",
        url=f"{PORTAL_CONFIG['base_url']}/cart/list",
        headers=headers,
    )

    # 校验接口成功
    body = assert_success(response)

    # 获取购物车数据
    data = body.get("data")

    # 当前项目购物车列表为空时，通常返回空数组
    assert isinstance(data, list)

    return data


def find_cart_item(
    cart_items: List[Dict[str, Any]],
    product_sku_id: int,
) -> Optional[Dict[str, Any]]:
    """
    根据 SKU ID 查找购物车商品。

    找到时返回购物车商品对象；
    找不到时返回 None。
    """

    for item in cart_items:
        if item.get("productSkuId") == product_sku_id:
            return item

    return None


def add_product_to_cart(
    headers: Dict[str, str],
    quantity: int = 1,
) -> Dict[str, Any]:
    """
    将测试商品加入购物车。

    接口：

    POST /cart/add
    """

    # 深拷贝商品数据，避免修改全局测试数据
    payload = deepcopy(TEST_PRODUCT)

    # 设置本次加入数量
    payload["quantity"] = quantity

    # 调用加入购物车接口
    response = client.request(
        method="POST",
        url=f"{PORTAL_CONFIG['base_url']}/cart/add",
        headers={
            **headers,
            "Content-Type": "application/json",
        },
        json=payload,
    )

    # 校验接口成功
    body = assert_success(response)

    return body


def update_cart_quantity(
    headers: Dict[str, str],
    cart_id: int,
    quantity: int,
) -> Dict[str, Any]:
    """
    修改购物车商品数量。

    接口：

    GET /cart/update/quantity?id=购物车ID&quantity=数量
    """

    # 调用修改数量接口
    response = client.request(
        method="GET",
        url=f"{PORTAL_CONFIG['base_url']}/cart/update/quantity",
        headers=headers,
        params={
            "id": cart_id,
            "quantity": quantity,
        },
    )

    # 校验接口成功
    body = assert_success(response)

    return body


def delete_cart_item(
    headers: Dict[str, str],
    cart_id: int,
) -> Dict[str, Any]:
    """
    删除购物车中的指定商品。

    接口：

    POST /cart/delete?ids=购物车ID

    该方法主要用于清理测试过程中新增的商品。
    """

    # 调用删除购物车商品接口
    response = client.request(
        method="POST",
        url=f"{PORTAL_CONFIG['base_url']}/cart/delete",
        headers=headers,
        params={
            "ids": cart_id,
        },
    )

    # 校验接口成功
    body = assert_success(response)

    return body


def cart_item_to_add_payload(item: Dict[str, Any]) -> Dict[str, Any]:
    """
    将购物车查询结果转换为加入购物车接口需要的请求参数。

    查询购物车返回的数据中可能包含：
    id、memberId、deleteStatus 等数据库字段。

    加入购物车时只保留接口需要的商品字段，
    避免把数据库主键等无关字段再次传给接口。
    """

    return {
        "price": item.get("price"),
        "productId": item.get("productId"),
        "productName": item.get("productName"),
        "productSkuCode": item.get("productSkuCode"),
        "productSkuId": item.get("productSkuId"),
        "productSubTitle": item.get("productSubTitle"),
        "quantity": item.get("quantity", 1),
        "sp1": item.get("sp1"),
        "sp2": item.get("sp2"),
        "sp3": item.get("sp3"),
    }


def restore_cart_items(
    headers: Dict[str, str],
    original_items: List[Dict[str, Any]],
) -> None:
    """
    尽量恢复清空购物车之前的数据。

    清空接口在项目中属于逻辑删除，
    因此清空后原购物车商品不会再出现在购物车列表中。

    这里通过重新调用加入购物车接口，
    将测试前的有效购物车商品恢复回来。
    """

    restore_errors = []

    for item in original_items:
        try:
            payload = cart_item_to_add_payload(item)

            response = client.request(
                method="POST",
                url=f"{PORTAL_CONFIG['base_url']}/cart/add",
                headers={
                    **headers,
                    "Content-Type": "application/json",
                },
                json=payload,
            )

            body = parse_json(response)

            if response.status_code != 200 or body.get("code") != 200:
                restore_errors.append(
                    f"商品 SKU={item.get('productSkuId')} 恢复失败：{body}"
                )

        except Exception as error:
            restore_errors.append(
                f"商品 SKU={item.get('productSkuId')} 恢复异常：{error}"
            )

    # 如果恢复过程中出现问题，写入 Allure 附件，
    # 方便在报告中查看，但不覆盖原始测试异常。
    if restore_errors:
        allure.attach(
            "\n".join(restore_errors),
            name="购物车数据恢复异常",
            attachment_type=allure.attachment_type.TEXT,
        )


# ============================================================
# 四、购物车接口测试用例
# ============================================================

@allure.feature("商城前台")
@allure.story("购物车")
@allure.title("查询购物车促销信息成功")
@pytest.mark.portal
@pytest.mark.product
def test_cart_promotion_list():
    """
    验证登录用户可以查询购物车促销信息。

    接口：

    GET /cart/list/promotion
    """

    # 获取商城接口 Token
    headers = get_auth_headers()

    # 调用购物车促销信息接口
    response = client.request(
        method="GET",
        url=f"{PORTAL_CONFIG['base_url']}/cart/list/promotion",
        headers=headers,
    )

    # 校验接口成功
    body = assert_success(response)

    # 当前项目即使没有促销商品，
    # data 也应该返回列表结构
    assert isinstance(body.get("data"), list)


@allure.feature("商城前台")
@allure.story("购物车")
@allure.title("加入购物车并查询加入结果成功")
@pytest.mark.portal
@pytest.mark.product
def test_cart_add_and_query_result():
    """
    验证商品加入购物车后可以查询到，
    并且购物车数量发生正确变化。

    接口：

    POST /cart/add
    GET /cart/list
    """

    # 获取商城接口 Token
    headers = get_auth_headers()

    # 记录测试前的购物车数据
    before_items = get_cart_items(headers)

    # 查找测试 SKU 在测试前是否已经存在
    before_item = find_cart_item(
        before_items,
        TEST_PRODUCT["productSkuId"],
    )

    # 记录测试前数量
    before_quantity = (
        before_item.get("quantity", 0)
        if before_item is not None
        else 0
    )

    try:
        # 加入 1 件测试商品
        add_body = add_product_to_cart(headers, quantity=1)

        # 加入接口通常返回成功数量
        assert add_body.get("data") is not None

        # 再次查询购物车
        after_items = get_cart_items(headers)

        # 查找刚加入的 SKU
        after_item = find_cart_item(
            after_items,
            TEST_PRODUCT["productSkuId"],
        )

        # 加入后必须可以查询到该商品
        assert after_item is not None

        # 数量应该比测试前增加 1
        assert after_item.get("quantity") == before_quantity + 1

    finally:
        # 恢复测试前的购物车状态
        current_items = get_cart_items(headers)

        current_item = find_cart_item(
            current_items,
            TEST_PRODUCT["productSkuId"],
        )

        if before_item is not None:
            # 如果测试前已经存在该商品，
            # 则将数量恢复成原来的数量。
            assert current_item is not None

            update_cart_quantity(
                headers=headers,
                cart_id=current_item["id"],
                quantity=before_quantity,
            )

        elif current_item is not None:
            # 如果测试前不存在该商品，
            # 则删除本次测试新增的商品。
            delete_cart_item(
                headers=headers,
                cart_id=current_item["id"],
            )


@allure.feature("商城前台")
@allure.story("购物车")
@allure.title("修改购物车商品数量成功并恢复原数量")
@pytest.mark.portal
@pytest.mark.product
def test_cart_update_quantity_and_restore():
    """
    验证购物车商品数量可以修改，
    测试结束后恢复原数量。

    接口：

    GET /cart/list
    GET /cart/update/quantity
    """

    # 获取商城接口 Token
    headers = get_auth_headers()

    # 查询测试前购物车
    before_items = get_cart_items(headers)

    # 优先使用测试商品；
    # 如果测试商品不存在，则使用购物车中的第一件商品。
    target_item = find_cart_item(
        before_items,
        TEST_PRODUCT["productSkuId"],
    )

    if target_item is None and before_items:
        target_item = before_items[0]

    # 如果当前购物车为空，
    # 则先加入测试商品，保证修改数量接口有测试对象。
    created_by_test = False

    if target_item is None:
        add_product_to_cart(headers, quantity=1)
        created_by_test = True

        after_add_items = get_cart_items(headers)

        target_item = find_cart_item(
            after_add_items,
            TEST_PRODUCT["productSkuId"],
        )

        assert target_item is not None

    # 保存原数量
    original_quantity = target_item.get("quantity", 1)

    # 目标数量设置为原数量加 1
    new_quantity = original_quantity + 1

    try:
        # 修改数量
        update_cart_quantity(
            headers=headers,
            cart_id=target_item["id"],
            quantity=new_quantity,
        )

        # 再次查询购物车
        after_update_items = get_cart_items(headers)

        # 找到修改后的商品
        updated_item = find_cart_item(
            after_update_items,
            target_item.get("productSkuId"),
        )

        # 修改后商品必须存在
        assert updated_item is not None

        # 校验商品数量已经修改
        assert updated_item.get("quantity") == new_quantity

    finally:
        # 如果商品原本就存在，恢复原数量
        if not created_by_test:
            current_items = get_cart_items(headers)

            current_item = find_cart_item(
                current_items,
                target_item.get("productSkuId"),
            )

            if current_item is not None:
                update_cart_quantity(
                    headers=headers,
                    cart_id=current_item["id"],
                    quantity=original_quantity,
                )

        else:
            # 如果是测试过程中新增的商品，
            # 则删除该测试商品，恢复测试前空购物车状态。
            current_items = get_cart_items(headers)

            current_item = find_cart_item(
                current_items,
                TEST_PRODUCT["productSkuId"],
            )

            if current_item is not None:
                delete_cart_item(
                    headers=headers,
                    cart_id=current_item["id"],
                )


@allure.feature("商城前台")
@allure.story("购物车")
@allure.title("清空购物车并验证购物车为空")
@pytest.mark.portal
@pytest.mark.product
def test_cart_clear_and_verify_empty():
    """
    验证登录用户可以清空购物车，
    并且清空后购物车列表为空。

    测试完成后会尽量恢复测试前购物车数据。

    接口：

    POST /cart/clear
    GET /cart/list
    """

    # 获取商城接口 Token
    headers = get_auth_headers()

    # 记录测试前购物车数据
    before_items = get_cart_items(headers)

    # 深拷贝测试前数据，
    # 避免后续操作影响恢复数据
    original_items = deepcopy(before_items)

    # 如果测试前购物车为空，
    # 先加入一件测试商品，
    # 确保清空接口有实际数据可以处理。
    if not before_items:
        add_product_to_cart(headers, quantity=1)

        # 确认测试商品加入成功
        prepared_items = get_cart_items(headers)
        assert find_cart_item(
            prepared_items,
            TEST_PRODUCT["productSkuId"],
        ) is not None

    try:
        # 调用清空购物车接口
        response = client.request(
            method="POST",
            url=f"{PORTAL_CONFIG['base_url']}/cart/clear",
            headers=headers,
        )

        # 校验清空接口成功
        body = assert_success(response)

        # 清空接口通常返回受影响的数据条数
        assert body.get("data") is not None

        # 清空后再次查询购物车
        after_clear_items = get_cart_items(headers)

        # 这里就是原来“清空后验证”的内容，
        # 现在合并在同一个测试用例中。
        assert after_clear_items == []

    finally:
        # 恢复测试前购物车商品
        restore_cart_items(
            headers=headers,
            original_items=original_items,
        )

        # 如果测试前购物车原本为空，
        # original_items 就是空列表，
        # 恢复后应保持为空。
        if not original_items:
            restored_items = get_cart_items(headers)
            assert restored_items == []