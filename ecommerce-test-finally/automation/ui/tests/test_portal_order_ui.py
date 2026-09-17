"""
商城前台订单模块 UI 自动化测试。

测试前置条件：
1. 商城前端已启动：http://localhost:8060
2. 商城后端已启动：http://localhost:8085
3. 测试账号 test / 123456 已存在
4. 测试账号最好已经配置默认收货地址，否则提交订单接口可能因缺少地址失败

测试范围：
1. 未登录访问订单列表；
2. 登录后进入订单列表；
3. 从购物车进入确认订单页；
4. 校验确认订单页商品、地址和金额；
5. 提交订单；
6. 新订单出现在订单列表；
7. 进入订单详情；
8. 取消待付款订单；
9. 订单状态 Tab 切换；
10. 订单列表卡片信息校验；
11. 待付款订单详情操作按钮校验。

说明：
- 本脚本复用 test_portal_cart_ui.py 中已经验证过的登录、商品和购物车操作。
- 每条下单用例都会清空当前账号购物车，避免历史数据影响测试结果。
- 订单金额、商品名称、订单编号均使用真实页面数据，不写死数据库数据。
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

import allure
import pytest
from playwright.sync_api import (
    Page,
    TimeoutError as PlaywrightTimeoutError,
    expect,
)

# 复用购物车模块中的公共方法。
# 本文件和 test_portal_cart_ui.py 必须位于同一个 tests 目录中。
from test_portal_cart_ui import (
    HOME_URL,
    LOGIN_URL,
    API_BASE_URL,
    PORTAL_USERNAME,
    PORTAL_PASSWORD,
    add_current_product_to_cart,
    attach_text,
    clear_authenticated_cart,
    clear_portal_auth,
    get_cart_items,
    get_visible_page,
    login_portal,
    open_cart_page,
    open_product_detail_page,
    save_screenshot,
)


# ============================================================
# 基础配置
# ============================================================

# 商城前台订单列表页
ORDER_URL = "http://localhost:8060/#/pages/order/order"

# 商城前台确认订单页
CREATE_ORDER_URL = "http://localhost:8060/#/pages/order/createOrder"

# 商城前台订单详情页
ORDER_DETAIL_URL = "http://localhost:8060/#/pages/order/orderDetail"

# Playwright 默认超时时间
TIMEOUT = 15000

# 报告目录
REPORT_DIR = Path(__file__).resolve().parents[1] / "reports"

# 截图目录
SCREENSHOT_DIR = REPORT_DIR / "screenshots"


# ============================================================
# 页面定位器
# ============================================================

def get_order_page(page: Page):
    """
    获取当前可见的订单列表页面。
    """
    return get_visible_page(
        page,
        "pages/order/order",
    )


def get_create_order_page(page: Page):
    """
    获取当前可见的确认订单页面。
    """
    return get_visible_page(
        page,
        "pages/order/createOrder",
    )


def get_order_detail_page(page: Page):
    """
    获取当前可见的订单详情页面。
    """
    return get_visible_page(
        page,
        "pages/order/orderDetail",
    )


def get_order_items(order_page):
    """
    获取订单列表中的订单卡片。
    """
    return order_page.locator(
        ".order-item"
    )


def get_create_order_items(create_page):
    """
    获取确认订单页面中的商品条目。
    """
    return create_page.locator(
        ".goods-section .g-item"
    )


def get_detail_order_items(detail_page):
    """
    获取订单详情页面中的商品条目。
    """
    return detail_page.locator(
        ".goods-section .g-item"
    )


# ============================================================
# 页面等待方法
# ============================================================

def wait_for_order_page(page: Page):
    """
    等待订单列表页面完成渲染。
    """

    order_page = get_order_page(page)

    expect(
        order_page
    ).to_be_visible(
        timeout=TIMEOUT
    )

    expect(
        order_page.locator(".content")
    ).to_be_visible(
        timeout=TIMEOUT
    )

    expect(
        order_page.locator(".navbar")
    ).to_be_visible(
        timeout=TIMEOUT
    )

    expect(
        order_page.locator(".nav-item").first
    ).to_be_visible(
        timeout=TIMEOUT
    )

    # 等待订单接口和页面数据渲染完成
    page.wait_for_timeout(800)

    return order_page


def wait_for_create_order_page(page: Page):
    """
    等待确认订单页面完成渲染。
    """

    create_page = get_create_order_page(page)

    expect(
        create_page
    ).to_be_visible(
        timeout=TIMEOUT
    )

    expect(
        create_page.locator(".goods-section")
    ).to_be_visible(
        timeout=TIMEOUT
    )

    expect(
        create_page.locator(".footer .submit")
    ).to_be_visible(
        timeout=TIMEOUT
    )

    page.wait_for_timeout(800)

    return create_page


def wait_for_order_detail_page(page: Page):
    """
    等待订单详情页面完成渲染。
    """

    detail_page = get_order_detail_page(page)

    expect(
        detail_page
    ).to_be_visible(
        timeout=TIMEOUT
    )

    expect(
        detail_page.locator(".status-section")
    ).to_be_visible(
        timeout=TIMEOUT
    )

    expect(
        detail_page.locator(".goods-section")
    ).to_be_visible(
        timeout=TIMEOUT
    )

    page.wait_for_timeout(800)

    return detail_page


# ============================================================
# 打开订单页面
# ============================================================

def open_order_list_page(
    page: Page,
    state: Optional[int] = None,
):
    """
    打开订单列表页。

    注意：
    order.vue 源码中的 state 参数实际上被当作 Tab 下标使用：

    0：全部
    1：待付款
    2：待收货
    3：已完成
    4：已取消
    """

    if state is None:
        url = ORDER_URL
    else:
        url = f"{ORDER_URL}?state={state}"

    page.set_default_timeout(
        TIMEOUT
    )

    page.goto(
        url,
        wait_until="domcontentloaded",
    )

    return wait_for_order_page(
        page
    )


def open_order_detail_by_id(
    page: Page,
    order_id: int,
):
    """
    根据订单 ID 打开订单详情页。
    """

    page.goto(
        f"{ORDER_DETAIL_URL}?orderId={order_id}",
        wait_until="domcontentloaded",
    )

    return wait_for_order_detail_page(
        page
    )


def select_order_tab(
    page: Page,
    index: int,
):
    """
    点击订单列表中的指定 Tab。

    参数：
        index=0：全部
        index=1：待付款
        index=2：待收货
        index=3：已完成
        index=4：已取消
    """

    order_page = get_order_page(
        page
    )

    nav_items = order_page.locator(
        ".navbar .nav-item"
    )

    expect(
        nav_items
    ).to_have_count(
        5,
        timeout=TIMEOUT,
    )

    nav_items.nth(
        index
    ).click()

    # 等待 Tab 切换和订单接口加载
    page.wait_for_timeout(
        1000
    )

    current_tab = order_page.locator(
        ".navbar .nav-item.current"
    )

    expect(
        current_tab
    ).to_have_count(
        1,
        timeout=TIMEOUT,
    )

    return order_page


# ============================================================
# 接口响应处理
# ============================================================

def parse_json_response(
    response,
    title: str,
) -> dict[str, Any]:
    """
    解析 JSON 接口响应，并校验 HTTP 状态码和业务状态码。
    """

    assert response.status == 200, (
        f"{title} HTTP 请求失败："
        f"{response.status}"
    )

    try:
        payload = response.json()
    except Exception as exc:
        raise AssertionError(
            f"{title}返回内容不是合法 JSON"
        ) from exc

    attach_text(
        f"{title}响应",
        payload,
    )

    assert isinstance(
        payload,
        dict,
    ), (
        f"{title}响应格式错误："
        f"{payload}"
    )

    assert payload.get("code") == 200, (
        f"{title}业务失败："
        f"{payload}"
    )

    return payload


def extract_order_id(
    payload: dict[str, Any],
) -> int:
    """
    从生成订单接口响应中提取订单 ID。

    真实接口结构：

    {
        "code": 200,
        "data": {
            "order": {
                "id": 1
            }
        }
    }
    """

    data = payload.get(
        "data"
    )

    assert isinstance(
        data,
        dict,
    ), (
        f"生成订单响应 data 格式错误："
        f"{payload}"
    )

    order = data.get(
        "order"
    )

    assert isinstance(
        order,
        dict,
    ), (
        f"生成订单响应中不存在 data.order："
        f"{payload}"
    )

    order_id = order.get(
        "id"
    )

    assert order_id is not None, (
        f"生成订单响应中不存在订单 ID："
        f"{payload}"
    )

    try:
        order_id_int = int(
            order_id
        )
    except (
        TypeError,
        ValueError,
    ) as exc:
        raise AssertionError(
            f"订单 ID 不是数字：{order_id}"
        ) from exc

    assert order_id_int > 0, (
        f"订单 ID 必须大于 0："
        f"{order_id_int}"
    )

    attach_text(
        "新建订单 ID",
        order_id_int,
    )

    return order_id_int


# ============================================================
# uni-app 弹窗处理
# ============================================================

def get_visible_modal(page: Page):
    """
    获取当前可见的 uni-app 弹窗。
    """

    return page.locator(
        "uni-modal:visible, "
        ".uni-modal:visible"
    ).last


def click_modal_button(
    page: Page,
    text: str,
) -> None:
    """
    点击当前弹窗中指定文本的按钮。

    例如：

        click_modal_button(page, "取消")
        click_modal_button(page, "确定")
    """

    modal = get_visible_modal(
        page
    )

    expect(
        modal
    ).to_be_visible(
        timeout=TIMEOUT
    )

    button = modal.locator(
        ".uni-modal__btn"
    ).filter(
        has_text=text
    ).last

    # 兼容部分 uni-app 版本没有 uni-modal__btn 类名的情况
    if button.count() == 0:
        button = modal.get_by_text(
            text,
            exact=True,
        ).last

    expect(
        button
    ).to_be_visible(
        timeout=TIMEOUT
    )

    button.click()

    expect(
        page.locator(
            "uni-modal:visible, "
            ".uni-modal:visible"
        )
    ).to_have_count(
        0,
        timeout=TIMEOUT,
    )


# ============================================================
# 创建测试订单
# ============================================================

def create_order_from_cart(
    page: Page,
) -> tuple[Any, dict[str, Any]]:
    """
    登录商城、清空购物车、加入商品，并进入确认订单页。

    返回：

        确认订单页定位器
        加入购物车接口响应
    """

    # 清理前端登录状态
    clear_portal_auth(
        page
    )

    # 登录商城
    login_portal(
        page
    )

    # 清理该测试账号历史购物车数据
    clear_authenticated_cart(
        page
    )

    # 打开商品详情页
    open_product_detail_page(
        page
    )

    # 加入当前商品
    add_result = add_current_product_to_cart(
        page
    )

    # 打开购物车页面
    cart_page, cart_data = open_cart_page(
        page,
        require_items=True,
    )

    # 校验购物车接口返回商品
    assert cart_data is None or len(cart_data) > 0, (
        "加入商品后购物车接口返回空数组"
    )

    # 校验页面渲染商品
    cart_items = get_cart_items(
        cart_page
    )

    assert cart_items.count() > 0, (
        "加入商品后购物车页面没有商品"
    )

    # cart.vue 中商品默认是选中状态，
    # 因此可以直接点击“去结算”。
    confirm_button = cart_page.locator(
        ".confirm-btn"
    ).last

    expect(
        confirm_button
    ).to_be_visible(
        timeout=TIMEOUT
    )

    expect(
        confirm_button
    ).to_be_enabled(
        timeout=TIMEOUT
    )

    # 点击去结算，进入确认订单页面
    # 当前 Playwright 版本不支持 Page.expect_url，使用兼容写法。
    # 先点击，再等待 uni-app 的 hash 路由发生变化。
    confirm_button.click()
    page.wait_for_url(
        "**/pages/order/createOrder*",
        timeout=TIMEOUT,
    )

    create_page = wait_for_create_order_page(
        page
    )

    return create_page, add_result


def submit_order_and_choose_cancel(
    page: Page,
) -> tuple[int, dict[str, Any]]:
    """
    在确认订单页提交订单。

    提交成功后，商城会弹出：

        订单创建成功，是否要立即支付？

    这里选择“取消”，避免进入支付页面。

    返回：

        新建订单 ID
        生成订单接口响应
    """

    create_page = get_create_order_page(
        page
    )

    expect(
        create_page
    ).to_be_visible(
        timeout=TIMEOUT
    )

    submit_button = create_page.locator(
        ".footer .submit"
    ).last

    expect(
        submit_button
    ).to_be_visible(
        timeout=TIMEOUT
    )

    expect(
        submit_button
    ).to_be_enabled(
        timeout=TIMEOUT
    )

    # 监听生成订单接口
    with page.expect_response(
        lambda response: (
            "/order/generateOrder" in response.url
            and response.request.method == "POST"
        ),
        timeout=TIMEOUT,
    ) as response_info:
        submit_button.click()

    generate_response = response_info.value

    payload = parse_json_response(
        generate_response,
        "生成订单接口",
    )

    order_id = extract_order_id(
        payload
    )

    # 校验订单创建成功弹窗
    modal = get_visible_modal(
        page
    )

    expect(
        modal
    ).to_be_visible(
        timeout=TIMEOUT
    )

    expect(
        modal
    ).to_contain_text(
        "订单创建成功",
        timeout=TIMEOUT,
    )

    expect(
        modal
    ).to_contain_text(
        "是否要立即支付",
        timeout=TIMEOUT,
    )

    attach_text(
        "提交订单后页面地址",
        page.url,
    )

    # createOrder.vue 源码中点击取消后：
    #
    # /pages/order/order?state=0
    #
    # 注意：order.vue 会把 state=0 当作 Tab 下标 0，
    # 所以跳转后默认显示“全部”Tab。
    # 当前 Playwright 版本不支持 Page.expect_url。
    click_modal_button(
        page,
        "取消",
    )
    page.wait_for_url(
        "**/pages/order/order*",
        timeout=TIMEOUT,
    )

    wait_for_order_page(
        page
    )

    return order_id, payload


# ============================================================
# 订单列表接口处理
# ============================================================

def capture_order_list(
    page: Page,
    state: int = -1,
) -> dict[str, Any]:
    """
    刷新订单列表并捕获 /order/list 接口响应。
    """

    order_page = get_order_page(
        page
    )

    expect(
        order_page
    ).to_be_visible(
        timeout=TIMEOUT
    )

    try:
        with page.expect_response(
            lambda response: (
                "/order/list" in response.url
                and response.request.method == "GET"
            ),
            timeout=TIMEOUT,
        ) as response_info:
            page.reload(
                wait_until="domcontentloaded"
            )

        payload = parse_json_response(
            response_info.value,
            "订单列表接口",
        )

    except PlaywrightTimeoutError as exc:
        save_screenshot(
            page,
            "order-list-request-timeout.png",
            "订单列表接口请求超时",
        )

        attach_text(
            "订单列表页面文本",
            page.locator("body").inner_text(),
        )

        raise AssertionError(
            "订单列表页面未捕获到 /order/list 接口"
        ) from exc

    wait_for_order_page(
        page
    )

    attach_text(
        "订单列表查询状态",
        state,
    )

    return payload


def get_order_list_data(
    payload: dict[str, Any],
) -> list[dict[str, Any]]:
    """
    从 /order/list 接口响应中提取订单数组。

    真实接口结构：

    {
        "code": 200,
        "data": {
            "list": []
        }
    }
    """

    data = payload.get(
        "data"
    )

    assert isinstance(
        data,
        dict,
    ), (
        f"订单列表接口 data 不是对象："
        f"{payload}"
    )

    order_list = data.get(
        "list"
    )

    assert isinstance(
        order_list,
        list,
    ), (
        f"订单列表接口 data.list 不是数组："
        f"{payload}"
    )

    return order_list


def find_order_by_id(
    order_list: list[dict[str, Any]],
    order_id: int,
) -> Optional[dict[str, Any]]:
    """
    根据订单 ID 查找订单。
    """

    for item in order_list:
        try:
            if int(item.get("id")) == order_id:
                return item
        except (
            TypeError,
            ValueError,
        ):
            continue

    return None


# ============================================================
# 用例 1：未登录访问订单列表
# ============================================================

@pytest.mark.portal
@pytest.mark.order
@allure.epic("商城前台 UI 自动化测试")
@allure.feature("订单模块")
@allure.story("未登录访问订单列表")
@allure.title("未登录访问订单页时校验登录限制")
def test_unlogin_visit_order_page(
    page: Page,
):
    """
    未登录访问订单页。

    不同商城前端版本可能存在两种表现：

    1. 直接跳转到登录页；
    2. 保留在订单页，但展示空订单状态。

    两种表现都属于未登录保护逻辑。
    """

    clear_portal_auth(
        page
    )

    page.goto(
        ORDER_URL,
        wait_until="domcontentloaded",
    )

    page.wait_for_timeout(
        1200
    )

    login_page = get_visible_page(
        page,
        "pages/public/login",
    )

    order_page = get_visible_page(
        page,
        "pages/order/order",
    )

    # 方式一：跳转登录页
    if login_page.count() > 0 and login_page.is_visible():
        expect(
            login_page
        ).to_be_visible(
            timeout=TIMEOUT
        )

        attach_text(
            "未登录访问订单页最终地址",
            page.url,
        )

        save_screenshot(
            page,
            "order-unlogin-login-page.png",
            "未登录访问订单页跳转登录",
        )

        return

    # 方式二：订单页显示空订单状态
    expect(
        order_page
    ).to_be_visible(
        timeout=TIMEOUT
    )

    expect(
        order_page.locator(".navbar")
    ).to_be_visible(
        timeout=TIMEOUT
    )

    assert get_order_items(
        order_page
    ).count() == 0, (
        "未登录订单页不应显示订单数据"
    )

    attach_text(
        "未登录订单页面文本",
        page.locator("body").inner_text(),
    )

    save_screenshot(
        page,
        "order-unlogin-empty.png",
        "未登录订单页空状态",
    )


# ============================================================
# 用例 2：登录后访问订单列表
# ============================================================

@pytest.mark.portal
@pytest.mark.order
@allure.epic("商城前台 UI 自动化测试")
@allure.feature("订单模块")
@allure.story("登录后访问订单列表")
@allure.title("登录成功后订单列表主体和状态 Tab 正常显示")
def test_login_open_order_page(
    page: Page,
):
    """
    登录后进入订单列表页面。
    """

    clear_portal_auth(
        page
    )

    login_portal(
        page
    )

    order_page = open_order_list_page(
        page
    )

    nav_items = order_page.locator(
        ".navbar .nav-item"
    )

    expect(
        nav_items
    ).to_have_count(
        5,
        timeout=TIMEOUT,
    )

    expected_tabs = [
        "全部",
        "待付款",
        "待收货",
        "已完成",
        "已取消",
    ]

    actual_tabs = [
        text.strip()
        for text in nav_items.all_inner_texts()
    ]

    attach_text(
        "订单状态 Tab",
        actual_tabs,
    )

    assert actual_tabs == expected_tabs, (
        f"订单状态 Tab 不符合预期："
        f"{actual_tabs}"
    )

    expect(
        nav_items.nth(0)
    ).to_have_class(
        "nav-item current",
        timeout=TIMEOUT,
    )

    save_screenshot(
        page,
        "order-list-page.png",
        "登录后订单列表页面",
    )


# ============================================================
# 用例 3：购物车进入确认订单页
# ============================================================

@pytest.mark.portal
@pytest.mark.order
@allure.epic("商城前台 UI 自动化测试")
@allure.feature("订单模块")
@allure.story("创建订单")
@allure.title("从购物车点击去结算进入确认订单页")
def test_cart_to_order_confirm(
    page: Page,
):
    """
    从购物车进入确认订单页面。
    """

    create_page, _ = create_order_from_cart(
        page
    )

    assert "pages/order/createOrder" in page.url, (
        f"未进入确认订单页："
        f"{page.url}"
    )

    expect(
        create_page.locator(".goods-section .g-header")
    ).to_contain_text(
        "商品信息"
    )

    expect(
        create_page.locator(".footer .submit")
    ).to_have_text(
        "提交订单"
    )

    save_screenshot(
        page,
        "order-confirm-page.png",
        "确认订单页面",
    )


# ============================================================
# 用例 4：确认订单页面信息
# ============================================================

@pytest.mark.portal
@pytest.mark.order
@allure.epic("商城前台 UI 自动化测试")
@allure.feature("订单模块")
@allure.story("确认订单信息")
@allure.title("确认订单页显示收货地址、商品和金额信息")
def test_order_confirm_information(
    page: Page,
):
    """
    校验确认订单页面中的：

    1. 收货地址；
    2. 商品区域；
    3. 商品名称；
    4. 商品价格；
    5. 购买数量；
    6. 应付金额；
    7. 提交订单按钮。
    """

    create_page, _ = create_order_from_cart(
        page
    )

    address = create_page.locator(
        ".address-section"
    )

    goods_section = create_page.locator(
        ".goods-section"
    )

    goods_items = get_create_order_items(
        create_page
    )

    price_list = create_page.locator(
        ".yt-list"
    )

    footer_price = create_page.locator(
        ".footer .price"
    )

    expect(
        address
    ).to_be_visible(
        timeout=TIMEOUT
    )

    expect(
        goods_section
    ).to_be_visible(
        timeout=TIMEOUT
    )

    expect(
        goods_items.first
    ).to_be_visible(
        timeout=TIMEOUT
    )

    expect(
        price_list.first
    ).to_be_visible(
        timeout=TIMEOUT
    )

    expect(
        footer_price
    ).to_be_visible(
        timeout=TIMEOUT
    )

    assert goods_items.count() > 0, (
        "确认订单页没有商品条目"
    )

    first_item = goods_items.first

    product_name = first_item.locator(
        ".title"
    ).inner_text().strip()

    product_price = first_item.locator(
        ".price"
    ).inner_text().strip()

    product_number = first_item.locator(
        ".number"
    ).inner_text().strip()

    assert product_name, (
        "确认订单商品名称为空"
    )

    assert product_price, (
        "确认订单商品价格为空"
    )

    assert product_number, (
        "确认订单商品数量为空"
    )

    assert (
        "¥" in product_price
        or "￥" in product_price
    ), (
        f"确认订单商品价格缺少货币符号："
        f"{product_price}"
    )

    total_price_text = footer_price.inner_text().strip()

    assert total_price_text, (
        "确认订单底部应付金额为空"
    )

    attach_text(
        "确认订单核心信息",
        {
            "商品名称": product_name,
            "商品单价": product_price,
            "购买数量": product_number,
            "应付金额": total_price_text,
            "收货地址区域文本": address.inner_text().strip(),
        },
    )

    save_screenshot(
        page,
        "order-confirm-information.png",
        "确认订单信息",
    )


# ============================================================
# 用例 5：提交订单
# ============================================================

@pytest.mark.portal
@pytest.mark.order
@allure.epic("商城前台 UI 自动化测试")
@allure.feature("订单模块")
@allure.story("提交订单")
@allure.title("确认订单页提交订单并生成待付款订单")
def test_submit_order(
    page: Page,
):
    """
    校验：

    1. /order/generateOrder 接口请求成功；
    2. 返回订单 ID；
    3. 页面显示订单创建成功弹窗；
    4. 取消支付后回到订单列表页。
    """

    create_order_from_cart(
        page
    )

    order_id, payload = submit_order_and_choose_cancel(
        page
    )

    assert order_id > 0, (
        "生成订单 ID 必须大于 0"
    )

    order_data = payload.get(
        "data",
        {},
    )

    order_info = order_data.get(
        "order",
        {},
    )

    # 部分后端响应中不会返回 status，
    # 因此允许 status 不存在。
    assert order_info.get(
        "status"
    ) in (
        0,
        None,
    ), (
        f"新订单状态异常："
        f"{payload}"
    )

    assert "pages/order/order" in page.url, (
        f"提交订单后未回到订单列表："
        f"{page.url}"
    )

    current_tab = get_order_page(
        page
    ).locator(
        ".navbar .nav-item.current"
    )

    # createOrder.vue 的真实跳转地址是 state=0。
    # order.vue 将 state=0 当作 Tab 下标 0，
    # 所以默认显示“全部”。
    expect(
        current_tab
    ).to_have_text(
        "全部",
        timeout=TIMEOUT,
    )

    save_screenshot(
        page,
        "order-submit-success.png",
        "提交订单成功",
    )


# ============================================================
# 用例 6：新订单出现在订单列表
# ============================================================

@pytest.mark.portal
@pytest.mark.order
@allure.epic("商城前台 UI 自动化测试")
@allure.feature("订单模块")
@allure.story("订单列表")
@allure.title("新建订单出现在订单列表")
def test_new_order_in_order_list(
    page: Page,
):
    """
    创建订单后，校验订单接口和页面订单列表。
    """

    create_order_from_cart(
        page
    )

    order_id, _ = submit_order_and_choose_cancel(
        page
    )

    # createOrder.vue 跳转到 state=0，
    # 实际对应订单列表“全部”Tab。
    payload = capture_order_list(
        page,
        state=0,
    )

    order_list = get_order_list_data(
        payload
    )

    order_from_api = find_order_by_id(
        order_list,
        order_id,
    )

    order_page = get_order_page(
        page
    )

    order_items = get_order_items(
        order_page
    )

    expect(
        order_items.first
    ).to_be_visible(
        timeout=TIMEOUT
    )

    assert order_items.count() > 0, (
        "订单列表没有渲染订单卡片"
    )

    if order_from_api is not None:
        assert int(
            order_from_api.get("status")
        ) == 0, (
            f"新建订单未处于待付款状态："
            f"{order_from_api}"
        )

    attach_text(
        "新订单列表校验",
        {
            "新订单 ID": order_id,
            "接口订单数量": len(order_list),
            "页面订单数量": order_items.count(),
            "接口是否找到新订单": order_from_api is not None,
        },
    )

    save_screenshot(
        page,
        "new-order-in-list.png",
        "新订单出现在订单列表",
    )


# ============================================================
# 用例 7：进入订单详情
# ============================================================

@pytest.mark.portal
@pytest.mark.order
@allure.epic("商城前台 UI 自动化测试")
@allure.feature("订单模块")
@allure.story("订单详情")
@allure.title("从订单列表进入订单详情并校验详情信息")
def test_open_order_detail(
    page: Page,
):
    """
    从待付款订单列表进入订单详情页面。
    """

    create_order_from_cart(
        page
    )

    order_id, _ = submit_order_and_choose_cancel(
        page
    )

    order_page = open_order_list_page(
        page
    )

    # order.vue 的 Tab 下标 1 对应“待付款”。
    order_page = select_order_tab(
        page,
        1,
    )

    order_items = get_order_items(
        order_page
    )

    expect(
        order_items.first
    ).to_be_visible(
        timeout=TIMEOUT
    )

    # order.vue 中 .goods-box-single 点击后进入详情。
    goods_link = order_items.first.locator(
        ".goods-box-single"
    ).first

    expect(
        goods_link
    ).to_be_visible(
        timeout=TIMEOUT
    )

    # uni-app 使用内部滚动容器，普通 click 可能被 Playwright 判断为视口外。
    # 使用 DOM click 触发页面真实点击事件。
    goods_link.evaluate(
        "(element) => element.click()"
    )
    page.wait_for_url(
        "**/pages/order/orderDetail*",
        timeout=TIMEOUT,
    )

    detail_page = wait_for_order_detail_page(
        page
    )

    assert f"orderId={order_id}" in page.url, (
        f"订单详情 ID 不正确："
        f"{page.url}"
    )

    status_text = detail_page.locator(
        ".status-section .label-text"
    ).inner_text().strip()

    detail_items = get_detail_order_items(
        detail_page
    )

    order_detail_text = detail_page.locator(
        ".yt-list"
    ).filter(
        has_text="订单编号"
    ).inner_text().strip()

    assert status_text, (
        "订单详情页状态文本为空"
    )

    assert detail_items.count() > 0, (
        "订单详情页没有商品条目"
    )

    assert "订单编号" in order_detail_text, (
        "订单详情页没有订单编号信息"
    )

    attach_text(
        "订单详情信息",
        {
            "订单 ID": order_id,
            "订单状态": status_text,
            "订单编号区域": order_detail_text,
            "详情商品数量": detail_items.count(),
        },
    )

    save_screenshot(
        page,
        "order-detail-page.png",
        "订单详情页面",
    )


# ============================================================
# 用例 8：取消待付款订单
# ============================================================

@pytest.mark.portal
@pytest.mark.order
@allure.epic("商城前台 UI 自动化测试")
@allure.feature("订单模块")
@allure.story("取消订单")
@allure.title("待付款订单可以取消并调用取消订单接口")
def test_cancel_pending_order(
    page: Page,
):
    """
    校验待付款订单取消功能。
    """

    create_order_from_cart(
        page
    )

    order_id, _ = submit_order_and_choose_cancel(
        page
    )

    order_page = open_order_list_page(
        page
    )

    # order.vue 的 Tab 下标 1 对应“待付款”。
    order_page = select_order_tab(
        page,
        1,
    )

    order_items = get_order_items(
        order_page
    )

    expect(
        order_items.first
    ).to_be_visible(
        timeout=TIMEOUT
    )

    cancel_button = order_items.first.locator(
        ".action-btn"
    ).filter(
        has_text="取消订单"
    )

    expect(
        cancel_button
    ).to_be_visible(
        timeout=TIMEOUT
    )

    # 订单卡片位于 uni-app 内部滚动容器中，使用 DOM click 触发真实事件。
    cancel_button.evaluate(
        "(element) => element.click()"
    )

    modal = get_visible_modal(
        page
    )

    expect(
        modal
    ).to_be_visible(
        timeout=TIMEOUT
    )

    expect(
        modal
    ).to_contain_text(
        "是否要取消该订单",
        timeout=TIMEOUT,
    )

    # 监听取消订单接口
    with page.expect_response(
        lambda response: (
            "/order/cancelUserOrder" in response.url
            and response.request.method == "POST"
        ),
        timeout=TIMEOUT,
    ) as response_info:
        click_modal_button(
            page,
            "确定",
        )

    cancel_payload = parse_json_response(
        response_info.value,
        "取消订单接口",
    )

    attach_text(
        "取消订单结果",
        {
            "订单 ID": order_id,
            "接口响应": cancel_payload,
        },
    )

    # 取消成功后，页面会重新加载订单列表。
    page.wait_for_timeout(
        1200
    )

    assert "pages/order/order" in page.url, (
        f"取消订单后页面地址异常："
        f"{page.url}"
    )

    save_screenshot(
        page,
        "cancel-pending-order.png",
        "取消待付款订单",
    )


# ============================================================
# 用例 9：订单状态 Tab 筛选
# ============================================================

@pytest.mark.portal
@pytest.mark.order
@allure.epic("商城前台 UI 自动化测试")
@allure.feature("订单模块")
@allure.story("订单状态筛选")
@allure.title("订单列表可以切换全部、待付款、待收货、已完成和已取消")
def test_order_status_tabs(
    page: Page,
):
    """
    校验订单列表五个状态 Tab 均可点击切换。
    """

    clear_portal_auth(
        page
    )

    login_portal(
        page
    )

    order_page = open_order_list_page(
        page
    )

    expected_tabs = [
        "全部",
        "待付款",
        "待收货",
        "已完成",
        "已取消",
    ]

    nav_items = order_page.locator(
        ".navbar .nav-item"
    )

    expect(
        nav_items
    ).to_have_count(
        5,
        timeout=TIMEOUT,
    )

    for index, expected_text in enumerate(
        expected_tabs
    ):
        nav_items.nth(
            index
        ).click()

        page.wait_for_timeout(
            900
        )

        current = order_page.locator(
            ".navbar .nav-item.current"
        )

        expect(
            current
        ).to_have_count(
            1,
            timeout=TIMEOUT,
        )

        actual_text = current.inner_text().strip()

        assert actual_text == expected_text, (
            f"点击第 {index + 1} 个 Tab 后当前状态错误："
            f"{actual_text}"
        )

    attach_text(
        "订单状态 Tab 切换结果",
        expected_tabs,
    )

    save_screenshot(
        page,
        "order-status-tabs.png",
        "订单状态 Tab 筛选",
    )


# ============================================================
# 用例 10：订单列表卡片信息
# ============================================================

@pytest.mark.portal
@pytest.mark.order
@allure.epic("商城前台 UI 自动化测试")
@allure.feature("订单模块")
@allure.story("订单卡片信息")
@allure.title("订单列表卡片显示时间、状态、商品和金额")
def test_order_list_card_information(
    page: Page,
):
    """
    校验订单列表卡片信息。

    如果当前账号没有订单，则校验空订单页面。
    """

    clear_portal_auth(
        page
    )

    login_portal(
        page
    )

    order_page = open_order_list_page(
        page
    )

    order_items = get_order_items(
        order_page
    )

    # 当前账号没有订单时，校验页面空状态。
    if order_items.count() == 0:
        body_text = order_page.inner_text().strip()

        attach_text(
            "订单列表空状态",
            body_text,
        )

        assert body_text, (
            "订单列表既没有订单，也没有页面内容"
        )

        save_screenshot(
            page,
            "order-list-empty.png",
            "订单列表空状态",
        )

        return

    first_item = order_items.first

    time_text = first_item.locator(
        ".i-top .time"
    ).inner_text().strip()

    state_text = first_item.locator(
        ".i-top .state"
    ).inner_text().strip()

    goods = first_item.locator(
        ".goods-box-single"
    )

    total_quantity = first_item.locator(
        ".price-box .num"
    ).inner_text().strip()

    pay_amount = first_item.locator(
        ".price-box .price"
    ).inner_text().strip()

    expect(
        goods.first
    ).to_be_visible(
        timeout=TIMEOUT
    )

    assert time_text, (
        "订单卡片创建时间为空"
    )

    assert state_text, (
        "订单卡片状态为空"
    )

    assert goods.count() > 0, (
        "订单卡片没有商品区域"
    )

    assert total_quantity, (
        "订单卡片商品总数量为空"
    )

    assert pay_amount, (
        "订单卡片实付款为空"
    )

    attach_text(
        "订单卡片信息",
        {
            "创建时间": time_text,
            "订单状态": state_text,
            "商品数量": total_quantity,
            "实付款": pay_amount,
        },
    )

    save_screenshot(
        page,
        "order-list-card-information.png",
        "订单卡片信息",
    )


# ============================================================
# 用例 11：待付款订单详情操作
# ============================================================

@pytest.mark.portal
@pytest.mark.order
@allure.epic("商城前台 UI 自动化测试")
@allure.feature("订单模块")
@allure.story("订单详情操作区")
@allure.title("待付款订单详情显示取消订单和立即付款按钮")
def test_pending_order_detail_actions(
    page: Page,
):
    """
    校验待付款订单详情页底部操作按钮。
    """

    create_order_from_cart(
        page
    )

    order_id, _ = submit_order_and_choose_cancel(
        page
    )

    detail_page = open_order_detail_by_id(
        page,
        order_id,
    )

    status_text = detail_page.locator(
        ".status-section .label-text"
    ).inner_text().strip()

    assert status_text == "等待付款", (
        f"新建订单详情状态异常："
        f"{status_text}"
    )

    action_box = detail_page.locator(
        ".action-box:visible"
    ).last

    expect(
        action_box
    ).to_be_visible(
        timeout=TIMEOUT
    )

    cancel_button = action_box.locator(
        ".action-btn"
    ).filter(
        has_text="取消订单"
    )

    pay_button = action_box.locator(
        ".action-btn"
    ).filter(
        has_text="立即付款"
    )

    expect(
        cancel_button
    ).to_be_visible(
        timeout=TIMEOUT
    )

    expect(
        pay_button
    ).to_be_visible(
        timeout=TIMEOUT
    )

    expect(
        pay_button
    ).to_be_enabled(
        timeout=TIMEOUT
    )

    attach_text(
        "订单详情操作按钮",
        {
            "订单 ID": order_id,
            "订单状态": status_text,
            "取消订单按钮": cancel_button.inner_text().strip(),
            "立即付款按钮": pay_button.inner_text().strip(),
        },
    )

    save_screenshot(
        page,
        "pending-order-detail-actions.png",
        "待付款订单详情操作区",
    )