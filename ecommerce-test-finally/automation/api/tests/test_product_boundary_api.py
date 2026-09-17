"""
商品接口边界值和异常场景测试。
测试范围：
1. 后台商品分页 pageSize=1；
2. 后台商品查询超出最大页码；
3. 后台根据不存在的商品货号查询；
4. 后台根据不存在的关键字查询；
5. 商城商品搜索 pageSize=1；
6. 商城商品搜索超出最大页码；
7. 商城根据不存在的关键字搜索；
8. 商城根据不存在的品牌查询商品。
说明：
本系统很多接口即使查询不到数据，也会返回：
HTTP 200 + code 200 + 空列表。
因此查询不到数据不一定是接口错误，
测试应验证接口结构和空结果是否符合预期。
"""
# 导入路径处理模块，用于获取项目文件绝对路径
from pathlib import Path
# 类型注解，标记任意类型、字典类型，提升代码可读性
from typing import Any, Dict
# allure装饰器，用于生成可视化测试报告
import allure
# pytest自动化测试框架，管理用例、fixture
import pytest
# yaml库，读取yaml格式配置文件
import yaml
# 导入自定义封装HTTP客户端，统一发送请求、解析响应
from common.http_client import HttpClient

# 获取当前脚本上级目录，作为接口自动化项目根目录
API_ROOT = Path(__file__).resolve().parents[1]
# 拼接配置文件config.yaml完整路径
CONFIG_FILE = API_ROOT / "config" / "config.yaml"

# utf-8编码读取yaml配置文件
with CONFIG_FILE.open("r", encoding="utf-8") as file:
    CONFIG = yaml.safe_load(file)

# 读取后台管理、商城前台两组配置
ADMIN_CONFIG = CONFIG["admin"]
PORTAL_CONFIG = CONFIG["portal"]
# 实例化HTTP客户端，超时时间读取配置，默认15秒
client = HttpClient(timeout=CONFIG.get("timeout", 15))


def login_admin() -> Dict[str, Any]:
    """
    登录后台并获取管理员 Token。
    """
    # 发送POST登录请求，JSON格式传参
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
    # 校验HTTP状态码200
    assert response.status_code == 200
    # 解析响应json
    body = client.json_body(response)
    # 校验业务码200，登录业务成功
    assert body.get("code") == 200
    # 校验data数据存在
    assert body.get("data")
    # 校验返回token字段
    assert body["data"].get("token")
    # 返回登录完整响应数据
    return body


@pytest.fixture(scope="module")
def admin_headers() -> Dict[str, str]:
    """
    当前测试模块只登录一次。
    后续后台商品测试共用同一个 Token。
    scope="module"：当前py文件所有用例执行前仅执行一次。
    """
    # 调用登录函数拿到token信息
    login_body = login_admin()
    token_data = login_body["data"]
    # 获取token前缀，默认Bearer
    token_head = token_data.get("tokenHead", "Bearer ")
    token = token_data["token"]
    # 组装鉴权请求头，供后台接口使用
    return {
        "Authorization": f"{token_head}{token}",
    }


def assert_success(response) -> Dict[str, Any]:
    """
    统一校验请求成功。
    项目接口正常返回通常为：
    HTTP 200 + code 200
    """
    # 校验HTTP响应状态码
    assert response.status_code == 200
    # 解析json响应体
    body = client.json_body(response)
    # 校验业务成功码
    assert body.get("code") == 200
    # 返回解析后的body，供后续字段断言
    return body


@allure.feature("后台管理系统")
@allure.story("商品分页")
@allure.title("商品分页 pageSize 为 1 时查询成功")
@pytest.mark.admin
@pytest.mark.product
def test_admin_product_page_size_one(admin_headers: Dict[str, str]):
    """
    验证 pageSize=1 时接口可以正常分页。属于边界值测试。
    """
    response = client.request(
        method="GET",
        url=f"{ADMIN_CONFIG['base_url']}/product/list",
        headers=admin_headers,
        params={
            "pageNum": 1,
            "pageSize": 1, # 边界：每页只查询1条
        },
    )
    body = assert_success(response)
    data = body.get("data")
    assert isinstance(data, dict)
    # 校验回传分页参数和入参一致
    assert data.get("pageNum") == 1
    assert data.get("pageSize") == 1
    # 总数据量大于0
    assert data.get("total", 0) > 0
    product_list = data.get("list")
    assert isinstance(product_list, list)
    # 返回结果不能超过1条
    assert len(product_list) <= 1


@allure.feature("后台管理系统")
@allure.story("商品分页")
@allure.title("商品查询超出最大页码时返回空列表")
@pytest.mark.admin
@pytest.mark.product
def test_admin_product_page_num_out_of_range(
    admin_headers: Dict[str, str],
):
    """
    验证查询第 999 页时接口返回空列表。
    这属于正常的无数据分页场景，
    不应出现服务异常。
    """
    response = client.request(
        method="GET",
        url=f"{ADMIN_CONFIG['base_url']}/product/list",
        headers=admin_headers,
        params={
            "pageNum": 999, # 超大页码，超出数据总量
            "pageSize": 5,
        },
    )
    body = assert_success(response)
    data = body.get("data")
    assert isinstance(data, dict)
    # 校验分页参数原样返回
    assert data.get("pageNum") == 999
    assert data.get("pageSize") == 5
    # total >=0，允许为0
    assert data.get("total", 0) >= 0
    # 超出范围，商品列表为空数组
    assert data.get("list") == []


@allure.feature("后台管理系统")
@allure.story("商品查询")
@allure.title("根据不存在的商品货号查询返回空列表")
@pytest.mark.admin
@pytest.mark.product
def test_admin_product_sn_not_exist(admin_headers: Dict[str, str]):
    """
    验证根据不存在的商品货号查询时返回空列表。异常场景测试
    """
    response = client.request(
        method="GET",
        url=f"{ADMIN_CONFIG['base_url']}/product/list",
        headers=admin_headers,
        params={
            "productSn": "NOT_EXIST_PRODUCT_SN", # 不存在的货号
        },
    )
    body = assert_success(response)
    data = body.get("data")
    assert isinstance(data, dict)
    # 查询无数据，总条数等于0
    assert data.get("total") == 0
    assert data.get("list") == []


@allure.feature("后台管理系统")
@allure.story("商品查询")
@allure.title("根据不存在的关键字查询返回空列表")
@pytest.mark.admin
@pytest.mark.product
def test_admin_product_keyword_not_exist(
    admin_headers: Dict[str, str],
):
    """
    验证后台根据不存在的关键字查询商品时返回空列表。异常场景
    """
    response = client.request(
        method="GET",
        url=f"{ADMIN_CONFIG['base_url']}/product/simpleList",
        headers=admin_headers,
        params={
            "keyword": "NOT_EXIST_KEYWORD", # 不存在关键字
        },
    )
    body = assert_success(response)
    product_list = body.get("data")
    assert isinstance(product_list, list)
    # 无匹配商品，返回空数组
    assert product_list == []


@allure.feature("商城前台")
@allure.story("商品搜索")
@allure.title("商城商品搜索 pageSize 为 1 时查询成功")
@pytest.mark.portal
@pytest.mark.product
def test_portal_product_search_page_size_one():
    """
    验证商城商品搜索 pageSize=1 时返回正常分页数据，边界值。
    前台浏览接口不需要token。
    """
    response = client.request(
        method="GET",
        url=f"{PORTAL_CONFIG['base_url']}/product/search",
        params={
            "pageNum": 1,
            "pageSize": 1, # 边界值，每页1条
            "sort": 0,
        },
    )
    body = assert_success(response)
    data = body.get("data")
    assert isinstance(data, dict)
    assert data.get("pageNum") == 1
    assert data.get("pageSize") == 1
    assert data.get("total", 0) > 0
    product_list = data.get("list")
    assert isinstance(product_list, list)
    assert len(product_list) <= 1


@allure.feature("商城前台")
@allure.story("商品搜索")
@allure.title("商城商品搜索超出最大页码时返回空列表")
@pytest.mark.portal
@pytest.mark.product
def test_portal_product_search_page_num_out_of_range():
    """
    验证商城商品搜索第 999 页时返回空列表，越界场景。
    """
    response = client.request(
        method="GET",
        url=f"{PORTAL_CONFIG['base_url']}/product/search",
        params={
            "pageNum": 999, # 超大页码
            "pageSize": 5,
        },
    )
    body = assert_success(response)
    data = body.get("data")
    assert isinstance(data, dict)
    assert data.get("pageNum") == 999
    assert data.get("pageSize") == 5
    # 无数据，列表为空
    assert data.get("list") == []


@allure.feature("商城前台")
@allure.story("商品搜索")
@allure.title("商城根据不存在的关键字搜索返回空列表")
@pytest.mark.portal
@pytest.mark.product
def test_portal_product_search_keyword_not_exist():
    """
    验证商城根据不存在的关键字搜索时返回空列表，异常场景。
    """
    response = client.request(
        method="GET",
        url=f"{PORTAL_CONFIG['base_url']}/product/search",
        params={
            "keyword": "NOT_EXIST_KEYWORD", # 不存在关键字
            "pageNum": 1,
            "pageSize": 5,
        },
    )
    body = assert_success(response)
    data = body.get("data")
    assert isinstance(data, dict)
    # 无匹配数据，total=0，空列表
    assert data.get("total") == 0
    assert data.get("list") == []


@allure.feature("商城前台")
@allure.story("品牌商品")
@allure.title("根据不存在的品牌查询商品返回空列表")
@pytest.mark.portal
@pytest.mark.product
def test_portal_brand_product_list_brand_not_exist():
    """
    验证根据不存在的品牌 ID 查询商品时返回空列表。
    使用一个数据库中不存在的品牌 ID：
    999999
    """
    response = client.request(
        method="GET",
        url=f"{PORTAL_CONFIG['base_url']}/brand/productList",
        params={
            "brandId": 999999, # 不存在品牌ID
            "pageNum": 1,
            "pageSize": 5,
        },
    )
    body = assert_success(response)
    data = body.get("data")
    assert isinstance(data, dict)
    # 没有该品牌商品，总条数0，列表为空
    assert data.get("total") == 0
    assert data.get("list") == []
