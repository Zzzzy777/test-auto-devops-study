"""
商城前台商品模块 UI 自动化测试

测试范围：

1. 从商城首页选择真实商品；
2. 点击商品进入商品详情页；
3. 校验商品详情页 URL；
4. 校验商品详情页主体结构；
5. 校验商品图片；
6. 校验商品名称；
7. 校验商品价格；
8. 校验加入购物车按钮；
9. 保存商品详情页截图；
10. 生成 Allure 测试报告。

注意：

首页中同时存在以下类型的卡片：

1. 品牌制造商卡片：
   class="guess-item"
   点击后进入品牌详情页；

2. 商品卡片：
   class="floor-item"
   或位于 .hot-section 下的 .guess-item
   点击后进入商品详情页。

本脚本会排除品牌制造商卡片，
只点击真实商品卡片。
"""

from pathlib import Path

import allure
from playwright.sync_api import Page, expect


# ============================================================
# 基础配置
# ============================================================

# 商城首页地址
HOME_URL = "http://localhost:8060/#/"

# 截图保存目录
SCREENSHOT_DIR = (
    Path(__file__).resolve().parents[1]
    / "reports"
    / "screenshots"
)


# ============================================================
# 首页真实商品选择器
# ============================================================

# 首页中真实商品所在区域：

# 1. 新鲜好物：
#    .seckill-section .floor-item

# 2. 人气推荐：
#    .hot-section .guess-item

# 3. 秒杀商品或猜你喜欢：
#    .guess-section .guess-item
#    但必须排除品牌制造商卡片。
#
# 品牌制造商卡片中包含：
#    .image-wrapper-brand
#
# 所以使用 :not(:has(.image-wrapper-brand))
# 排除品牌制造商卡片。
PRODUCT_CARD_SELECTOR = (
    ".seckill-section .floor-item:visible, "
    ".hot-section .guess-item:visible, "
    ".guess-section .guess-item"
    ":not(:has(.image-wrapper-brand)):visible"
)


# ============================================================
# 商品模块测试类
# ============================================================

@allure.epic("商城前台 UI 自动化测试")
@allure.feature("商品模块")
class TestPortalProductUI:
    """
    商城前台商品模块 UI 自动化测试。
    """

    # --------------------------------------------------------
    # 第 11 条：点击商品进入商品详情页
    # --------------------------------------------------------

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
        测试场景：

        1. 打开商城首页；
        2. 等待真实商品数据加载；
        3. 排除品牌制造商卡片；
        4. 选择第一个真实商品；
        5. 点击商品进入详情页；
        6. 校验商品详情页结构；
        7. 校验商品名称、价格、图片；
        8. 校验加入购物车按钮；
        9. 保存截图。
        """

        with allure.step("打开商城首页"):
            page.goto(
                HOME_URL,
                wait_until="domcontentloaded",
            )

            # uni-app 页面切换时，DOM 中可能存在多个首页页面。
            # 使用 :visible，定位当前真正显示的首页。
            home_page = page.locator(
                "uni-page[data-page='pages/index/index']:visible"
            )

            expect(home_page).to_be_visible(
                timeout=15000
            )

        with allure.step("等待真实商品数据加载"):
            # 只定位真实商品卡片。
            #
            # 不直接使用：
            #
            # .guess-item, .floor-item
            #
            # 因为首页最前面的 .guess-item 可能是品牌卡片，
            # 点击品牌卡片会进入品牌详情页，而不是商品详情页。
            product_items = home_page.locator(
                PRODUCT_CARD_SELECTOR
            )

            # 等待商品接口返回并完成页面渲染。
            expect(
                product_items.first
            ).to_be_visible(timeout=15000)

            product_count = product_items.count()

            assert product_count > 0, (
                "商城首页没有加载出真实商品卡片"
            )

            allure.attach(
                f"首页真实商品数量：{product_count}",
                name="首页真实商品数量",
                attachment_type=allure.attachment_type.TEXT,
            )

        with allure.step("获取第一个真实商品"):
            first_product = product_items.first

            # 获取商品名称。
            product_title = first_product.locator(
                ".title"
            )

            expect(
                product_title
            ).to_be_visible(timeout=15000)

            product_name = (
                product_title.first.inner_text().strip()
            )

            assert product_name, (
                "首页商品名称为空"
            )

            allure.attach(
                product_name,
                name="点击的商品名称",
                attachment_type=allure.attachment_type.TEXT,
            )

            # 记录商品卡片文本，便于 Allure 报告排查。
            allure.attach(
                first_product.inner_text(),
                name="点击的商品卡片内容",
                attachment_type=allure.attachment_type.TEXT,
            )

        with allure.step("点击真实商品"):
            # 点击真实商品卡片。
            #
            # 该卡片对应首页源码中的：
            #
            # @click="handleNavToDetailPage(item)"
            #
            # 页面跳转地址为：
            #
            # /pages/product/product?id=商品ID
            first_product.click()

        with allure.step("校验跳转到商品详情页"):
            # 商品详情页 URL 通常类似：
            #
            # http://localhost:8060/#/pages/product/product?id=1
            #
            page.wait_for_url(
                "**/pages/product/product*",
                timeout=15000,
            )

        with allure.step("定位当前可见的商品详情页"):
            # uni-app 页面跳转时可能存在多个相同 data-page 的节点。
            # 使用 :visible，定位当前正在显示的页面。
            product_detail_page = page.locator(
                "uni-page[data-page='pages/product/product']:visible"
            )

            expect(
                product_detail_page
            ).to_be_visible(timeout=15000)

        with allure.step("校验商品详情页主体"):
            # 商品详情页最外层容器。
            detail_container = product_detail_page.locator(
                ".container"
            )

            expect(
                detail_container
            ).to_be_visible(timeout=15000)

            # 商品基本信息区域。
            introduce_section = product_detail_page.locator(
                ".introduce-section"
            )

            expect(
                introduce_section
            ).to_be_visible(timeout=15000)

        with allure.step("校验商品图片"):
            # 商品详情页图片轮播区域。
            carousel = product_detail_page.locator(
                ".carousel"
            )

            expect(
                carousel
            ).to_be_visible(timeout=15000)

            # 页面源码中使用的是 uni-app image 组件。
            product_images = carousel.locator(
                "uni-image, image, img"
            )

            # 等待至少一张商品图片真正显示。
            expect(
                product_images.first
            ).to_be_visible(timeout=15000)

            image_count = product_images.count()

            # 商品详情页必须至少有一张商品图片。
            assert image_count > 0, (
                "商品详情页没有加载商品图片"
            )

            allure.attach(
                f"商品图片数量：{image_count}",
                name="商品图片数量",
                attachment_type=allure.attachment_type.TEXT,
            )

        with allure.step("校验商品名称"):
            # 商品详情页商品名称：
            #
            # .introduce-section .title
            detail_title = introduce_section.locator(
                ".title"
            )

            expect(
                detail_title
            ).to_be_visible(timeout=15000)

            detail_product_name = (
                detail_title.first.inner_text().strip()
            )

            assert detail_product_name, (
                "商品详情页商品名称为空"
            )

            allure.attach(
                detail_product_name,
                name="商品详情页名称",
                attachment_type=allure.attachment_type.TEXT,
            )

        with allure.step("校验商品价格"):
            # 商品详情页当前价格：
            #
            # .introduce-section .price
            detail_price = introduce_section.locator(
                ".price"
            )

            expect(
                detail_price
            ).to_be_visible(timeout=15000)

            detail_price_text = (
                detail_price.first.inner_text().strip()
            )

            assert detail_price_text, (
                "商品详情页商品价格为空"
            )

            allure.attach(
                detail_price_text,
                name="商品详情页价格",
                attachment_type=allure.attachment_type.TEXT,
            )

        with allure.step("校验商品其他基本信息"):
            # 销量、库存、浏览量所在区域。
            bot_row = introduce_section.locator(
                ".bot-row"
            )

            expect(
                bot_row
            ).to_be_visible(timeout=15000)

            bot_row_text = bot_row.inner_text().strip()

            allure.attach(
                bot_row_text,
                name="商品销量库存信息",
                attachment_type=allure.attachment_type.TEXT,
            )

        with allure.step("校验底部操作区域"):
            page_bottom = product_detail_page.locator(
                ".page-bottom"
            )

            expect(
                page_bottom
            ).to_be_visible(timeout=15000)

        with allure.step("校验立即购买按钮"):
            buy_now_button = product_detail_page.locator(
                ".buy-now-btn"
            )

            expect(
                buy_now_button
            ).to_be_visible(timeout=15000)

            expect(
                buy_now_button
            ).to_contain_text("立即购买")

        with allure.step("校验加入购物车按钮"):
            add_cart_button = product_detail_page.locator(
                ".add-cart-btn"
            )

            expect(
                add_cart_button
            ).to_be_visible(timeout=15000)

            expect(
                add_cart_button
            ).to_contain_text("加入购物车")

        with allure.step("记录商品详情页地址"):
            allure.attach(
                page.url,
                name="商品详情页地址",
                attachment_type=allure.attachment_type.TEXT,
            )

        with allure.step("保存商品详情页截图"):
            self.save_screenshot(
                page=page,
                file_name="portal_product_detail_page.png",
                allure_name="商品详情页面",
            )

    # ========================================================
    # 公共方法：保存截图
    # ========================================================

    @staticmethod
    def save_screenshot(
        page: Page,
        file_name: str,
        allure_name: str,
    ):
        """
        保存页面截图，并将截图添加到 Allure 报告。
        """

        # 创建截图目录。
        SCREENSHOT_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        # 拼接截图路径。
        screenshot_path = (
            SCREENSHOT_DIR / file_name
        )

        # 保存截图到本地目录。
        page.screenshot(
            path=str(screenshot_path),
            full_page=True,
        )

        # 同时添加到 Allure 报告。
        screenshot_bytes = page.screenshot(
            full_page=True,
        )

        allure.attach(
            screenshot_bytes,
            name=allure_name,
            attachment_type=allure.attachment_type.PNG,
        )


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
        测试场景：

        1. 打开商城首页；
        2. 点击首页中的真实商品；
        3. 进入商品详情页；
        4. 点击“购买类型”；
        5. 校验商品规格弹窗；
        6. 校验规格弹窗中的商品价格、库存和完成按钮；
        7. 点击完成关闭弹窗。
        """

        with allure.step("打开商城首页"):
            page.goto(
                HOME_URL,
                wait_until="domcontentloaded",
            )

            home_page = page.locator(
                "uni-page[data-page='pages/index/index']:visible"
            )

            expect(home_page).to_be_visible(
                timeout=15000
            )

        with allure.step("等待真实商品加载"):
            # 排除品牌制造商卡片，只选择真实商品。
            product_items = home_page.locator(
                ".seckill-section .floor-item:visible, "
                ".hot-section .guess-item:visible, "
                ".guess-section .guess-item"
                ":not(:has(.image-wrapper-brand)):visible"
            )

            expect(
                product_items.first
            ).to_be_visible(timeout=15000)

            assert product_items.count() > 0, (
                "首页没有加载出真实商品"
            )

        with allure.step("进入商品详情页"):
            first_product = product_items.first
            first_product.click()

            page.wait_for_url(
                "**/pages/product/product*",
                timeout=15000,
            )

            # 只定位当前可见的商品详情页。
            product_detail_page = page.locator(
                "uni-page[data-page='pages/product/product']:visible"
            )

            expect(
                product_detail_page
            ).to_be_visible(timeout=15000)

        with allure.step("等待商品详情信息加载"):
            introduce_section = product_detail_page.locator(
                ".introduce-section"
            )

            expect(
                introduce_section
            ).to_be_visible(timeout=15000)

            # 商品规格入口所在的第一个 c-row。
            specification_row = product_detail_page.locator(
                ".c-list .c-row"
            ).filter(
                has_text="购买类型"
            )

            expect(
                specification_row
            ).to_be_visible(timeout=15000)

        with allure.step("点击购买类型"):
            specification_row.click()

        with allure.step("校验规格弹窗"):
            # 商品详情页源码中规格弹窗为：
            #
            # <view class="popup spec" :class="specClass">
            #
            # 使用 :visible，避免定位到隐藏的历史弹窗。
            specification_popup = product_detail_page.locator(
                ".popup.spec:visible"
            )

            expect(
                specification_popup
            ).to_be_visible(timeout=15000)

        with allure.step("校验规格弹窗商品信息"):
            # 弹窗中的商品价格。
            popup_price = specification_popup.locator(
                ".price"
            )

            expect(
                popup_price
            ).to_be_visible(timeout=15000)

            # 弹窗中的库存信息。
            popup_stock = specification_popup.locator(
                ".stock"
            )

            expect(
                popup_stock
            ).to_be_visible(timeout=15000)

            allure.attach(
                f"规格弹窗价格：{popup_price.first.inner_text()}\n"
                f"规格弹窗库存：{popup_stock.first.inner_text()}",
                name="规格弹窗商品信息",
                attachment_type=allure.attachment_type.TEXT,
            )

        with allure.step("校验规格选项"):
            # 商品规格选项位于 .attr-list .tit。
            specification_options = (
                specification_popup.locator(
                    ".attr-list .tit"
                )
            )

            specification_option_count = (
                specification_options.count()
            )

            # 某些商品可能没有配置具体规格。
            # 如果有规格，则校验第一个规格选项可见。
            if specification_option_count > 0:
                expect(
                    specification_options.first
                ).to_be_visible(timeout=15000)

                allure.attach(
                    f"规格选项数量："
                    f"{specification_option_count}",
                    name="规格选项数量",
                    attachment_type=allure.attachment_type.TEXT,
                )
            else:
                allure.attach(
                    "当前商品没有配置具体规格选项",
                    name="规格选项结果",
                    attachment_type=allure.attachment_type.TEXT,
                )

        with allure.step("校验完成按钮"):
            complete_button = specification_popup.locator(
                ".btn"
            )

            expect(
                complete_button
            ).to_be_visible(timeout=15000)

            expect(
                complete_button
            ).to_contain_text("完成")

        with allure.step("关闭规格弹窗"):
            complete_button.click()

            # 等待弹窗关闭动画结束。
            page.wait_for_timeout(400)

            # 弹窗关闭后，当前可见规格弹窗数量应为 0。
            expect(
                product_detail_page.locator(
                    ".popup.spec:visible"
                )
            ).to_have_count(
                0,
                timeout=15000,
            )

        with allure.step("保存规格弹窗截图"):
            self.save_screenshot(
                page=page,
                file_name="portal_product_specification_popup.png",
                allure_name="商品规格弹窗",
            )


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
        测试场景：

        1. 打开商城首页；
        2. 点击真实商品进入详情页；
        3. 点击商品参数；
        4. 校验商品参数弹窗；
        5. 校验参数内容；
        6. 关闭参数弹窗。
        """

        with allure.step("打开商城首页"):
            page.goto(
                "http://localhost:8060/#/",
                wait_until="domcontentloaded",
            )

            home_page = page.locator(
                "uni-page[data-page='pages/index/index']:visible"
            )

            expect(home_page).to_be_visible(
                timeout=15000
            )

        with allure.step("等待真实商品加载"):
            # 排除品牌制造商卡片，只选择真实商品。
            product_items = home_page.locator(
                ".seckill-section .floor-item:visible, "
                ".hot-section .guess-item:visible, "
                ".guess-section .guess-item"
                ":not(:has(.image-wrapper-brand)):visible"
            )

            expect(
                product_items.first
            ).to_be_visible(timeout=15000)

            assert product_items.count() > 0, (
                "首页没有加载出真实商品"
            )

        with allure.step("进入商品详情页"):
            product_items.first.click()

            page.wait_for_url(
                "**/pages/product/product*",
                timeout=15000,
            )

            product_detail_page = page.locator(
                "uni-page[data-page='pages/product/product']:visible"
            )

            expect(
                product_detail_page
            ).to_be_visible(timeout=15000)

        with allure.step("等待商品详情页加载"):
            detail_container = product_detail_page.locator(
                ".container"
            )

            expect(
                detail_container
            ).to_be_visible(timeout=15000)

            # 商品参数是商品详情页第二个 c-row。
            # 当前页面顺序为：
            #
            # 0：购买类型
            # 1：商品参数
            # 2：优惠券
            # 3：促销活动
            # 4：服务
            detail_rows = product_detail_page.locator(
                ".c-list .c-row"
            )

            expect(
                detail_rows.nth(1)
            ).to_be_visible(timeout=15000)

        with allure.step("点击商品参数"):
            attribute_row = detail_rows.nth(1)

            allure.attach(
                attribute_row.inner_text(),
                name="商品参数入口文本",
                attachment_type=allure.attachment_type.TEXT,
            )

            attribute_row.click()

        with allure.step("校验商品参数弹窗"):
            # 商品参数弹窗和规格弹窗都使用 popup spec，
            # 但是商品参数弹窗内部有 .no-padding。
            attribute_popup = product_detail_page.locator(
                ".popup.spec:visible .layer.no-padding"
            )

            expect(
                attribute_popup
            ).to_be_visible(timeout=15000)

        with allure.step("校验参数内容"):
            parameter_rows = attribute_popup.locator(
                ".c-list .c-row"
            )

            parameter_count = parameter_rows.count()

            allure.attach(
                f"商品参数数量：{parameter_count}",
                name="商品参数数量",
                attachment_type=allure.attachment_type.TEXT,
            )

            # 如果后台给当前商品配置了参数，
            # 则校验第一条参数可见。
            if parameter_count > 0:
                expect(
                    parameter_rows.first
                ).to_be_visible(timeout=15000)

                first_parameter_text = (
                    parameter_rows.first.inner_text().strip()
                )

                assert first_parameter_text, (
                    "商品参数内容为空"
                )

                allure.attach(
                    first_parameter_text,
                    name="第一条商品参数",
                    attachment_type=allure.attachment_type.TEXT,
                )
            else:
                # 某些商品可能没有配置参数。
                # 这种情况下弹窗正常打开即可。
                allure.attach(
                    "当前商品没有配置具体参数",
                    name="商品参数结果",
                    attachment_type=allure.attachment_type.TEXT,
                )

        with allure.step("保存商品参数弹窗截图"):
            self.save_screenshot(
                page=page,
                file_name="portal_product_attribute_popup.png",
                allure_name="商品参数弹窗",
            )

        with allure.step("关闭商品参数弹窗"):
            # 点击弹窗遮罩层关闭弹窗。
            popup_mask = product_detail_page.locator(
                ".popup.spec:visible .mask"
            )

            expect(
                popup_mask
            ).to_be_visible(timeout=15000)

            # 获取遮罩层的尺寸。
            # 不能点击 position={"x": 5, "y": 5}，
            # 因为左上角可能被页面顶部导航栏拦截。
            mask_box = popup_mask.bounding_box()

            assert mask_box is not None, (
            "商品参数弹窗遮罩层没有获取到有效坐标"
            )

            # 在遮罩层上方区域选择一个安全点击点。
            #
            # 说明：
            # 1. y 坐标不能太靠近顶部，避免被 custom-navbar 拦截；
            # 2. y 坐标不能太靠近底部，避免点击到弹窗内容区域；
            # 3. 遮罩层一般覆盖整个页面，因此这里选择页面上方中间区域。
            safe_x = 10
            safe_y = min(
                max(mask_box["height"] * 0.25, 100),
                mask_box["height"] - 20,
            )

            # 点击遮罩层，关闭商品参数弹窗。
            popup_mask.click(
            position={
                "x": safe_x,
                "y": safe_y,
            },
            timeout=15000,
            )

            # 等待前端 hide 动画和状态切换完成。
            page.wait_for_timeout(500)

            # 关闭后，商品参数弹窗不应再处于可见状态。
            expect(
                product_detail_page.locator(
                ".popup.spec:visible .layer.no-padding"
            )
            ).to_have_count(
                0,
                timeout=15000,
            )