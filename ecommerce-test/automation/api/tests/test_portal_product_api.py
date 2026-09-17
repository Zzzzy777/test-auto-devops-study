"""
商城前台商品接口自动化测试。
测试范围：
1. 商品搜索；
2. 商品关键字搜索；
3. 商品分类树；
4. 商品详情；
5. 推荐品牌；
6. 品牌详情；
7. 品牌商品列表；
8. 商城首页内容。
注意：
商城前台的商品浏览接口不需要登录 Token，
所以本文件主要验证接口返回数据和业务字段。
"""
# 导入路径工具类，获取项目文件绝对路径
from pathlib import Path
# 类型注解，标记任意类型、字典类型，提升代码可读性
from typing import Any, Dict
# allure装饰器，用于生成可视化测试报告，标记模块、用例标题
import allure
# pytest自动化测试框架，用来管理和执行测试用例
import pytest
# yaml库，用于读取yaml格式的配置文件
import yaml
# 导入自定义封装的HTTP请求客户端，统一封装请求、解析响应
from common.http_client import HttpClient

# 获取当前脚本所在目录的上级目录，作为API自动化项目根目录
API_ROOT = Path(__file__).resolve().parents[1]
# 拼接config.yaml配置文件完整路径
CONFIG_FILE = API_ROOT / "config" / "config.yaml"

# 以utf-8编码打开yaml配置文件
with CONFIG_FILE.open("r", encoding="utf-8") as file:
    # 将yaml配置内容加载为Python字典对象
    CONFIG = yaml.safe_load(file)

# 取出配置文件中商城前台portal模块的配置信息（服务地址等）
PORTAL_CONFIG = CONFIG["portal"]
# 实例化HTTP请求客户端，超时时间读取配置，默认15秒
client = HttpClient(timeout=CONFIG.get("timeout", 15))


def assert_success(response) -> Dict[str, Any]:
    """
    统一校验接口响应成功。
    项目接口通常会返回：
    HTTP 200 + 业务 code 200
    """
    # 断言HTTP状态码为200，代表服务正常返回响应
    assert response.status_code == 200
    # 调用封装方法，将接口返回的json字符串转为python字典
    body = client.json_body(response)
    # 断言业务码等于200，代表业务逻辑执行成功
    assert body.get("code") == 200
    # 返回解析后的响应体，供调用方继续做字段断言
    return body


@allure.feature("商城前台")          # allure报告大模块：商城前台
@allure.story("商品搜索")            # allure报告子模块：商品搜索功能
@allure.title("商城商品默认分页搜索成功") # 测试用例标题，展示在allure报告页面
@pytest.mark.portal                  # 自定义标记：前台商城用例，可筛选执行
@pytest.mark.product                 # 自定义标记：商品相关模块用例
@pytest.mark.smoke                   # 冒烟用例标记，核心主流程用例
def test_portal_product_search_default():
    """
    验证商城前台商品默认分页搜索。
    请求：
    GET /product/search?pageNum=1&pageSize=5
    """
    # 发起GET请求，查询商品分页列表，不需要token
    response = client.request(
        method="GET",
        url=f"{PORTAL_CONFIG['base_url']}/product/search",
        params={
            "pageNum": 1,   # 当前页码
            "pageSize": 5,  # 每页展示条数
            "sort": 0,      # 排序参数，0代表默认排序
        },
    )
    # 调用通用成功断言函数，校验HTTP状态码和业务code
    body = assert_success(response)
    # 获取接口返回的业务分页数据
    data = body.get("data")
    # 校验data是字典类型
    assert isinstance(data, dict)
    # 校验返回的页码参数与请求参数一致
    assert data.get("pageNum") == 1
    assert data.get("pageSize") == 5
    # 校验商品总条数大于0，数据库存在商品数据
    assert data.get("total", 0) > 0
    # 获取商品列表
    product_list = data.get("list")
    # 校验商品列表是数组类型
    assert isinstance(product_list, list)
    # 校验当前页返回商品数量不超过每页5条限制
    assert len(product_list) <= 5


@allure.feature("商城前台")
@allure.story("商品搜索")
@allure.title("商城根据关键字搜索商品成功")
@pytest.mark.portal
@pytest.mark.product
def test_portal_product_search_by_keyword():
    """
    验证商城根据关键字搜索商品。
    使用 HUAWEI 作为关键字，避免命令行中文编码影响。
    """
    response = client.request(
        method="GET",
        url=f"{PORTAL_CONFIG['base_url']}/product/search",
        params={
            "keyword": "HUAWEI", # 搜索关键字
            "pageNum": 1,
            "pageSize": 5,
        },
    )
    body = assert_success(response)
    data = body.get("data")
    assert isinstance(data, dict)
    product_list = data.get("list")
    assert isinstance(product_list, list)
    # 校验关键字搜索至少返回一条商品
    assert len(product_list) >= 1
    # 校验结果列表中存在名称包含HUAWEI的商品，转大写忽略大小写匹配
    assert any(
        "HUAWEI" in product.get("name", "").upper()
        for product in product_list
    )


@allure.feature("商城前台")
@allure.story("商品分类")
@allure.title("查询商城商品分类树成功")
@pytest.mark.portal
@pytest.mark.product
def test_portal_product_category_tree():
    """
    验证商城前台商品分类树接口。
    """
    # GET请求获取商品分类树，无需鉴权
    response = client.request(
        method="GET",
        url=f"{PORTAL_CONFIG['base_url']}/product/categoryTreeList",
    )
    body = assert_success(response)
    category_list = body.get("data")
    # 分类树返回数组结构
    assert isinstance(category_list, list)
    # 至少存在一个一级分类
    assert len(category_list) >= 1
    # 校验至少有一个分类包含子分类children数组
    assert any(
        isinstance(category.get("children"), list)
        for category in category_list
    )


@allure.feature("商城前台")
@allure.story("商品详情")
@allure.title("查询商品详情成功")
@pytest.mark.portal
@pytest.mark.product
def test_portal_product_detail():
    """
    验证商品详情接口。
    当前测试商品：
    商品 ID：26
    商品货号：6946605
    """
    response = client.request(
        method="GET",
        url=f"{PORTAL_CONFIG['base_url']}/product/detail/26", # 路径传参，商品ID=26
    )
    body = assert_success(response)
    data = body.get("data")
    assert isinstance(data, dict)
    # 获取商品对象
    product = data.get("product")
    assert isinstance(product, dict)
    # 校验返回商品ID与请求一致
    assert product.get("id") == 26
    # 校验商品货号
    assert product.get("productSn") == "6946605"
    # 校验商品名称不为空
    assert product.get("name")


@allure.feature("商城前台")
@allure.story("品牌浏览")
@allure.title("查询推荐品牌成功")
@pytest.mark.portal
@pytest.mark.product
def test_portal_brand_recommend_list():
    """
    验证商城推荐品牌列表。
    """
    response = client.request(
        method="GET",
        url=f"{PORTAL_CONFIG['base_url']}/brand/recommendList",
        params={
            "pageNum": 1,
            "pageSize": 6,
        },
    )
    body = assert_success(response)
    brand_list = body.get("data")
    # 推荐品牌接口直接返回品牌数组
    assert isinstance(brand_list, list)
    # 至少存在一条推荐品牌
    assert len(brand_list) >= 1
    # 取第一个品牌，校验id和name字段存在
    first_brand = brand_list[0]
    assert first_brand.get("id") is not None
    assert first_brand.get("name")


@allure.feature("商城前台")
@allure.story("品牌浏览")
@allure.title("查询品牌详情成功")
@pytest.mark.portal
@pytest.mark.product
def test_portal_brand_detail():
    """
    验证品牌详情接口。
    当前测试品牌：
    brandId=3，对应华为品牌。
    """
    response = client.request(
        method="GET",
        url=f"{PORTAL_CONFIG['base_url']}/brand/detail/3", # 路径传参品牌ID=3
    )
    body = assert_success(response)
    brand = body.get("data")
    assert isinstance(brand, dict)
    # 校验品牌ID
    assert brand.get("id") == 3
    # 校验品牌名称为华为
    assert brand.get("name") == "华为"


@allure.feature("商城前台")
@allure.story("品牌浏览")
@allure.title("查询品牌下的商品成功")
@pytest.mark.portal
@pytest.mark.product
def test_portal_brand_product_list():
    """
    验证根据品牌查询商品。
    当前测试品牌：
    brandId=3。
    """
    response = client.request(
        method="GET",
        url=f"{PORTAL_CONFIG['base_url']}/brand/productList",
        params={
            "brandId": 3,
            "pageNum": 1,
            "pageSize": 6,
        },
    )
    body = assert_success(response)
    data = body.get("data")
    assert isinstance(data, dict)
    product_list = data.get("list")
    assert isinstance(product_list, list)
    # 该品牌下至少存在一条商品
    assert len(product_list) >= 1
    # 循环校验返回所有商品品牌ID都是3
    for product in product_list:
        assert product.get("brandId") == 3


@allure.feature("商城前台")
@allure.story("商城首页")
@allure.title("查询商城首页内容成功")
@pytest.mark.portal
@pytest.mark.product
def test_portal_home_content():
    """
    验证商城首页内容接口。
    """
    response = client.request(
        method="GET",
        url=f"{PORTAL_CONFIG['base_url']}/home/content",
    )
    body = assert_success(response)
    data = body.get("data")
    assert isinstance(data, dict)
    # 首页内容通常包含广告、推荐商品、热门商品等数据
    # 不强制要求每个数组都有数据，
    # 但需要校验字段结构存在。
    # 校验首页返回的各个模块字段都存在
    assert "advertiseList" in data
    assert "brandList" in data
    assert "hotProductList" in data
    assert "newProductList" in data
    assert "subjectList" in data
    # 校验每个模块字段类型都是数组
    assert isinstance(data["advertiseList"], list)
    assert isinstance(data["brandList"], list)
    assert isinstance(data["hotProductList"], list)
    assert isinstance(data["newProductList"], list)
    assert isinstance(data["subjectList"], list)
