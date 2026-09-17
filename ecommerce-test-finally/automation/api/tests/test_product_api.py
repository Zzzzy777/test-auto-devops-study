"""
商品接口自动化测试。
测试范围：
1. 商品分页查询；
2. 根据商品货号查询；
3. 根据商品分类查询；
4. 根据商品品牌查询；
5. 根据关键字查询商品；
6. 查询商品分类及子分类；
7. 查询品牌列表。
说明：
- 后台商品接口服务地址为：http://localhost:8082；
- 所有商品管理接口都需要后台管理员 Token；
- 登录失败或鉴权失败时，接口可能返回 HTTP 200，
  因此测试中必须同时校验 HTTP 状态码和业务 code。
"""
# 导入路径处理模块，获取项目文件绝对路径
from pathlib import Path
# 类型注解，标记任意类型、字典类型，提升代码可读性
from typing import Any, Dict
# allure装饰器，用于生成allure可视化测试报告
import allure
# pytest测试框架，用于管理、执行测试用例
import pytest
# yaml库，读取yaml格式配置文件
import yaml
# 导入自定义封装的HTTP请求客户端，统一处理http请求
from common.http_client import HttpClient

# 获取当前脚本上级目录，定位API自动化项目根目录
# D:\ecommerce-test\automation\api
API_ROOT = Path(__file__).resolve().parents[1]
# 拼接配置文件config.yaml完整路径
CONFIG_FILE = API_ROOT / "config" / "config.yaml"

# 以utf-8编码打开yaml配置文件
with CONFIG_FILE.open("r", encoding="utf-8") as file:
    # 将yaml配置内容加载为Python字典
    CONFIG = yaml.safe_load(file)

# 获取配置文件中后台管理系统的配置信息（地址、账号密码）
ADMIN_CONFIG = CONFIG["admin"]
# 实例化HTTP客户端，超时时间读取配置，默认15秒
client = HttpClient(timeout=CONFIG.get("timeout", 15))


def login_admin() -> Dict[str, Any]:
    """
    使用管理员账号登录后台系统，获取 Token。
    当前项目账号：
    用户名：admin
    密码：macro123
    """
    # 发起POST登录请求
    response = client.request(
        method="POST",
        url=f"{ADMIN_CONFIG['base_url']}/admin/login",
        headers={
            "Content-Type": "application/json", # 请求体格式为JSON
        },
        json={
            "username": ADMIN_CONFIG["username"],
            "password": ADMIN_CONFIG["password"],
        },
    )
    # 断言HTTP状态码200，代表服务正常响应
    assert response.status_code == 200
    # 调用封装方法，把响应体转为字典
    body = client.json_body(response)
    # 断言业务码200，代表登录业务成功
    assert body.get("code") == 200
    # 断言返回data字段存在
    assert body.get("data")
    # 断言data内存在token字段
    assert body["data"].get("token")
    # 返回登录响应数据，供后续获取token
    return body


@pytest.fixture(scope="module")
def admin_headers() -> Dict[str, str]:
    """
    模块级 Token Fixture。
    一个测试文件只登录一次，后面的商品接口测试
    共用本次登录获取的 Token，减少重复登录请求。
    scope="module"：当前py文件所有用例执行前只执行一次。
    """
    # 调用登录函数拿到登录返回结果
    login_body = login_admin()
    token_data = login_body["data"]
    # 获取token前缀，默认Bearer
    token_head = token_data.get("tokenHead", "Bearer ")
    token = token_data["token"]
    # 组装鉴权请求头并返回，所有商品用例直接复用
    return {
        "Authorization": f"{token_head}{token}",
    }


@allure.feature("后台管理系统")        # allure大模块
@allure.story("商品管理")              # allure子模块
@allure.title("商品分页查询成功")      # 用例标题，展示在报告
@pytest.mark.admin                     # 标记：后台相关用例
@pytest.mark.product                   # 标记：商品模块用例
@pytest.mark.smoke                     # 标记：冒烟核心用例
def test_product_list_pagination(admin_headers: Dict[str, str]):
    """
    验证商品分页查询功能。
    请求：
    GET /product/list?pageNum=2&pageSize=5
    """
    # 发起GET商品列表请求，传入鉴权头和分页参数
    response = client.request(
        method="GET",
        url=f"{ADMIN_CONFIG['base_url']}/product/list",
        headers=admin_headers, # 复用fixture里的token请求头
        params={
            "pageNum": 2,
            "pageSize": 5,
        },
    )
    # 校验HTTP状态码
    assert response.status_code == 200
    body = client.json_body(response)
    # 校验业务成功码
    assert body.get("code") == 200
    # 获取返回的业务数据
    data = body.get("data")
    # 校验data是字典类型
    assert isinstance(data, dict)
    # 校验返回的页码和请求传入页码一致
    assert data.get("pageNum") == 2
    assert data.get("pageSize") == 5
    # 校验总条数大于0，说明有商品数据
    assert data.get("total", 0) > 0
    # 校验商品列表是数组
    assert isinstance(data.get("list"), list)
    # 当前页返回条目不能超过每页5条限制
    assert len(data["list"]) <= 5


@allure.feature("后台管理系统")
@allure.story("商品管理")
@allure.title("根据商品货号查询商品成功")
@pytest.mark.admin
@pytest.mark.product
def test_product_list_by_product_sn(admin_headers: Dict[str, str]):
    """
    验证根据商品货号查询商品。
    当前测试数据中的商品货号：
    6946605
    """
    response = client.request(
        method="GET",
        url=f"{ADMIN_CONFIG['base_url']}/product/list",
        headers=admin_headers,
        params={
            "productSn": "6946605", # 按商品货号精确查询
        },
    )
    assert response.status_code == 200
    body = client.json_body(response)
    assert body.get("code") == 200
    data = body.get("data")
    assert isinstance(data, dict)
    product_list = data.get("list")
    assert isinstance(product_list, list)
    # 精确货号查询至少返回一条商品
    assert len(product_list) >= 1
    # 校验返回结果里存在货号等于6946605的商品
    assert any(
        product.get("productSn") == "6946605"
        for product in product_list
    )


@allure.feature("后台管理系统")
@allure.story("商品管理")
@allure.title("根据商品分类查询商品成功")
@pytest.mark.admin
@pytest.mark.product
def test_product_list_by_category(admin_headers: Dict[str, str]):
    """
    验证根据商品分类编号查询商品。
    当前测试数据中：
    productCategoryId=19 对应商品分类。
    """
    response = client.request(
        method="GET",
        url=f"{ADMIN_CONFIG['base_url']}/product/list",
        headers=admin_headers,
        params={
            "productCategoryId": 19, # 按分类ID筛选商品
        },
    )
    assert response.status_code == 200
    body = client.json_body(response)
    assert body.get("code") == 200
    data = body.get("data")
    assert isinstance(data, dict)
    product_list = data.get("list")
    assert isinstance(product_list, list)
    # 该分类下至少存在一条商品
    assert len(product_list) >= 1
    # 循环校验返回所有商品分类ID都是19
    for product in product_list:
        assert product.get("productCategoryId") == 19


@allure.feature("后台管理系统")
@allure.story("商品管理")
@allure.title("根据品牌查询商品成功")
@pytest.mark.admin
@pytest.mark.product
def test_product_list_by_brand(admin_headers: Dict[str, str]):
    """
    验证根据品牌编号查询商品。
    当前测试数据中：
    brandId=3 对应华为品牌。
    """
    response = client.request(
        method="GET",
        url=f"{ADMIN_CONFIG['base_url']}/product/list",
        headers=admin_headers,
        params={
            "brandId": 3, # 按品牌ID筛选商品
        },
    )
    assert response.status_code == 200
    body = client.json_body(response)
    assert body.get("code") == 200
    data = body.get("data")
    assert isinstance(data, dict)
    product_list = data.get("list")
    assert isinstance(product_list, list)
    # 该品牌下至少存在一条商品
    assert len(product_list) >= 1
    # 校验返回商品品牌ID全部等于3
    for product in product_list:
        assert product.get("brandId") == 3


@allure.feature("后台管理系统")
@allure.story("商品管理")
@allure.title("根据关键字查询商品成功")
@pytest.mark.admin
@pytest.mark.product
def test_product_simple_list_by_keyword(admin_headers: Dict[str, str]):
    """
    验证根据关键字查询商品。
    使用 HUAWEI 作为关键字，
    避免中文编码对命令行执行造成影响。
    """
    response = client.request(
        method="GET",
        url=f"{ADMIN_CONFIG['base_url']}/product/simpleList",
        headers=admin_headers,
        params={
            "keyword": "HUAWEI", # 关键字模糊搜索
        },
    )
    assert response.status_code == 200
    body = client.json_body(response)
    assert body.get("code") == 200
    product_list = body.get("data")
    # simpleList接口直接返回商品数组，不是带分页对象
    assert isinstance(product_list, list)
    # 至少查询到一条商品
    assert len(product_list) >= 1
    # 判断列表中存在名称包含HUAWEI的商品（转大写匹配，忽略大小写）
    assert any(
        "HUAWEI" in product.get("name", "").upper()
        for product in product_list
    )


@allure.feature("后台管理系统")
@allure.story("商品分类管理")
@allure.title("查询商品分类及子分类成功")
@pytest.mark.admin
@pytest.mark.product
def test_product_category_list_with_children(
    admin_headers: Dict[str, str],
):
    """
    验证查询一级商品分类及其子分类。
    """
    response = client.request(
        method="GET",
        url=(
            f"{ADMIN_CONFIG['base_url']}"
            "/productCategory/list/withChildren"
        ),
        headers=admin_headers,
    )
    assert response.status_code == 200
    body = client.json_body(response)
    assert body.get("code") == 200
    category_list = body.get("data")
    # 返回分类数组
    assert isinstance(category_list, list)
    # 至少有一个一级分类
    assert len(category_list) >= 1
    # 判断至少有一个分类包含子分类children数组
    assert any(
        isinstance(category.get("children"), list)
        for category in category_list
    )


@allure.feature("后台管理系统")
@allure.story("品牌管理")
@allure.title("查询品牌列表成功")
@pytest.mark.admin
@pytest.mark.product
def test_brand_list_all(admin_headers: Dict[str, str]):
    """
    验证查询全部品牌列表。
    """
    response = client.request(
        method="GET",
        url=f"{ADMIN_CONFIG['base_url']}/brand/listAll",
        headers=admin_headers,
    )
    assert response.status_code == 200
    body = client.json_body(response)
    assert body.get("code") == 200
    brand_list = body.get("data")
    # 返回品牌数组
    assert isinstance(brand_list, list)
    # 至少存在一个品牌
    assert len(brand_list) >= 1
    # 获取第一个品牌，校验id和name字段存在
    first_brand = brand_list[0]
    assert first_brand.get("id") is not None
    assert first_brand.get("name")
