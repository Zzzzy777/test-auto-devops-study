"""
商城前台商品详情页 UI 自动化测试。

覆盖场景：
1. 首页点击真实商品进入详情页；
2. 校验详情页主体、商品图片、名称、价格和操作按钮；
3. 打开并关闭商品规格弹窗；
4. 打开并关闭商品参数弹窗；
5. 生成截图和 Allure 附件。

运行环境：
- 前端：http://localhost:8060
- pytest-playwright
- 浏览器：Chromium
"""

from pathlib import Path

import allure
from playwright.sync_api import Page, expect


# =====================================================================
# 基础配置
# =====================================================================

# 商城前台首页地址
HOME_URL = "http://localhost:8060/#/"

# 商品详情页 URL 匹配规则
DETAIL_PATH = "**/pages/product/product*"

# Playwright 默认等待时间，单位为毫秒
TIMEOUT = 15_000

# 截图保存目录
SCREENSHOT_DIR = (
    Path(__file__).resolve().parents[1]
    / "reports"
    / "screenshots"
)


# =====================================================================
# 首页真实商品选择器
# =====================================================================

# 首页中既有品牌卡片，也有商品卡片。
#
# 真实商品卡片主要位于：
# 1. .seckill-section .floor-item
# 2. .hot-section .guess-item
# 3. .guess-section .guess-item
#
# 品牌卡片通常包含：
# .image-wrapper-brand
#
# 因此需要排除品牌卡片，避免点击后进入品牌详情页。
PRODUCT_CARD_SELECTOR = (
    ".seckill-section .floor-item:visible, "
    ".hot-section .guess-item:visible, "
    ".guess-section .guess-item"
    ":not(:has(.image-wrapper-brand)):visible"
)


# =====================================================================
# 通用辅助方法
# =====================================================================

def attach_text(name: str, value: object) -> None:
    """
    将文本信息添加到 Allure 报告。

    参数：
        name：附件名称
        value：附件内容
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

    参数：
        page：Playwright 页面对象
        file_name：本地截图文件名
        allure_name：Allure 中显示的附件名称
    """
    SCREENSHOT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    screenshot_path = SCREENSHOT_DIR / file_name

    # 保存截图到项目目录
    screenshot_bytes = page.screenshot(
        path=str(screenshot_path),
        full_page=True,
    )

    # 将截图添加到 Allure
    allure.attach(
        screenshot_bytes,
        name=allure_name,
        attachment_type=allure.attachment_type.PNG,
    )


def visible_page(page: Page, page_name: str):
    """
    定位 uni-app 当前正在显示的页面。

    uni-app 页面跳转过程中，DOM 中可能暂时存在多个
    相同 data-page 的页面，所以必须使用 :visible。
    """
    return page.locator(
        f"uni-page[data-page='{page_name}']:visible"
    )


def open_product_detail(page: Page):
    """
    从商城首页点击第一个真实商品，进入商品详情页。

    返回：
        商品详情页 Locator
    """
    # 设置当前页面默认等待时间
    page.set_default_timeout(TIMEOUT)

    with allure.step("打开商城首页"):
        page.goto(
            HOME_URL,
            wait_until="domcontentloaded",
        )

    with allure.step("定位商城首页"):
        home_page = visible_page(
            page,
            "pages/index/index",
        )

        expect(home_page).to_be_visible(
            timeout=TIMEOUT,
        )

    with allure.step("等待真实商品加载"):
        # 只定位商品卡片，排除品牌制造商卡片
        products = home_page.locator(
            PRODUCT_CARD_SELECTOR
        )

        # 等待第一个真实商品显示
        expect(products.first).to_be_visible(
            timeout=TIMEOUT,
        )

        product_count = products.count()

        assert product_count > 0, (
            "商城首页没有加载出真实商品卡片"
        )

        attach_text(
            "首页真实商品数量",
            product_count,
        )

    with allure.step("获取第一个真实商品信息"):
        first_product = products.first

        product_card_text = (
            first_product.inner_text().strip()
        )

        assert product_card_text, (
            "第一个真实商品卡片没有文本内容"
        )

        attach_text(
            "本次测试商品卡片内容",
            product_card_text,
        )

        # 获取商品名称，作为测试报告中的辅助信息
        product_title = first_product.locator(
            ".title"
        ).first

        if product_title.count() > 0:
            attach_text(
                "本次测试商品名称",
                product_title.inner_text().strip(),
            )

    with allure.step("点击第一个真实商品"):
        first_product.click()

    with allure.step("等待进入商品详情页"):
        page.wait_for_url(
            DETAIL_PATH,
            timeout=TIMEOUT,
        )

        detail_page = visible_page(
            page,
            "pages/product/product",
        )

        expect(detail_page).to_be_visible(
            timeout=TIMEOUT,
        )

        # 商品详情页主体容器
        expect(
            detail_page.locator(".container")
        ).to_be_visible(
            timeout=TIMEOUT,
        )

    return detail_page


def close_popup_by_mask(
    page: Page,
    popup,
) -> None:
    """
    点击弹窗遮罩层关闭弹窗。

    关闭弹窗时不依赖关闭图标，避免因为页面版本、
    图标结构或者定位变化导致用例不稳定。
    """
    mask = popup.locator(
        ".mask"
    ).first

    expect(mask).to_be_visible(
        timeout=TIMEOUT,
    )

    mask_box = mask.bounding_box()

    assert mask_box is not None, (
        "弹窗遮罩层没有获取到有效坐标"
    )

    # 不能点击最左上角，因为可能被顶部导航栏拦截。
    # 选择遮罩层上方的安全位置进行点击。
    safe_x = min(
        max(mask_box["width"] * 0.05, 10),
        max(mask_box["width"] - 10, 10),
    )

    safe_y = min(
        max(mask_box["height"] * 0.25, 100),
        max(mask_box["height"] - 20, 100),
    )

    mask.click(
        position={
            "x": safe_x,
            "y": safe_y,
        },
        timeout=TIMEOUT,
    )

    # 等待弹窗关闭动画完成
    page.wait_for_timeout(500)


# =====================================================================
# 商品详情页测试类
# =====================================================================

@allure.epic("商城前台 UI 自动化测试")
@allure.feature("商品详情模块")
class TestPortalProductDetailUI:
    """
    商城前台商品详情页 UI 自动化测试。
    """

    # -----------------------------------------------------------------
    # 用例一：进入商品详情页并校验基本信息
    # -----------------------------------------------------------------

    @allure.story("进入商品详情")
    @allure.title("从首页点击真实商品进入商品详情页")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("portal")
    @allure.tag("product")
    def test_click_product_to_detail_page(
        self,
        page: Page,
    ):
        """
        测试内容：

        1. 打开商城首页；
        2. 等待真实商品加载；
        3. 点击商品进入详情页；
        4. 校验详情页主体结构；
        5. 校验商品图片；
        6. 校验商品名称；
        7. 校验商品价格；
        8. 校验立即购买按钮；
        9. 校验加入购物车按钮。
        """

        detail_page = open_product_detail(page)

        with allure.step("校验商品详情页主体结构"):
            # 商品基本信息区域
            introduce_section = detail_page.locator(
                ".introduce-section"
            )

            expect(
                introduce_section
            ).to_be_visible(
                timeout=TIMEOUT,
            )

            # 商品图片轮播区域
            carousel = detail_page.locator(
                ".carousel"
            )

            expect(
                carousel
            ).to_be_visible(
                timeout=TIMEOUT,
            )

            # 页面底部操作区域
            page_bottom = detail_page.locator(
                ".page-bottom"
            )

            expect(
                page_bottom
            ).to_be_visible(
                timeout=TIMEOUT,
            )

        with allure.step("校验商品图片"):
            # 商品图片可能被渲染成 uni-image、image 或 img
            product_images = carousel.locator(
                "uni-image, image, img"
            )

            expect(
                product_images.first
            ).to_be_visible(
                timeout=TIMEOUT,
            )

            image_count = product_images.count()

            assert image_count > 0, (
                "商品详情页没有加载商品图片"
            )

            attach_text(
                "商品图片数量",
                image_count,
            )

        with allure.step("校验商品名称"):
            detail_title = introduce_section.locator(
                ".title"
            ).first

            expect(
                detail_title
            ).to_be_visible(
                timeout=TIMEOUT,
            )

            product_name = (
                detail_title.inner_text().strip()
            )

            assert product_name, (
                "商品详情页商品名称为空"
            )

            attach_text(
                "商品详情页名称",
                product_name,
            )

        with allure.step("校验商品价格"):
            detail_price = introduce_section.locator(
                ".price"
            ).first

            expect(
                detail_price
            ).to_be_visible(
                timeout=TIMEOUT,
            )

            price_text = (
                detail_price.inner_text().strip()
            )

            assert price_text, (
                "商品详情页商品价格为空"
            )

            attach_text(
                "商品详情页价格",
                price_text,
            )

        with allure.step("校验销量和库存信息"):
            stock_info = introduce_section.locator(
                ".bot-row"
            )

            expect(
                stock_info
            ).to_be_visible(
                timeout=TIMEOUT,
            )

            stock_text = (
                stock_info.inner_text().strip()
            )

            attach_text(
                "商品销量库存信息",
                stock_text,
            )

        with allure.step("校验立即购买按钮"):
            buy_now_button = detail_page.locator(
                ".buy-now-btn"
            ).first

            expect(
                buy_now_button
            ).to_be_visible(
                timeout=TIMEOUT,
            )

            expect(
                buy_now_button
            ).to_contain_text(
                "立即购买"
            )

        with allure.step("校验加入购物车按钮"):
            add_cart_button = detail_page.locator(
                ".add-cart-btn"
            ).first

            expect(
                add_cart_button
            ).to_be_visible(
                timeout=TIMEOUT,
            )

            expect(
                add_cart_button
            ).to_contain_text(
                "加入购物车"
            )

        with allure.step("保存商品详情页地址"):
            attach_text(
                "商品详情页地址",
                page.url,
            )

        with allure.step("保存商品详情页截图"):
            save_screenshot(
                page=page,
                file_name="portal_product_detail_page.png",
                allure_name="商品详情页",
            )

    # -----------------------------------------------------------------
    # 用例二：商品规格弹窗
    # -----------------------------------------------------------------

    @allure.story("商品规格")
    @allure.title("点击购买类型后能够正常打开商品规格弹窗")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("portal")
    @allure.tag("product")
    @allure.tag("specification")
    def test_product_specification_popup(
        self,
        page: Page,
    ):
        """
        测试内容：

        1. 进入商品详情页；
        2. 点击购买类型；
        3. 校验商品规格弹窗；
        4. 校验弹窗价格；
        5. 校验弹窗库存；
        6. 校验规格选项；
        7. 点击完成关闭弹窗。
        """

        detail_page = open_product_detail(page)

        with allure.step("定位购买类型入口"):
            specification_row = (
                detail_page
                .locator(".c-list .c-row")
                .filter(has_text="购买类型")
            )

            expect(
                specification_row
            ).to_be_visible(
                timeout=TIMEOUT,
            )

            attach_text(
                "购买类型入口文本",
                specification_row.inner_text().strip(),
            )

        with allure.step("点击购买类型"):
            specification_row.click()

        with allure.step("校验规格弹窗"):
            specification_popup = detail_page.locator(
                ".popup.spec:visible"
            )

            expect(
                specification_popup
            ).to_be_visible(
                timeout=TIMEOUT,
            )

        with allure.step("校验规格弹窗商品价格"):
            popup_price = specification_popup.locator(
                ".price"
            ).first

            expect(
                popup_price
            ).to_be_visible(
                timeout=TIMEOUT,
            )

        with allure.step("校验规格弹窗库存"):
            popup_stock = specification_popup.locator(
                ".stock"
            ).first

            expect(
                popup_stock
            ).to_be_visible(
                timeout=TIMEOUT,
            )

        with allure.step("记录规格弹窗商品信息"):
            attach_text(
                "规格弹窗商品信息",
                specification_popup.inner_text().strip(),
            )

        with allure.step("校验规格选项"):
            specification_options = (
                specification_popup
                .locator(".attr-list .tit")
            )

            option_count = (
                specification_options.count()
            )

            attach_text(
                "规格选项数量",
                option_count,
            )

            # 当前商品可能没有配置具体规格。
            # 如果存在规格，则必须校验第一个规格真实可见。
            if option_count > 0:
                expect(
                    specification_options.first
                ).to_be_visible(
                    timeout=TIMEOUT,
                )

        with allure.step("校验完成按钮"):
            complete_button = (
                specification_popup
                .locator(".btn")
                .filter(has_text="完成")
                .first
            )

            expect(
                complete_button
            ).to_be_visible(
                timeout=TIMEOUT,
            )

            expect(
                complete_button
            ).to_contain_text(
                "完成"
            )

        with allure.step("保存规格弹窗截图"):
            save_screenshot(
                page=page,
                file_name="portal_product_specification_popup.png",
                allure_name="商品规格弹窗",
            )

        with allure.step("点击完成关闭规格弹窗"):
            complete_button.click()

            # 等待弹窗关闭动画
            page.wait_for_timeout(500)

            # 关闭后不应再存在可见规格弹窗
            expect(
                detail_page.locator(
                    ".popup.spec:visible"
                )
            ).to_have_count(
                0,
                timeout=TIMEOUT,
            )

    # -----------------------------------------------------------------
    # 用例三：商品参数弹窗
    # -----------------------------------------------------------------

    @allure.story("商品参数")
    @allure.title("点击商品参数后能够正常打开参数弹窗")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("portal")
    @allure.tag("product")
    @allure.tag("attribute")
    def test_product_attribute_popup(
        self,
        page: Page,
    ):
        """
        测试内容：

        1. 进入商品详情页；
        2. 定位商品参数入口；
        3. 点击商品参数；
        4. 校验商品参数弹窗；
        5. 校验商品参数内容；
        6. 关闭商品参数弹窗。
        """

        detail_page = open_product_detail(page)

        with allure.step("定位商品参数入口"):
            detail_rows = detail_page.locator(
                ".c-list .c-row"
            )

            # 优先使用文字定位。
            # 这样比固定使用 nth(1) 更稳定。
            attribute_row = detail_rows.filter(
                has_text="商品参数"
            )

            # 如果当前数据文本没有渲染“商品参数”，
            # 则按照当前项目页面结构使用第二行。
            if attribute_row.count() == 0:
                attribute_row = detail_rows.nth(1)

            expect(
                attribute_row
            ).to_be_visible(
                timeout=TIMEOUT,
            )

            attach_text(
                "商品参数入口文本",
                attribute_row.inner_text().strip(),
            )

        with allure.step("点击商品参数"):
            attribute_row.click()

        with allure.step("校验商品参数弹窗"):
            # 商品参数弹窗结构：
            # .popup.spec:visible .layer.no-padding
            attribute_popup = detail_page.locator(
                ".popup.spec:visible .layer.no-padding"
            )

            expect(
                attribute_popup
            ).to_be_visible(
                timeout=TIMEOUT,
            )

        with allure.step("校验商品参数内容"):
            parameter_rows = attribute_popup.locator(
                ".c-list .c-row"
            )

            parameter_count = parameter_rows.count()

            attach_text(
                "商品参数数量",
                parameter_count,
            )

            # 当前商品可能没有维护具体参数。
            # 如果有参数，则校验第一条参数有内容。
            if parameter_count > 0:
                expect(
                    parameter_rows.first
                ).to_be_visible(
                    timeout=TIMEOUT,
                )

                first_parameter_text = (
                    parameter_rows.first
                    .inner_text()
                    .strip()
                )

                assert first_parameter_text, (
                    "商品参数内容为空"
                )

                attach_text(
                    "第一条商品参数",
                    first_parameter_text,
                )
            else:
                attach_text(
                    "商品参数结果",
                    "当前商品没有配置具体参数",
                )

        with allure.step("保存商品参数弹窗截图"):
            save_screenshot(
                page=page,
                file_name="portal_product_attribute_popup.png",
                allure_name="商品参数弹窗",
            )

        with allure.step("点击遮罩关闭商品参数弹窗"):
            visible_popup = detail_page.locator(
                ".popup.spec:visible"
            )

            close_popup_by_mask(
                page=page,
                popup=visible_popup,
            )

            # 关闭后，参数弹窗内容不能继续可见
            expect(
                detail_page.locator(
                    ".popup.spec:visible .layer.no-padding"
                )
            ).to_have_count(
                0,
                timeout=TIMEOUT,
            )