"""
商品状态修改接口自动化测试。

测试范围：
1. 商品上下架状态；
2. 商品审核状态；
3. 商品推荐状态；
4. 商品新品状态；
5. 商品删除状态。

测试原则：
1. 先查询商品原始状态；
2. 修改为相反状态；
3. 查询商品，验证修改成功；
4. 无论测试成功还是失败，都恢复原始状态；
5. 再次查询商品，验证状态已经恢复。

测试商品：
商品 ID：26
商品货号：6946605

重要说明：
普通商品查询接口：
GET /product/list

该接口默认只查询 deleteStatus=0 的商品。

当商品被修改为 deleteStatus=1 后，
商品会从 /product/list 的结果中消失。

因此：
- 普通状态测试使用 /product/list；
- 删除状态测试使用 /product/updateInfo/{id}。
"""

from pathlib import Path
from typing import Any, Callable, Dict, Optional

import allure
import pytest
import yaml

from common.http_client import HttpClient


# ============================================================
# 一、读取项目配置
# ============================================================

# 获取接口自动化项目根目录：
# D:\ecommerce-test\automation\api
API_ROOT = Path(__file__).resolve().parents[1]

# 配置文件路径：
# D:\ecommerce-test\automation\api\config\config.yaml
CONFIG_FILE = API_ROOT / "config" / "config.yaml"


# 读取 YAML 配置文件
with CONFIG_FILE.open("r", encoding="utf-8") as file:
    CONFIG = yaml.safe_load(file)


# 读取后台管理系统配置
ADMIN_CONFIG = CONFIG["admin"]

# 创建 HTTP 请求客户端
client = HttpClient(
    timeout=CONFIG.get("timeout", 15)
)


# ============================================================
# 二、测试数据配置
# ============================================================

# 测试商品 ID
PRODUCT_ID = 26

# 测试商品货号
PRODUCT_SN = "6946605"


# ============================================================
# 三、管理员登录方法
# ============================================================

def login_admin() -> Dict[str, Any]:
    """
    使用管理员账号登录后台系统。

    登录接口：
    POST /admin/login

    当前账号：
    用户名：admin
    密码：macro123

    返回：
    登录接口完整响应数据。
    """

    # 发送管理员登录请求
    response = client.request(
        method="POST",
        url=f"{ADMIN_CONFIG['base_url']}/admin/login",
        headers={
            "Content-Type": "application/json",
        },
        json={
            "username": ADMIN_CONFIG["username"],
            "password": ADMIN_CONFIG["password"],
        },
    )

    # 校验 HTTP 状态码
    assert response.status_code == 200

    # 解析响应 JSON
    body = client.json_body(response)

    # 校验业务状态码
    assert body.get("code") == 200

    # 校验 data 字段
    assert body.get("data")

    # 校验 Token 字段
    assert body["data"].get("token")

    return body


@pytest.fixture(scope="module")
def admin_headers() -> Dict[str, str]:
    """
    获取后台接口鉴权请求头。

    当前测试文件只登录一次，
    所有测试共用本次登录获取的 Token。
    """

    # 登录后台
    login_body = login_admin()

    # 获取 Token 数据
    token_data = login_body["data"]

    # 获取 Token 前缀
    token_head = token_data.get(
        "tokenHead",
        "Bearer ",
    )

    # 获取具体 Token
    token = token_data["token"]

    # 组装请求头
    return {
        "Authorization": f"{token_head}{token}",
    }


# ============================================================
# 四、普通商品查询方法
# ============================================================

def get_product(
    headers: Dict[str, str],
) -> Dict[str, Any]:
    """
    使用普通商品列表接口查询商品。

    接口：
    GET /product/list

    注意：
    该接口默认只查询 deleteStatus=0 的商品。

    因此该方法适合：
    - publishStatus 测试；
    - verifyStatus 测试；
    - recommandStatus 测试；
    - newStatus 测试。

    不适合：
    - deleteStatus=1 的商品查询。
    """

    # 通过商品货号查询商品
    response = client.request(
        method="GET",
        url=f"{ADMIN_CONFIG['base_url']}/product/list",
        headers=headers,
        params={
            "productSn": PRODUCT_SN,
            "pageNum": 1,
            "pageSize": 5,
        },
    )

    # 校验 HTTP 状态码
    assert response.status_code == 200

    # 解析响应 JSON
    body = client.json_body(response)

    # 校验业务状态码
    assert body.get("code") == 200

    # 获取分页数据
    data = body.get("data")

    # 分页数据必须是字典
    assert isinstance(data, dict)

    # 获取商品列表
    product_list = data.get("list")

    # 商品列表必须是列表
    assert isinstance(product_list, list)

    # 商品货号正确时，必须能够查询到商品
    assert len(product_list) >= 1

    # 获取第一条商品数据
    product = product_list[0]

    # 校验商品 ID
    assert product.get("id") == PRODUCT_ID

    # 校验商品货号
    assert product.get("productSn") == PRODUCT_SN

    return product


# ============================================================
# 五、商品详情查询方法
# ============================================================

def get_product_update_info(
    headers: Dict[str, str],
) -> Dict[str, Any]:
    """
    使用商品编辑信息接口查询商品。

    接口：
    GET /product/updateInfo/{id}

    使用该接口的原因：
    当 deleteStatus=1 时，商品会从普通商品列表中消失，
    但是仍然可以通过商品 ID 查询商品编辑信息。

    因此删除状态测试必须使用该方法。
    """

    # 根据商品 ID 查询商品编辑信息
    response = client.request(
        method="GET",
        url=(
            f"{ADMIN_CONFIG['base_url']}"
            f"/product/updateInfo/{PRODUCT_ID}"
        ),
        headers=headers,
    )

    # 校验 HTTP 状态码
    assert response.status_code == 200

    # 解析响应 JSON
    body = client.json_body(response)

    # 校验业务状态码
    assert body.get("code") == 200

    # 获取商品详情
    product = body.get("data")

    # 商品详情必须是字典
    assert isinstance(product, dict)

    # 校验商品 ID
    assert product.get("id") == PRODUCT_ID

    # 校验商品货号
    assert product.get("productSn") == PRODUCT_SN

    return product


# ============================================================
# 六、商品状态修改方法
# ============================================================

def update_product_status(
    headers: Dict[str, str],
    endpoint: str,
    request_field: str,
    status: int,
    detail: Optional[str] = None,
) -> Dict[str, Any]:
    """
    通用商品状态修改方法。

    参数说明：

    headers：
        后台接口鉴权请求头。

    endpoint：
        商品状态修改接口路径。

    request_field：
        商品状态参数名称。

    status：
        修改后的状态值，只允许传 0 或 1。

    detail：
        审核状态修改时的审核说明。

    支持的接口：

    商品上下架：
    /product/update/publishStatus

    商品审核：
    /product/update/verifyStatus

    商品推荐：
    /product/update/recommendStatus

    商品新品：
    /product/update/newStatus

    商品删除：
    /product/update/deleteStatus
    """

    # 组装表单请求参数
    request_data = {
        # 商品 ID，单个商品也需要使用 ids 参数
        "ids": str(PRODUCT_ID),

        # 需要修改的状态值
        request_field: str(status),
    }

    # 审核状态接口需要额外传 detail
    if detail is not None:
        request_data["detail"] = detail

    # 发送状态修改请求
    response = client.request(
        method="POST",
        url=f"{ADMIN_CONFIG['base_url']}{endpoint}",
        headers={
            **headers,
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data=request_data,
    )

    # 校验 HTTP 状态码
    assert response.status_code == 200

    # 解析响应 JSON
    body = client.json_body(response)

    # 校验业务状态码
    assert body.get("code") == 200

    return body


# ============================================================
# 七、状态修改、验证和恢复公共方法
# ============================================================

def verify_status_update_and_restore(
    headers: Dict[str, str],
    response_field: str,
    endpoint: str,
    request_field: str,
    detail: Optional[str] = None,
    query_product: Callable[
        [Dict[str, str]],
        Dict[str, Any],
    ] = get_product,
):
    """
    通用商品状态修改、验证、恢复方法。

    执行步骤：

    1. 查询商品原始状态；
    2. 计算相反状态；
    3. 修改商品状态；
    4. 查询商品，验证修改成功；
    5. finally 中恢复原始状态；
    6. 再次查询商品，验证恢复成功。

    参数说明：

    response_field：
        查询商品返回结果中的字段名称。

    endpoint：
        修改状态的接口路径。

    request_field：
        修改状态时提交的参数名称。

    detail：
        审核状态接口需要的审核说明。

    query_product：
        商品查询方法。

        普通状态使用：
        get_product

        删除状态使用：
        get_product_update_info
    """

    # ========================================================
    # 第一步：查询商品原始状态
    # ========================================================

    original_product = query_product(headers)

    # 获取原始状态
    original_status = original_product.get(response_field)

    # 所有状态正常情况下只能是 0 或 1
    assert original_status in [0, 1]

    # ========================================================
    # 第二步：计算修改后的状态
    # ========================================================

    # 原始状态为 1 时修改为 0；
    # 原始状态为 0 时修改为 1。
    changed_status = (
        0 if original_status == 1 else 1
    )

    try:
        # ====================================================
        # 第三步：修改商品状态
        # ====================================================

        update_product_status(
            headers=headers,
            endpoint=endpoint,
            request_field=request_field,
            status=changed_status,
            detail=detail,
        )

        # ====================================================
        # 第四步：查询商品，验证修改成功
        # ====================================================

        changed_product = query_product(headers)

        # 校验商品状态已经修改成功
        assert changed_product.get(response_field) == changed_status

    finally:
        """
        无论测试成功还是失败，
        都必须恢复商品原始状态。

        普通状态接口不需要 detail；
        审核状态接口需要 detail。
        """

        # 恢复原始商品状态
        update_product_status(
            headers=headers,
            endpoint=endpoint,
            request_field=request_field,
            status=original_status,
            detail=(
                "自动化测试恢复原始审核状态"
                if detail is not None
                else None
            ),
        )

    # ========================================================
    # 第五步：查询商品，验证状态恢复成功
    # ========================================================

    restored_product = query_product(headers)

    # 校验恢复后的状态和原始状态一致
    assert restored_product.get(response_field) == original_status


# ============================================================
# 八、商品上下架状态测试
# ============================================================

@allure.feature("后台管理系统")
@allure.story("商品状态管理")
@allure.title("商品上下架状态修改并恢复成功")
@pytest.mark.admin
@pytest.mark.product
def test_product_publish_status_update_and_restore(
    admin_headers: Dict[str, str],
):
    """
    验证商品上下架状态修改和恢复。

    接口：
    POST /product/update/publishStatus

    状态：
    publishStatus=0：下架
    publishStatus=1：上架
    """

    verify_status_update_and_restore(
        headers=admin_headers,
        response_field="publishStatus",
        endpoint="/product/update/publishStatus",
        request_field="publishStatus",
    )


# ============================================================
# 九、商品审核状态测试
# ============================================================

@allure.feature("后台管理系统")
@allure.story("商品状态管理")
@allure.title("商品审核状态修改并恢复成功")
@pytest.mark.admin
@pytest.mark.product
def test_product_verify_status_update_and_restore(
    admin_headers: Dict[str, str],
):
    """
    验证商品审核状态修改和恢复。

    接口：
    POST /product/update/verifyStatus

    状态：
    verifyStatus=0：未审核
    verifyStatus=1：审核通过

    该接口必须传递 detail 参数。
    """

    verify_status_update_and_restore(
        headers=admin_headers,
        response_field="verifyStatus",
        endpoint="/product/update/verifyStatus",
        request_field="verifyStatus",
        detail="自动化测试审核状态变更",
    )


# ============================================================
# 十、商品推荐状态测试
# ============================================================

@allure.feature("后台管理系统")
@allure.story("商品状态管理")
@allure.title("商品推荐状态修改并恢复成功")
@pytest.mark.admin
@pytest.mark.product
def test_product_recommend_status_update_and_restore(
    admin_headers: Dict[str, str],
):
    """
    验证商品推荐状态修改和恢复。

    接口：
    POST /product/update/recommendStatus

    注意：

    接口请求参数名称：
    recommendStatus

    商品查询结果字段名称：
    recommandStatus

    这是项目原有字段命名差异，不能写反。
    """

    verify_status_update_and_restore(
        headers=admin_headers,

        # 查询商品时的字段名称
        response_field="recommandStatus",

        # 修改接口地址
        endpoint="/product/update/recommendStatus",

        # 修改接口参数名称
        request_field="recommendStatus",
    )


# ============================================================
# 十一、商品新品状态测试
# ============================================================

@allure.feature("后台管理系统")
@allure.story("商品状态管理")
@allure.title("商品新品状态修改并恢复成功")
@pytest.mark.admin
@pytest.mark.product
def test_product_new_status_update_and_restore(
    admin_headers: Dict[str, str],
):
    """
    验证商品新品状态修改和恢复。

    接口：
    POST /product/update/newStatus

    状态：
    newStatus=0：不是新品
    newStatus=1：新品
    """

    verify_status_update_and_restore(
        headers=admin_headers,
        response_field="newStatus",
        endpoint="/product/update/newStatus",
        request_field="newStatus",
    )


# ============================================================
# 十二、商品删除状态测试
# ============================================================

@allure.feature("后台管理系统")
@allure.story("商品状态管理")
@allure.title("商品删除状态修改并恢复成功")
@pytest.mark.admin
@pytest.mark.product
def test_product_delete_status_update_and_restore(
    admin_headers: Dict[str, str],
):
    """
    验证商品删除状态修改和恢复。

    接口：
    POST /product/update/deleteStatus

    状态：
    deleteStatus=0：未删除
    deleteStatus=1：已删除

    特别说明：

    商品设置 deleteStatus=1 后，
    /product/list 默认查询不到该商品。

    所以本用例必须使用：
    /product/updateInfo/{id}

    查询商品状态。
    """

    verify_status_update_and_restore(
        headers=admin_headers,

        # 查询商品返回的字段名
        response_field="deleteStatus",

        # 修改删除状态接口
        endpoint="/product/update/deleteStatus",

        # 请求参数名称
        request_field="deleteStatus",

        # 关键：删除状态必须使用 updateInfo 查询
        query_product=get_product_update_info,
    )