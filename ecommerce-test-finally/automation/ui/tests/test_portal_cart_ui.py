"""
商城前台购物车模块 UI 自动化测试。

测试范围：

1. 未登录访问购物车页面；
2. 未登录购物车显示“去登陆”；
3. 点击“去登陆”跳转到商城登录页面；
4. 未登录点击“加入购物车”显示登录提示；
5. 登录成功后添加商品到购物车；
6. 校验购物车商品信息；
7. 校验购物车数量控件；
8. 校验删除商品按钮；
9. 校验去结算按钮；
10. 生成 Allure 测试报告；
11. 保存关键步骤截图。

商城前台地址：

首页：
http://localhost:8060/#/

登录页：
http://localhost:8060/#/pages/public/login

购物车页：
http://localhost:8060/#/pages/cart/cart

商城业务后端：
http://localhost:8085

测试账号：

用户名：test
密码：123456
"""

import json
from pathlib import Path
from typing import Any, Optional

import allure
import pytest
from playwright.sync_api import (
    Page,
    TimeoutError as PlaywrightTimeoutError,
    expect,
)


# ============================================================
# 基础配置
# ============================================================

# 商城前台首页地址
HOME_URL = "http://localhost:8060/#/"

# 商城前台登录页地址
LOGIN_URL = "http://localhost:8060/#/pages/public/login"

# 商城前台购物车地址
CART_URL = "http://localhost:8060/#/pages/cart/cart"

# 商城业务后端地址
API_BASE_URL = "http://localhost:8085"

# 商城前台测试账号
PORTAL_USERNAME = "test"

# 商城前台测试密码
PORTAL_PASSWORD = "123456"

# 测试报告目录
REPORT_DIR = (
    Path(__file__).resolve().parents[1]
    / "reports"
)

# 截图目录
SCREENSHOT_DIR = REPORT_DIR / "screenshots"


# ============================================================
# 首页商品选择器
# ============================================================

"""
首页存在多种卡片：

1. 秒杀商品；
2. 热门商品；
3. 猜你喜欢商品；
4. 品牌制造商卡片。

品牌制造商卡片也可能使用 .guess-item，
所以要排除包含 .image-wrapper-brand 的卡片。
"""

PRODUCT_CARD_SELECTOR = (
    ".seckill-section .floor-item:visible, "
    ".hot-section .guess-item:visible, "
    ".guess-section .guess-item"
    ":not(:has(.image-wrapper-brand)):visible"
)


# ============================================================
# Allure 和截图辅助方法
# ============================================================

def attach_text(
    name: str,
    value: Any,
) -> None:
    """
    将文本信息写入 Allure 报告。

    参数：
        name：附件名称；
        value：附件内容。
    """

    allure.attach(
        str(value),
        name=name,
        attachment_type=allure.attachment_type.TEXT,
    )


def save_screenshot(
    page: Page,
    file_name: str,
    allure_name: str,
) -> None:
    """
    保存页面截图，并将截图添加到 Allure 报告。
    """

    # 确保截图目录存在
    SCREENSHOT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # 生成截图路径
    screenshot_path = SCREENSHOT_DIR / file_name

    # 保存截图
    page.screenshot(
        path=str(screenshot_path),
        full_page=True,
    )

    # 添加到 Allure 报告
    allure.attach(
        screenshot_path.read_bytes(),
        name=allure_name,
        attachment_type=allure.attachment_type.PNG,
    )


# ============================================================
# 浏览器登录状态处理
# ============================================================

def clear_portal_auth(page: Page) -> None:
    """
    清理商城前台登录状态。

    说明：

    每条用例使用独立的 Page，但浏览器上下文有可能保留
    localStorage 或 sessionStorage，所以测试开始前主动清理。

    必须先访问商城前台同源页面，
    才能操作 localhost:8060 下的 localStorage。
    """

    # 先访问商城首页，建立同源环境
    page.goto(
        HOME_URL,
        wait_until="domcontentloaded",
    )

    # 清理前端登录状态
    page.evaluate(
        """
        () => {
            localStorage.clear();
            sessionStorage.clear();
        }
        """
    )

    # 刷新页面，让前端重新进入未登录状态
    page.reload(
        wait_until="domcontentloaded",
    )

    # 等待前端状态稳定
    page.wait_for_timeout(500)


def clear_authenticated_cart(page: Page) -> None:
    """
    清理当前测试账号已有的购物车数据。

    为什么需要这个方法：

    购物车页面源码中会对每一条购物车记录执行：

        JSON.parse(item.productAttr)

    如果数据库中存在以前遗留的异常购物车数据，
    例如 productAttr 为空或不是合法 JSON，
    前端购物车页面可能会在加载过程中抛出异常，
    最终表现为：

        购物车接口看似请求成功；
        页面显示清空、¥0、去结算；
        但页面没有 .cart-item 商品节点。

    所以登录后添加商品的用例开始之前，
    先清理当前测试账号购物车，保证测试数据干净。
    """

    # 从商城前台 localStorage 中获取 token
    token = page.evaluate(
        "() => localStorage.getItem('token') || ''"
    )

    # 登录成功后必须存在 token
    assert token, (
        "登录成功后浏览器 localStorage 中没有 token"
    )

    # 使用当前登录 token 调用清空购物车接口
    clear_result = page.evaluate(
        """
        async ({ apiUrl, token }) => {
            const response = await fetch(
                `${apiUrl}/cart/clear`,
                {
                    method: 'POST',
                    headers: {
                        'source-client': 'miniapp',
                        'Authorization': token,
                    },
                }
            );

            return {
                status: response.status,
                body: await response.text(),
            };
        }
        """,
        {
            "apiUrl": API_BASE_URL,
            "token": token,
        },
    )

    # 将清空结果写入 Allure
    attach_text(
        "清空历史购物车结果",
        clear_result,
    )

    # 校验 HTTP 状态码
    assert clear_result["status"] == 200, (
        "清空购物车接口 HTTP 请求失败："
        f"{clear_result}"
    )

    # 解析接口返回内容
    try:
        result = json.loads(
            clear_result["body"]
        )
    except Exception as exc:
        raise AssertionError(
            "清空购物车接口返回内容不是合法 JSON："
            f"{clear_result}"
        ) from exc

    # 校验业务状态码
    assert result.get("code") == 200, (
        "清空购物车业务失败："
        f"{result}"
    )

    # 等待后端事务完成
    page.wait_for_timeout(500)


# ============================================================
# 页面定位器
# ============================================================

def get_visible_page(
    page: Page,
    page_name: str,
):
    """
    获取当前可见的 uni-app 页面。

    uni-app H5 页面中可能同时存在多个 uni-page，
    所以必须增加 :visible 条件。
    """

    return page.locator(
        f"uni-page[data-page='{page_name}']:visible"
    )


def get_home_page(page: Page):
    """
    获取当前可见的商城首页。
    """

    return get_visible_page(
        page,
        "pages/index/index",
    )


def get_login_page(page: Page):
    """
    获取当前可见的商城登录页。
    """

    return get_visible_page(
        page,
        "pages/public/login",
    )


def get_cart_page(page: Page):
    """
    获取当前可见的商城购物车页。
    """

    return get_visible_page(
        page,
        "pages/cart/cart",
    )


def get_product_detail_page(page: Page):
    """
    获取当前可见的商品详情页。
    """

    return get_visible_page(
        page,
        "pages/product/product",
    )


def get_real_product_items(page: Page):
    """
    获取首页真实商品卡片。

    排除品牌制造商卡片。
    """

    home_page = get_home_page(page)

    return home_page.locator(
        PRODUCT_CARD_SELECTOR
    )


# ============================================================
# 首页和商品详情页操作
# ============================================================

def open_home_page(page: Page):
    """
    打开商城首页，并等待商品列表加载完成。
    """

    # 设置 Playwright 默认超时时间
    page.set_default_timeout(15000)

    # 打开首页
    page.goto(
        HOME_URL,
        wait_until="domcontentloaded",
    )

    # 校验首页可见
    home_page = get_home_page(page)

    expect(home_page).to_be_visible(
        timeout=15000,
    )

    # 获取真实商品
    product_items = get_real_product_items(page)

    # 等待至少一个商品显示
    expect(
        product_items.first
    ).to_be_visible(
        timeout=15000,
    )

    # 校验商品数量
    assert product_items.count() > 0, (
        "商城首页没有加载出真实商品"
    )

    return home_page


def open_product_detail_page(page: Page):
    """
    从商城首页点击第一个真实商品，
    进入商品详情页。
    """

    # 打开首页
    open_home_page(page)

    # 获取真实商品
    product_items = get_real_product_items(page)

    # 记录商品信息到 Allure
    product_name = (
        product_items.first
        .inner_text()
        .strip()
    )

    attach_text(
        "本次测试商品信息",
        product_name,
    )

    # 点击第一个商品
    product_items.first.click()

    # 等待跳转到商品详情页
    page.wait_for_url(
        "**/pages/product/product*",
        timeout=15000,
    )

    # 获取商品详情页
    detail_page = get_product_detail_page(page)

    # 校验详情页可见
    expect(detail_page).to_be_visible(
        timeout=15000,
    )

    # 校验详情页主体可见
    detail_container = detail_page.locator(
        ".container"
    )

    expect(detail_container).to_be_visible(
        timeout=15000,
    )

    return detail_page


# ============================================================
# 登录相关操作
# ============================================================

def get_username_input(page: Page):
    """
    获取登录页用户名输入框。
    """

    login_page = get_login_page(page)

    return login_page.locator(
        "input[type='text']"
    )


def get_password_input(page: Page):
    """
    获取登录页密码输入框。
    """

    login_page = get_login_page(page)

    return login_page.locator(
        "input[type='password']"
    )


def get_login_button(page: Page):
    """
    获取登录按钮。

    uni-app H5 页面可能渲染为：

        <uni-button class="confirm-btn">

    也可能渲染为：

        <button class="confirm-btn">
    """

    login_page = get_login_page(page)

    return login_page.locator(
        "uni-button.confirm-btn, "
        "button.confirm-btn"
    ).last


def get_visible_login_modal(page: Page):
    """
    获取当前可见的登录提示弹窗。
    """

    return page.locator(
        "uni-modal:visible, "
        ".uni-modal:visible"
    ).last


def cancel_login_modal(page: Page) -> None:
    """
    点击登录提示弹窗中的“取消”按钮。
    """

    # 获取弹窗
    modal = get_visible_login_modal(page)

    # 校验弹窗显示
    expect(modal).to_be_visible(
        timeout=15000,
    )

    # 优先使用 uni-app 弹窗按钮类名
    cancel_button = modal.locator(
        ".uni-modal__btn"
    ).filter(
        has_text="取消"
    )

    # 如果当前版本没有对应类名，
    # 则使用文本定位。
    if cancel_button.count() == 0:
        cancel_button = modal.get_by_text(
            "取消",
            exact=True,
        )

    # 校验取消按钮可见
    expect(
        cancel_button.last
    ).to_be_visible(
        timeout=15000,
    )

    # 点击取消
    cancel_button.last.click()

    # 等待弹窗关闭
    expect(
        page.locator(
            "uni-modal:visible, "
            ".uni-modal:visible"
        )
    ).to_have_count(
        0,
        timeout=15000,
    )


def login_portal(page: Page) -> None:
    """
    登录商城前台。

    登录流程：

    1. 打开商城登录页面；
    2. 填写账号密码；
    3. 调用 /sso/login；
    4. 保存 token；
    5. 获取 /sso/info；
    6. 返回商城首页。
    """

    # 设置默认超时时间
    page.set_default_timeout(15000)

    # 打开登录页面
    page.goto(
        LOGIN_URL,
        wait_until="domcontentloaded",
    )

    # 获取登录页面
    login_page = get_login_page(page)

    # 校验登录页面可见
    expect(login_page).to_be_visible(
        timeout=15000,
    )

    # 获取输入框
    username_input = get_username_input(page)
    password_input = get_password_input(page)

    # 校验输入框可见
    expect(username_input).to_be_visible(
        timeout=15000,
    )

    expect(password_input).to_be_visible(
        timeout=15000,
    )

    # 填写用户名密码
    username_input.fill(
        PORTAL_USERNAME
    )

    password_input.fill(
        PORTAL_PASSWORD
    )

    # 获取登录按钮
    login_button = get_login_button(page)

    # 校验登录按钮
    expect(login_button).to_be_visible(
        timeout=15000,
    )

    expect(login_button).to_be_enabled(
        timeout=15000,
    )

    # 同时监听登录请求和登录响应
    with page.expect_request(
        lambda request: (
            "/sso/login" in request.url
            and request.method == "POST"
        ),
        timeout=15000,
    ) as request_info, page.expect_response(
        lambda response: (
            "/sso/login" in response.url
            and response.request.method == "POST"
        ),
        timeout=15000,
    ) as response_info:

        # 点击登录按钮，触发真实登录请求
        login_button.click()

    # 获取登录请求对象
    login_request = request_info.value

    # 获取登录响应对象
    login_response = response_info.value

    # 打印登录请求的真实信息
    print("\n================ 商城登录请求信息 ================")
    print(f"请求地址：{login_request.url}")
    print(f"请求方法：{login_request.method}")
    print(f"请求头：{login_request.all_headers()}")
    print(f"请求参数：{login_request.post_data}")
    print("====================================================\n")

    # 将请求参数写入 Allure 报告
    attach_text(
        "商城登录真实请求参数",
        (
            f"请求地址：{login_request.url}\n"
            f"请求方法：{login_request.method}\n"
            f"请求参数：{login_request.post_data}"
        ),
    )

    # 校验 HTTP 状态码
    assert login_response.status == 200, (
        "商城登录接口 HTTP 请求失败："
        f"{login_response.status}"
    )

    # 解析接口响应
    try:
        result = login_response.json()
        print("\n================ 商城登录响应信息 ================")
        print(result)
        print("data 内容：", result.get("data"))
        print("====================================================\n")
    except Exception as exc:
        raise AssertionError(
            "商城登录接口返回内容不是合法 JSON"
        ) from exc

    # 记录登录响应
    attach_text(
        "商城登录接口响应",
        result,
    )

    # 校验登录结果
    assert isinstance(result, dict), (
        f"商城登录接口响应格式错误：{result}"
    )

    assert result.get("code") == 200, (
        f"商城登录业务失败：{result}"
    )

    assert isinstance(
        result.get("data"),
        dict,
    ), (
        f"商城登录 token 不存在：{result}"
    )

    # 前端登录成功后会继续请求 /sso/info，
    # 并延迟约 1 秒返回上一页。
    page.wait_for_timeout(1800)

    # 登录成功后不应该停留在登录页面
    assert "pages/public/login" not in page.url, (
        "登录成功后仍然停留在登录页面，"
        f"当前地址：{page.url}"
    )

    # 登录后应该回到商城页面
    assert "#/" in page.url, (
        "登录成功后没有回到商城页面，"
        f"当前地址：{page.url}"
    )


# ============================================================
# 商品规格和加入购物车
# ============================================================

def ensure_product_spec_selected(page: Page) -> None:
    """
    确保商品详情页已经选择商品规格。

    商品详情页源码会默认选择每个规格组的第一项，
    但为了兼容部分商品没有默认规格的情况，
    如果没有检测到已选规格，就手动选择第一项。
    """

    # 获取详情页
    detail_page = get_product_detail_page(page)

    # 校验详情页可见
    expect(detail_page).to_be_visible(
        timeout=15000,
    )

    # 获取商品详情区域已选择的规格
    selected_specs = detail_page.locator(
        ".introduce-section .selected-text"
    )

    # 如果已经有已选规格，则不再处理
    if selected_specs.count() > 0:
        selected_texts = (
            selected_specs.all_inner_texts()
        )

        if any(
            text.strip()
            for text in selected_texts
        ):
            return

    # 获取“购买类型”规格行
    spec_row = detail_page.locator(
        ".c-row"
    ).filter(
        has_text="购买类型"
    ).first

    # 如果存在规格行，则点击打开规格弹窗
    if spec_row.count() > 0:
        spec_row.click()

    # 获取规格弹窗
    spec_popup = detail_page.locator(
        ".popup.spec.show:visible"
    )

    # 兼容部分页面没有 show 类的情况
    if spec_popup.count() == 0:
        spec_popup = detail_page.locator(
            ".popup.spec:visible"
        )

    # 校验规格弹窗显示
    expect(spec_popup.first).to_be_visible(
        timeout=5000,
    )

    # 获取第一个规格选项
    first_option = spec_popup.locator(
        ".attr-list .tit:visible"
    ).first

    # 校验规格选项可见
    expect(first_option).to_be_visible(
        timeout=5000,
    )

    # 点击第一个规格选项
    first_option.click()

    # 点击完成按钮
    done_button = spec_popup.locator(
        ".btn"
    ).filter(
        has_text="完成"
    )

    expect(done_button).to_be_visible(
        timeout=5000,
    )

    done_button.click()

    # 等待规格状态刷新
    page.wait_for_timeout(400)


def add_current_product_to_cart(page: Page) -> dict:
    """
    将当前商品加入购物车。

    返回：
        加入购物车接口返回的 JSON 数据。
    """

    # 获取商品详情页
    detail_page = get_product_detail_page(page)

    # 校验详情页可见
    expect(detail_page).to_be_visible(
        timeout=15000,
    )

    # 确保商品规格已选择
    ensure_product_spec_selected(page)

    # 获取加入购物车按钮
    add_cart_button = detail_page.locator(
        ".add-cart-btn"
    ).last

    # 校验按钮
    expect(add_cart_button).to_be_visible(
        timeout=15000,
    )

    expect(add_cart_button).to_be_enabled(
        timeout=15000,
    )

    # 监听加入购物车接口
    with page.expect_response(
        lambda response: (
            "/cart/add" in response.url
            and response.request.method == "POST"
        ),
        timeout=15000,
    ) as response_info:
        add_cart_button.click()

    # 获取接口响应
    add_cart_response = response_info.value

    # 记录接口基本信息
    attach_text(
        "加入购物车接口信息",
        (
            f"接口地址：{add_cart_response.url}\n"
            f"HTTP 状态码：{add_cart_response.status}"
        ),
    )

    # 校验 HTTP 状态码
    assert add_cart_response.status == 200, (
        "加入购物车接口 HTTP 请求失败："
        f"{add_cart_response.status}"
    )

    # 解析接口响应
    try:
        result = add_cart_response.json()
    except Exception as exc:
        raise AssertionError(
            "加入购物车接口返回内容不是合法 JSON"
        ) from exc

    # 记录接口响应
    attach_text(
        "加入购物车接口响应",
        result,
    )

    # 校验业务响应
    assert isinstance(result, dict), (
        f"加入购物车接口响应格式错误：{result}"
    )

    assert result.get("code") == 200, (
        f"加入购物车业务失败：{result}"
    )

    # 等待后端事务提交和前端提示完成
    page.wait_for_timeout(1200)

    return result


# ============================================================
# 购物车接口和页面等待
# ============================================================

def is_cart_list_response(response) -> bool:
    """
    判断是否为购物车列表接口。

    只匹配：

        GET /cart/list

    避免误匹配：

        POST /cart/add
    """

    return (
        "/cart/list" in response.url
        and response.request.method == "GET"
    )


def parse_cart_response(response) -> list[dict[str, Any]]:
    """
    解析 /cart/list 接口响应。

    正常结构：

    {
        "code": 200,
        "message": "操作成功",
        "data": []
    }
    """

    # 解析 JSON
    try:
        payload = response.json()
    except Exception as exc:
        raise AssertionError(
            "/cart/list 返回内容不是合法 JSON"
        ) from exc

    # 记录接口响应
    attach_text(
        "购物车列表接口响应",
        payload,
    )

    # 校验响应结构
    assert isinstance(payload, dict), (
        f"/cart/list 响应格式错误：{payload}"
    )

    # 校验业务状态码
    assert payload.get("code") == 200, (
        f"/cart/list 业务请求失败：{payload}"
    )

    # 获取商品列表
    data = payload.get("data")

    # data 必须是数组
    assert isinstance(data, list), (
        f"/cart/list 的 data 不是数组：{payload}"
    )

    return data


def wait_cart_list_request(
    page: Page,
) -> Optional[list[dict[str, Any]]]:
    """
    刷新购物车页面，并等待购物车列表接口。

    说明：

    登录状态下会请求 /cart/list；
    未登录状态下前端不会请求 /cart/list，
    所以未登录场景超时后返回 None 是正常的。
    """

    try:
        # 监听购物车列表接口
        with page.expect_response(
            is_cart_list_response,
            timeout=15000,
        ) as response_info:

            # 刷新页面，稳定触发购物车加载逻辑
            page.reload(
                wait_until="domcontentloaded"
            )

        # 解析接口响应
        return parse_cart_response(
            response_info.value
        )

    except PlaywrightTimeoutError:
        # 未登录时不会调用 /cart/list
        return None


def get_cart_items(cart_page):
    """
    获取购物车商品列表元素。
    """

    return cart_page.locator(
        ".cart-list .cart-item"
    )


def open_cart_page(
    page: Page,
    require_items: bool = False,
) -> tuple[Any, Optional[list[dict[str, Any]]]]:
    """
    打开购物车页面，并等待页面渲染完成。

    参数：

        page：
            Playwright 页面对象；

        require_items：
            是否要求购物车中必须存在商品。

    返回：

        (
            购物车页面定位器，
            /cart/list 接口返回的商品列表
        )
    """

    # 设置默认超时时间
    page.set_default_timeout(15000)

    # 打开购物车页面
    page.goto(
        CART_URL,
        wait_until="domcontentloaded",
    )

    # 获取购物车页面
    cart_page = get_cart_page(page)

    # 校验购物车页面可见
    expect(cart_page).to_be_visible(
        timeout=15000,
    )

    # 等待页面初步渲染
    page.wait_for_timeout(500)

    # 刷新页面并监听购物车接口
    cart_data = wait_cart_list_request(page)

    # 等待购物车页面出现以下两种状态之一：

    # 1. 商品列表：
    #    .cart-list .cart-item

    # 2. 空购物车：
    #    .empty

    # 不能直接使用 cart_items.first 做 expect，
    # 因为购物车为空时该定位器本身不存在。
    try:
        page.wait_for_function(
            """
            () => {
                const pages = Array.from(
                    document.querySelectorAll(
                        "uni-page[data-page='pages/cart/cart']"
                    )
                );

                return pages.some((cartPage) => {
                    const style = window.getComputedStyle(
                        cartPage
                    );

                    const visible =
                        style.display !== "none"
                        && style.visibility !== "hidden";

                    return visible && Boolean(
                        cartPage.querySelector(
                            ".cart-list .cart-item"
                        )
                        || cartPage.querySelector(
                            ".empty"
                        )
                    );
                });
            }
            """,
            timeout=10000,
        )

    except PlaywrightTimeoutError:
        # 页面既没有商品，也没有空状态
        save_screenshot(
            page,
            "cart-render-timeout.png",
            "购物车页面渲染超时",
        )

        attach_text(
            "购物车页面文本",
            page.locator("body").inner_text(),
        )

        raise AssertionError(
            "购物车页面没有渲染出商品列表或空购物车状态，"
            f"当前地址：{page.url}"
        )

    # 如果当前用例要求购物车必须存在商品
    if require_items:

        # 接口返回空数组，说明商品没有进入当前用户购物车
        if cart_data is not None and len(cart_data) == 0:

            save_screenshot(
                page,
                "cart-empty-after-add.png",
                "添加商品后购物车为空",
            )

            attach_text(
                "添加商品后购物车页面文本",
                page.locator("body").inner_text(),
            )

            raise AssertionError(
                "加入购物车接口返回成功，"
                "但 /cart/list 返回空数组。"
                "请检查登录 token、当前用户、"
                "数据库购物车记录和后端事务。"
            )

        # 获取页面商品元素
        cart_items = get_cart_items(
            cart_page
        )

        # 页面中没有商品
        if cart_items.count() == 0:

            save_screenshot(
                page,
                "cart-item-not-rendered.png",
                "购物车商品未渲染",
            )

            attach_text(
                "购物车页面文本",
                page.locator("body").inner_text(),
            )

            raise AssertionError(
                "购物车接口返回了商品，"
                "但是页面没有渲染 .cart-list .cart-item。"
                f"接口商品数量：{len(cart_data or [])}"
            )

    return cart_page, cart_data


def assert_cart_has_items(
    cart_page,
    cart_data: Optional[list[dict[str, Any]]],
) -> None:
    """
    统一校验接口商品和页面商品。

    注意：

    这里不能写成：

        assert len(cart_data) >= 0

    因为 >= 0 永远成立，会掩盖真正的业务问题。

    正确逻辑是：

        接口有商品；
        页面也渲染出商品。
    """

    # 校验接口数据
    assert cart_data is None or len(cart_data) > 0, (
        "购物车列表接口返回空数组，"
        "说明商品没有落入当前登录账号"
    )

    # 获取页面商品
    cart_items = get_cart_items(
        cart_page
    )

    # 校验页面商品数量
    page_count = cart_items.count()

    assert page_count > 0, (
        "购物车接口返回商品，"
        "但是页面没有找到 .cart-list .cart-item"
    )

    # 记录接口和页面数量
    attach_text(
        "购物车数量对比",
        (
            f"接口商品数量："
            f"{len(cart_data) if cart_data is not None else '未捕获'}\n"
            f"页面商品数量：{page_count}"
        ),
    )


# ============================================================
# 用例一：未登录访问购物车
# ============================================================

@pytest.mark.portal
@pytest.mark.cart
@allure.epic("商城前台 UI 自动化测试")
@allure.feature("购物车模块")
@allure.story("未登录访问购物车")
@allure.title("未登录访问购物车时显示去登陆入口")
@allure.severity(allure.severity_level.NORMAL)
def test_unlogin_visit_cart_page(page: Page):
    """
    测试场景：

    1. 清理登录状态；
    2. 打开购物车；
    3. 校验空购物车图片；
    4. 校验“空空如也”；
    5. 校验“去登陆”；
    6. 点击“去登陆”；
    7. 校验跳转到登录页面。
    """

    # 清理登录状态
    clear_portal_auth(page)

    # 打开购物车
    cart_page, _ = open_cart_page(page)

    # 获取空购物车区域
    empty_area = cart_page.locator(
        ".empty"
    )

    # 校验空购物车区域可见
    expect(empty_area).to_be_visible(
        timeout=15000,
    )

    # 校验空购物车图片
    empty_image = empty_area.locator(
        "uni-image, image, img"
    ).first

    expect(empty_image).to_be_visible(
        timeout=15000,
    )

    # 校验空购物车文字
    expect(empty_area).to_contain_text(
        "空空如也"
    )

    # 获取去登陆入口
    login_link = empty_area.get_by_text(
        "去登陆",
        exact=True,
    )

    # 校验去登陆入口可见
    expect(login_link).to_be_visible(
        timeout=15000,
    )

    # 保存截图
    save_screenshot(
        page,
        "portal-cart-unlogin.png",
        "未登录购物车页面",
    )

    # 点击去登陆
    login_link.click()

    # 等待跳转到登录页
    page.wait_for_url(
        "**/pages/public/login*",
        timeout=15000,
    )

    # 校验登录页显示
    expect(
        get_login_page(page)
    ).to_be_visible(
        timeout=15000,
    )


# ============================================================
# 用例二：未登录点击加入购物车
# ============================================================

@pytest.mark.portal
@pytest.mark.cart
@allure.epic("商城前台 UI 自动化测试")
@allure.feature("购物车模块")
@allure.story("未登录加入购物车")
@allure.title("未登录点击加入购物车时显示登录提示")
@allure.severity(allure.severity_level.NORMAL)
def test_unlogin_add_product_to_cart(page: Page):
    """
    测试场景：

    1. 未登录打开商城首页；
    2. 进入商品详情页；
    3. 点击加入购物车；
    4. 校验登录提示；
    5. 点击取消；
    6. 校验仍然停留在商品详情页。
    """

    # 清理登录状态
    clear_portal_auth(page)

    # 打开商品详情页
    open_product_detail_page(page)

    # 记录点击前页面地址
    before_url = page.url

    # 获取加入购物车按钮
    detail_page = get_product_detail_page(page)

    add_cart_button = detail_page.locator(
        ".add-cart-btn"
    ).last

    # 校验按钮可见
    expect(add_cart_button).to_be_visible(
        timeout=15000,
    )

    # 未登录点击后不会调用 /cart/add，
    # 而是弹出登录提示框。
    add_cart_button.click()

    # 获取登录提示弹窗
    modal = get_visible_login_modal(page)

    # 校验弹窗可见
    expect(modal).to_be_visible(
        timeout=15000,
    )

    # 校验弹窗提示内容
    expect(modal).to_contain_text(
        "你还没登录，是否要登录？"
    )

    # 记录弹窗内容
    attach_text(
        "未登录加入购物车提示",
        modal.inner_text(),
    )

    # 保存截图
    save_screenshot(
        page,
        "portal-cart-unlogin-add.png",
        "未登录加入购物车提示",
    )

    # 点击取消
    cancel_login_modal(page)

    # 校验取消后仍在商品详情页
    assert page.url == before_url, (
        "取消登录后页面地址发生变化："
        f"{page.url}"
    )

    expect(
        get_product_detail_page(page)
    ).to_be_visible(
        timeout=15000,
    )


# ============================================================
# 用例三：登录后加入购物车
# ============================================================

@pytest.mark.portal
@pytest.mark.cart
@allure.epic("商城前台 UI 自动化测试")
@allure.feature("购物车模块")
@allure.story("登录后加入购物车")
@allure.title("登录后可以将商品加入购物车")
@allure.severity(allure.severity_level.CRITICAL)
def test_login_add_product_to_cart(page: Page):
    """
    测试场景：

    1. 登录商城前台；
    2. 清理当前账号历史购物车；
    3. 打开商品详情页；
    4. 点击加入购物车；
    5. 校验 /cart/add 接口成功；
    6. 打开购物车；
    7. 校验 /cart/list 接口有商品；
    8. 校验页面显示商品。
    """

    # 清理浏览器登录状态
    clear_portal_auth(page)

    # 登录商城前台
    login_portal(page)

    # 清理历史购物车数据
    clear_authenticated_cart(page)

    # 打开商品详情页
    open_product_detail_page(page)

    # 加入购物车
    add_result = add_current_product_to_cart(page)

    # 记录加入结果
    attach_text(
        "添加购物车结果",
        add_result,
    )

    # 打开购物车并要求商品必须存在
    cart_page, cart_data = open_cart_page(
        page,
        require_items=True,
    )

    # 校验接口和页面均有商品
    assert_cart_has_items(
        cart_page,
        cart_data,
    )

    # 保存截图
    save_screenshot(
        page,
        "portal-cart-after-add.png",
        "商品加入购物车后页面",
    )


# ============================================================
# 用例四：购物车商品信息和操作按钮
# ============================================================

@pytest.mark.portal
@pytest.mark.cart
@allure.epic("商城前台 UI 自动化测试")
@allure.feature("购物车模块")
@allure.story("购物车商品信息")
@allure.title("校验购物车商品信息和操作按钮")
@allure.severity(allure.severity_level.NORMAL)
def test_cart_product_information_and_controls(
    page: Page,
):
    """
    测试场景：

    1. 登录商城；
    2. 清理当前账号历史购物车；
    3. 打开商品详情页；
    4. 加入商品到购物车；
    5. 校验商品名称；
    6. 校验商品规格；
    7. 校验商品价格；
    8. 校验商品数量；
    9. 校验商品选择框；
    10. 校验删除按钮；
    11. 校验去结算按钮。
    """

    # 清理浏览器登录状态
    clear_portal_auth(page)

    # 登录商城
    login_portal(page)

    # 清理历史购物车
    clear_authenticated_cart(page)

    # 打开商品详情页
    open_product_detail_page(page)

    # 加入购物车
    add_current_product_to_cart(page)

    # 打开购物车并要求必须有商品
    cart_page, cart_data = open_cart_page(
        page,
        require_items=True,
    )

    # 校验购物车接口和页面均有商品
    assert_cart_has_items(
        cart_page,
        cart_data,
    )

    # 获取第一个购物车商品
    first_cart_item = get_cart_items(
        cart_page
    ).first

    # ========================================================
    # 校验商品名称
    # ========================================================

    product_title = first_cart_item.locator(
        ".title"
    )

    expect(product_title).to_be_visible(
        timeout=15000,
    )

    product_title_text = (
        product_title
        .inner_text()
        .strip()
    )

    assert product_title_text, (
        "购物车商品名称为空"
    )

    attach_text(
        "购物车商品名称",
        product_title_text,
    )

    # ========================================================
    # 校验商品规格
    # ========================================================

    product_attribute = first_cart_item.locator(
        ".attr"
    )

    expect(product_attribute).to_be_visible(
        timeout=15000,
    )

    product_attribute_text = (
        product_attribute
        .inner_text()
        .strip()
    )

    # 规格内容有可能为空，
    # 因此这里只校验规格元素存在。
    attach_text(
        "购物车商品规格",
        product_attribute_text
        or "该商品没有规格信息",
    )

    # ========================================================
    # 校验商品价格
    # ========================================================

    product_price = first_cart_item.locator(
        ".price"
    )

    expect(product_price).to_be_visible(
        timeout=15000,
    )

    price_text = (
        product_price
        .inner_text()
        .strip()
    )

    assert price_text, (
        "购物车商品价格为空"
    )

    assert (
        "¥" in price_text
        or "￥" in price_text
    ), (
        "购物车商品价格没有货币符号，"
        f"实际内容：{price_text}"
    )

    attach_text(
        "购物车商品价格",
        price_text,
    )

    # ========================================================
    # 校验商品数量控件
    # ========================================================

    number_box = first_cart_item.locator(
        ".step"
    )

    expect(number_box).to_be_visible(
        timeout=15000,
    )

    # uni-number-box 的数量输入框
    quantity_input = number_box.locator(
        "input"
    ).first

    expect(quantity_input).to_be_visible(
        timeout=15000,
    )

    quantity_text = (
        quantity_input
        .input_value()
        .strip()
    )

    # 数量必须是大于等于 1 的数字
    assert quantity_text.isdigit(), (
        "购物车商品数量不是数字："
        f"{quantity_text}"
    )

    assert int(quantity_text) >= 1, (
        "购物车商品数量必须大于等于 1："
        f"{quantity_text}"
    )

    attach_text(
        "购物车商品数量",
        quantity_text,
    )

    # ========================================================
    # 校验商品选择框
    # ========================================================

    checkbox = first_cart_item.locator(
        ".checkbox"
    ).first

    expect(checkbox).to_be_visible(
        timeout=15000,
    )

    # ========================================================
    # 校验删除按钮
    # ========================================================

    delete_button = first_cart_item.locator(
        ".del-btn"
    )

    expect(delete_button).to_be_visible(
        timeout=15000,
    )

    # ========================================================
    # 校验去结算按钮
    # ========================================================

    confirm_button = cart_page.locator(
        ".confirm-btn"
    )

    expect(confirm_button).to_be_visible(
        timeout=15000,
    )

    expect(confirm_button).to_contain_text(
        "去结算"
    )

    expect(confirm_button).to_be_enabled(
        timeout=15000,
    )

    # 保存最终购物车截图
    save_screenshot(
        page,
        "portal-cart-product-information.png",
        "购物车商品信息",
    )