"""
商城前台收货地址接口自动化测试。

测试范围：

1. 查询收货地址列表；
2. 未登录访问收货地址列表；
3. 新增收货地址并查询详情；
4. 修改收货地址并验证修改结果；
5. 删除收货地址并验证删除结果。

接口地址：

GET  /member/address/list
POST /member/address/add
GET  /member/address/{id}
POST /member/address/update/{id}
POST /member/address/delete/{id}

注意：

1. 所有请求都会动态登录获取 Token；
2. 不使用固定地址 ID；
3. 测试地址使用唯一标识；
4. 测试结束后只清理本次创建的测试地址；
5. 不会删除用户原有地址。
"""

# 导入时间模块，用于生成唯一测试数据
import time

# 导入路径处理工具
from pathlib import Path

# 导入类型注解
from typing import Any, Dict, List, Optional

# 导入 Allure
import allure

# 导入 pytest
import pytest

# 导入 YAML 配置读取工具
import yaml

# 导入项目统一封装的 HTTP 客户端
from common.http_client import HttpClient


# ============================================================
# 一、读取项目配置
# ============================================================

# 当前文件路径：
# D:\ecommerce-test\automation\api\tests\test_address_api.py
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


# 创建 HTTP 客户端
client = HttpClient(timeout=CONFIG.get("timeout", 15))


# ============================================================
# 二、公共方法
# ============================================================

def login_portal() -> Dict[str, Any]:
    """
    登录商城前台并返回登录结果。

    当前商城账号：

    用户名：test
    密码：123456
    """

    # 商城登录接口使用表单格式提交
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
    动态登录并生成请求头。

    返回格式：

    {
        "Authorization": "Bearer xxxxxx"
    }
    """

    # 登录商城前台
    login_body = login_portal()

    # 获取 Token
    token = login_body["data"]["token"]

    # 获取 Token 前缀
    token_head = login_body["data"].get("tokenHead", "Bearer ")

    # 返回鉴权请求头
    return {
        "Authorization": f"{token_head}{token}",
    }


def parse_json(response) -> Dict[str, Any]:
    """
    安全解析 JSON 响应。
    """

    # 使用公共客户端解析 JSON
    body = client.json_body(response)

    # 响应应该是字典结构
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


def get_address_list(headers: Dict[str, str]) -> List[Dict[str, Any]]:
    """
    查询当前登录用户的收货地址列表。

    接口：

    GET /member/address/list
    """

    # 调用收货地址列表接口
    response = client.request(
        method="GET",
        url=f"{PORTAL_CONFIG['base_url']}/member/address/list",
        headers=headers,
    )

    # 校验请求成功
    body = assert_success(response)

    # 获取地址列表
    address_list = body.get("data")

    # 当前接口应该返回数组
    assert isinstance(address_list, list)

    return address_list


def find_address_by_detail(
    address_list: List[Dict[str, Any]],
    detail_address: str,
) -> Optional[Dict[str, Any]]:
    """
    根据详细地址查找收货地址。

    测试数据使用唯一详细地址，
    因此可以通过 detailAddress 找到本次创建的数据。
    """

    # 遍历地址列表
    for address in address_list:
        if address.get("detailAddress") == detail_address:
            return address

    # 没有找到时返回 None
    return None


def create_unique_address_payload() -> Dict[str, Any]:
    """
    创建一组唯一的测试地址数据。

    使用时间戳生成唯一地址，
    防止和数据库中已有地址重复。
    """

    # 获取毫秒级时间戳
    marker = str(int(time.time() * 1000))[-8:]

    # 返回新增地址请求体
    return {
        # 设置为非默认地址，避免影响原默认地址
        "defaultStatus": 0,

        # 测试收货人姓名
        "name": f"自动化测试用户{marker}",

        # 测试手机号
        "phoneNumber": "13800000000",

        # 邮政编码
        "postCode": "518000",

        # 省份
        "province": "广东省",

        # 城市
        "city": "深圳市",

        # 区域
        "region": "福田区",

        # 唯一详细地址，用于后续查找
        "detailAddress": f"自动化测试地址-{marker}",
    }


def add_address(
    headers: Dict[str, str],
    payload: Dict[str, Any],
) -> Dict[str, Any]:
    """
    新增收货地址。

    接口：

    POST /member/address/add
    """

    # 调用新增地址接口
    response = client.request(
        method="POST",
        url=f"{PORTAL_CONFIG['base_url']}/member/address/add",
        headers={
            **headers,
            "Content-Type": "application/json",
        },
        json=payload,
    )

    # 校验接口成功
    return assert_success(response)


def get_address_detail(
    headers: Dict[str, str],
    address_id: int,
) -> Dict[str, Any]:
    """
    查询收货地址详情。

    接口：

    GET /member/address/{id}
    """

    # 调用地址详情接口
    response = client.request(
        method="GET",
        url=f"{PORTAL_CONFIG['base_url']}/member/address/{address_id}",
        headers=headers,
    )

    # 校验接口成功
    body = assert_success(response)

    # 返回地址详情对象
    address = body.get("data")

    # 地址详情应该是字典
    assert isinstance(address, dict)

    return address


def update_address(
    headers: Dict[str, str],
    address_id: int,
    payload: Dict[str, Any],
) -> Dict[str, Any]:
    """
    修改收货地址。

    接口：

    POST /member/address/update/{id}
    """

    # 调用修改地址接口
    response = client.request(
        method="POST",
        url=f"{PORTAL_CONFIG['base_url']}/member/address/update/{address_id}",
        headers={
            **headers,
            "Content-Type": "application/json",
        },
        json=payload,
    )

    # 校验接口成功
    return assert_success(response)


def delete_address(
    headers: Dict[str, str],
    address_id: int,
) -> Dict[str, Any]:
    """
    删除收货地址。

    接口：

    POST /member/address/delete/{id}
    """

    # 调用删除地址接口
    response = client.request(
        method="POST",
        url=f"{PORTAL_CONFIG['base_url']}/member/address/delete/{address_id}",
        headers=headers,
    )

    # 校验接口成功
    return assert_success(response)


def create_test_address(
    headers: Dict[str, str],
) -> Dict[str, Any]:
    """
    创建测试地址并返回数据库中的地址对象。

    新增接口返回的 data 通常只是影响行数，
    不一定直接返回地址 ID。

    因此这里新增后重新查询地址列表，
    通过唯一 detailAddress 找到真正的地址对象。
    """

    # 创建唯一地址请求体
    payload = create_unique_address_payload()

    # 调用新增地址接口
    add_body = add_address(headers, payload)

    # 新增接口 data 通常为 1，表示新增成功
    assert add_body.get("data") is not None

    # 查询最新地址列表
    address_list = get_address_list(headers)

    # 通过唯一详细地址查找新地址
    address = find_address_by_detail(
        address_list,
        payload["detailAddress"],
    )

    # 必须能够找到刚刚新增的地址
    assert address is not None

    # 地址必须有 ID
    assert address.get("id") is not None

    return address


def safe_delete_test_address(
    headers: Dict[str, str],
    address_id: Optional[int],
) -> None:
    """
    安全删除测试地址。

    清理失败时不覆盖原始测试异常，
    而是将错误写入 Allure 附件。
    """

    # 如果没有地址 ID，说明新增可能没有成功
    if address_id is None:
        return

    try:
        # 查询当前地址列表
        address_list = get_address_list(headers)

        # 只在地址仍然存在时删除
        address_exists = any(
            address.get("id") == address_id
            for address in address_list
        )

        if address_exists:
            delete_address(headers, address_id)

    except Exception as error:
        # 将清理异常写入 Allure 报告
        allure.attach(
            str(error),
            name=f"测试地址清理失败，address_id={address_id}",
            attachment_type=allure.attachment_type.TEXT,
        )


def assert_unauthorized(response) -> Dict[str, Any]:
    """
    统一断言未登录访问失败。

    当前项目通常返回：

    HTTP 200
    code 401
    """

    # 当前项目一般 HTTP 仍然返回 200，
    # 兼容部分配置直接返回 401 的情况。
    assert response.status_code in (200, 401)

    # 解析响应内容
    body = parse_json(response)

    # 不能返回成功业务码
    assert body.get("code") != 200

    # 应该存在错误提示
    assert body.get("message")

    return body


# ============================================================
# 三、收货地址测试用例
# ============================================================

@allure.feature("商城前台")
@allure.story("收货地址")
@allure.title("登录用户查询收货地址列表成功")
@pytest.mark.portal
def test_address_list_with_valid_token():
    """
    验证登录用户可以查询自己的收货地址列表。

    接口：

    GET /member/address/list
    """

    # 获取有效 Token
    headers = get_auth_headers()

    # 查询收货地址列表
    address_list = get_address_list(headers)

    # 即使用户没有地址，也应该返回空列表
    assert isinstance(address_list, list)


@allure.feature("商城前台")
@allure.story("收货地址鉴权")
@allure.title("未登录查询收货地址列表失败")
@pytest.mark.portal
@pytest.mark.auth
def test_address_list_without_token():
    """
    验证未登录用户不能查询收货地址。

    接口：

    GET /member/address/list
    """

    # 不携带 Authorization 请求头
    response = client.request(
        method="GET",
        url=f"{PORTAL_CONFIG['base_url']}/member/address/list",
    )

    # 校验鉴权失败
    body = assert_unauthorized(response)

    # 当前项目通常是业务码 401
    assert body.get("code") == 401

    # 错误信息应该存在
    assert body.get("message")


@allure.feature("商城前台")
@allure.story("收货地址")
@allure.title("新增收货地址并查询详情成功")
@pytest.mark.portal
def test_address_add_and_detail():
    """
    验证新增收货地址后可以查询详情。

    接口：

    POST /member/address/add
    GET /member/address/{id}
    """

    # 获取有效 Token
    headers = get_auth_headers()

    # 保存地址 ID，方便 finally 清理
    address_id = None

    try:
        # 创建测试地址
        address = create_test_address(headers)

        # 获取测试地址 ID
        address_id = address["id"]

        # 查询地址详情
        detail = get_address_detail(headers, address_id)

        # 校验地址 ID
        assert detail.get("id") == address_id

        # 校验收货人姓名
        assert detail.get("name") == address.get("name")

        # 校验手机号
        assert detail.get("phoneNumber") == "13800000000"

        # 校验详细地址不为空
        assert detail.get("detailAddress")

        # 测试地址应该是非默认地址
        assert detail.get("defaultStatus") == 0

    finally:
        # 只清理本次创建的测试地址
        safe_delete_test_address(headers, address_id)


@allure.feature("商城前台")
@allure.story("收货地址")
@allure.title("修改收货地址并验证修改结果成功")
@pytest.mark.portal
def test_address_update_and_verify():
    """
    验证收货地址可以修改。

    接口：

    POST /member/address/update/{id}
    GET /member/address/{id}
    """

    # 获取有效 Token
    headers = get_auth_headers()

    # 保存测试地址 ID
    address_id = None

    try:
        # 创建测试地址
        original_address = create_test_address(headers)

        # 获取地址 ID
        address_id = original_address["id"]

        # 获取原始详细地址
        original_detail = original_address["detailAddress"]

        # 构造更新请求体
        update_payload = {
            "defaultStatus": 0,
            "name": original_address["name"],
            "phoneNumber": "13900000000",
            "postCode": "518000",
            "province": "广东省",
            "city": "深圳市",
            "region": "南山区",
            "detailAddress": f"{original_detail}-已更新",
        }

        # 调用修改地址接口
        update_body = update_address(
            headers=headers,
            address_id=address_id,
            payload=update_payload,
        )

        # 修改接口通常返回影响行数
        assert update_body.get("data") is not None

        # 查询修改后的地址详情
        updated_address = get_address_detail(headers, address_id)

        # 校验收货人姓名未被错误修改
        assert updated_address.get("name") == update_payload["name"]

        # 校验手机号已经修改
        assert updated_address.get("phoneNumber") == "13900000000"

        # 校验区域已经修改
        assert updated_address.get("region") == "南山区"

        # 校验详细地址已经修改
        assert updated_address.get("detailAddress") == update_payload[
            "detailAddress"
        ]

    finally:
        # 删除本次创建的测试地址
        safe_delete_test_address(headers, address_id)


@allure.feature("商城前台")
@allure.story("收货地址")
@allure.title("删除收货地址并验证删除结果成功")
@pytest.mark.portal
def test_address_delete_and_verify():
    """
    验证收货地址可以删除。

    接口：

    POST /member/address/delete/{id}
    GET /member/address/list
    """

    # 获取有效 Token
    headers = get_auth_headers()

    # 创建测试地址
    test_address = create_test_address(headers)

    # 获取地址 ID
    address_id = test_address["id"]

    # 删除收货地址
    delete_body = delete_address(headers, address_id)

    # 删除接口通常返回影响行数
    assert delete_body.get("data") is not None

    # 再次查询地址列表
    address_list = get_address_list(headers)

    # 被删除的地址不能继续出现在当前用户地址列表中
    assert all(
        address.get("id") != address_id
        for address in address_list
    )