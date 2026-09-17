"""
商城前台分类页面 UI 自动化测试

测试范围：

1. 从商城首页点击“分类”，进入分类页面；
2. 校验分类页面整体结构；
3. 校验一级分类和二级分类数据；
4. 点击一级分类，校验分类切换；
5. 点击二级分类，进入商品列表页面；
6. 校验商品列表页面结构；
7. 保存页面截图；
8. 生成 Allure 测试报告。

商城前台地址：

首页：
http://localhost:8060/#/

分类页面：
http://localhost:8060/#/pages/category/category

商品列表页面：
http://localhost:8060/#/pages/product/list
"""

import re
from pathlib import Path

import allure
from playwright.sync_api import Page, expect


# ============================================================
# 基础配置
# ============================================================

# 商城首页地址
HOME_URL = "http://localhost:8060/#/"

# 商城分类页面地址
CATEGORY_URL = (
    "http://localhost:8060/#/pages/category/category"
)

# 截图保存目录
SCREENSHOT_DIR = (
    Path(__file__).resolve().parents[1]
    / "reports"
    / "screenshots"
)


# ============================================================
# 分类页面测试类
# ============================================================

@allure.epic("商城前台 UI 自动化测试")
@allure.feature("分类模块")
class TestPortalCategoryUI:
    """
    商城前台分类模块 UI 自动化测试。
    """

    # --------------------------------------------------------
    # 第 8 条：从首页进入分类页面
    # --------------------------------------------------------

    @allure.story("进入分类页面")
    @allure.title(
        "点击首页底部分类进入分类页面并校验分类数据"
    )
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("portal")
    @allure.tag("category")
    def test_enter_category_page_and_verify_data(
        self,
        page: Page,
    ):
        """
        测试场景：

        1. 打开商城首页；
        2. 点击底部导航栏中的“分类”；
        3. 校验 URL 跳转到分类页面；
        4. 校验分类页面主体结构；
        5. 校验一级分类正常展示；
        6. 校验二级分类正常展示；
        7. 保存分类页面截图。
        """

        with allure.step("打开商城首页"):
            page.goto(
                HOME_URL,
                wait_until="domcontentloaded",
            )

            # 使用 :visible，确保定位当前可见首页。
            # uni-app 页面切换时，历史页面可能仍保留在 DOM 中。
            home_page = page.locator(
                "uni-page[data-page='pages/index/index']:visible"
            )

            expect(home_page).to_be_visible(
                timeout=15000
            )

        with allure.step("定位底部导航栏"):
            tabbar = page.locator("uni-tabbar:visible")

            expect(tabbar).to_be_visible(
                timeout=15000
            )

        with allure.step("点击底部导航栏分类"):
            category_tab = tabbar.get_by_text(
                "分类",
                exact=True,
            )

            expect(category_tab).to_be_visible(
                timeout=15000
            )

            category_tab.click()

        with allure.step("校验进入分类页面"):
            page.wait_for_url(
                "**/pages/category/category*",
                timeout=15000,
            )

            # 重点：使用 :visible，防止匹配到隐藏的分类页面。
            category_page = page.locator(
                "uni-page[data-page='pages/category/category']:visible"
            )

            expect(category_page).to_be_visible(
                timeout=15000
            )

        with allure.step("校验分类页面主体结构"):
            content = category_page.locator(".content")

            expect(content).to_be_visible(
                timeout=15000
            )

            # 左侧一级分类区域
            left_aside = category_page.locator(
                ".left-aside"
            )

            expect(left_aside).to_be_visible(
                timeout=15000
            )

            # 右侧二级分类区域
            right_aside = category_page.locator(
                ".right-aside"
            )

            expect(right_aside).to_be_visible(
                timeout=15000
            )

        with allure.step("等待分类数据加载"):
            # 一级分类列表
            first_level_items = category_page.locator(
                ".f-item"
            )

            # 二级分类列表
            second_level_items = category_page.locator(
                ".s-item"
            )

            # 等待一级分类中的第一个元素显示
            expect(
                first_level_items.first
            ).to_be_visible(timeout=15000)

            # 等待二级分类中的第一个元素显示
            expect(
                second_level_items.first
            ).to_be_visible(timeout=15000)

        with allure.step("校验一级分类数据"):
            first_level_count = first_level_items.count()

            assert first_level_count > 0, (
                "分类页面没有加载出一级分类数据"
            )

            allure.attach(
                f"一级分类数量：{first_level_count}",
                name="一级分类数量",
                attachment_type=allure.attachment_type.TEXT,
            )

        with allure.step("校验二级分类数据"):
            second_level_count = second_level_items.count()

            assert second_level_count > 0, (
                "分类页面没有加载出二级分类数据"
            )

            allure.attach(
                f"二级分类数量：{second_level_count}",
                name="二级分类数量",
                attachment_type=allure.attachment_type.TEXT,
            )

        with allure.step("保存分类页面截图"):
            self.save_screenshot(
                page=page,
                file_name="portal_category_page.png",
                allure_name="商城分类页面",
            )

    # --------------------------------------------------------
    # 第 9 条：点击一级分类进行切换
    # --------------------------------------------------------

    @allure.story("一级分类切换")
    @allure.title(
        "点击不同一级分类后能够正确切换二级分类"
    )
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("portal")
    @allure.tag("category")
    def test_switch_first_level_category(
        self,
        page: Page,
    ):
        """
        测试场景：

        1. 打开分类页面；
        2. 等待一级分类数据加载；
        3. 获取一级分类数量；
        4. 点击第二个一级分类；
        5. 校验第二个一级分类具有 active 状态；
        6. 校验切换后右侧二级分类仍然正常展示；
        7. 保存分类切换截图。
        """

        with allure.step("打开商城分类页面"):
            page.goto(
                CATEGORY_URL,
                wait_until="domcontentloaded",
            )

            # 必须使用 :visible，避免获取到隐藏页面。
            category_page = page.locator(
                "uni-page[data-page='pages/category/category']:visible"
            )

            expect(category_page).to_be_visible(
                timeout=15000
            )

        with allure.step("等待一级分类数据加载"):
            first_level_items = category_page.locator(
                ".f-item"
            )

            expect(
                first_level_items.first
            ).to_be_visible(timeout=15000)

            first_level_count = first_level_items.count()

            # 至少需要两个一级分类，才能验证切换功能。
            assert first_level_count >= 2, (
                f"当前一级分类数量为 {first_level_count}，"
                "少于 2 个，无法验证一级分类切换功能"
            )

            allure.attach(
                f"一级分类数量：{first_level_count}",
                name="一级分类数量",
                attachment_type=allure.attachment_type.TEXT,
            )

        with allure.step("记录当前一级分类状态"):
            first_item = first_level_items.first
            second_item = first_level_items.nth(1)

            first_item_name = first_item.inner_text()
            second_item_name = second_item.inner_text()

            allure.attach(
                f"第一个一级分类：{first_item_name}\n"
                f"第二个一级分类：{second_item_name}",
                name="一级分类名称",
                attachment_type=allure.attachment_type.TEXT,
            )

        with allure.step("点击第二个一级分类"):
            second_item.click()

        with allure.step("校验一级分类切换成功"):
            # 分类页面源码中：
            #
            # :class="{ active: item.id === currentCateId }"
            #
            # 因此点击后第二个一级分类应包含 active class。
            expect(second_item).to_have_class(
                re.compile(r"\bactive\b"),
                timeout=15000,
            )

        with allure.step("校验切换后的二级分类"):
            second_level_items = category_page.locator(
                ".s-item"
            )

            expect(
                second_level_items.first
            ).to_be_visible(timeout=15000)

            second_level_count = second_level_items.count()

            assert second_level_count > 0, (
                "切换一级分类后没有展示二级分类数据"
            )

            allure.attach(
                f"切换后的二级分类数量：{second_level_count}",
                name="切换后二级分类数量",
                attachment_type=allure.attachment_type.TEXT,
            )

        with allure.step("保存一级分类切换截图"):
            self.save_screenshot(
                page=page,
                file_name="portal_category_switch.png",
                allure_name="一级分类切换页面",
            )

    # --------------------------------------------------------
    # 第 10 条：点击二级分类进入商品列表
    # --------------------------------------------------------

    @allure.story("进入商品列表")
    @allure.title(
        "点击二级分类后进入商品列表页面"
    )
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("portal")
    @allure.tag("category")
    @allure.tag("product")
    def test_click_second_level_category_to_product_list(
        self,
        page: Page,
    ):
        """
        测试场景：

        1. 打开分类页面；
        2. 等待二级分类数据加载；
        3. 点击第一个二级分类；
        4. 校验 URL 跳转到商品列表页面；
        5. 校验当前可见的商品列表页面；
        6. 校验搜索栏、排序栏和商品列表容器；
        7. 保存商品列表页面截图。

        注意：

        uni-app 页面跳转时，旧页面可能仍然保留在 DOM 中。
        因此本用例中的商品列表页面必须使用：

        uni-page[data-page='pages/product/list']:visible

        否则可能定位到隐藏页面，出现：

        Actual value: hidden
        """

        with allure.step("打开商城分类页面"):
            page.goto(
                CATEGORY_URL,
                wait_until="domcontentloaded",
            )

            # 只定位当前可见的分类页面。
            category_page = page.locator(
                "uni-page[data-page='pages/category/category']:visible"
            )

            expect(category_page).to_be_visible(
                timeout=15000
            )

        with allure.step("等待二级分类数据加载"):
            second_level_items = category_page.locator(
                ".s-item"
            )

            # 等待第一个二级分类显示。
            expect(
                second_level_items.first
            ).to_be_visible(timeout=15000)

            second_level_count = second_level_items.count()

            assert second_level_count > 0, (
                "分类页面没有加载出二级分类数据"
            )

            allure.attach(
                f"二级分类数量：{second_level_count}",
                name="二级分类数量",
                attachment_type=allure.attachment_type.TEXT,
            )

        with allure.step("获取要点击的二级分类"):
            first_second_level_item = (
                second_level_items.first
            )

            second_level_name = (
                first_second_level_item.inner_text()
            )

            allure.attach(
                second_level_name,
                name="点击的二级分类名称",
                attachment_type=allure.attachment_type.TEXT,
            )

        with allure.step("点击第一个二级分类"):
            first_second_level_item.click()

            # uni-app 页面切换需要短暂时间。
            # 这里不是用来代替断言，而是等待路由切换动画开始。
            page.wait_for_timeout(500)

        with allure.step("校验 URL 跳转到商品列表页面"):
            # 商品列表页面地址通常类似：
            #
            # http://localhost:8060/#/pages/product/list?fid=1&sid=2
            #
            page.wait_for_url(
                "**/pages/product/list*",
                timeout=15000,
            )

        with allure.step("定位当前可见的商品列表页面"):
            # 关键修复：
            #
            # 页面跳转后 DOM 中可能存在多个相同 data-page 的 uni-page，
            # 其中部分是隐藏的历史页面。
            #
            # :visible 可以确保定位当前正在显示的商品列表页面。
            product_list_page = page.locator(
                "uni-page[data-page='pages/product/list']:visible"
            )

            expect(product_list_page).to_be_visible(
                timeout=15000
            )

            # 等待页面切换动画结束。
            page.wait_for_timeout(800)

        with allure.step("校验商品列表页面结构"):
            # 商品搜索区域
            search_bar = product_list_page.locator(
                ".search-bar"
            )

            expect(search_bar).to_be_visible(
                timeout=15000
            )

            # 商品排序导航栏
            navbar = product_list_page.locator(
                ".navbar"
            )

            expect(navbar).to_be_visible(
                timeout=15000
            )

            # 商品列表容器
            goods_list = product_list_page.locator(
            ".goods-list"
            )

            expect(goods_list).to_have_count(
            1,
            timeout=15000,
            )

        with allure.step("记录商品列表信息"):
            # 商品项可能因为分类暂无商品而为 0。
            # 当前第 10 条用例主要验证：
            #
            # 1. 分类跳转成功；
            # 2. 商品列表页面存在；
            # 3. 页面主要结构存在。
            #
            # 因此不强制要求商品数量必须大于 0。
            goods_items = product_list_page.locator(
                ".goods-item"
            )

            goods_count = goods_items.count()

            allure.attach(
                f"当前商品数量：{goods_count}",
                name="当前商品数量",
                attachment_type=allure.attachment_type.TEXT,
            )

            allure.attach(
                f"当前页面地址：{page.url}",
                name="商品列表页面地址",
                attachment_type=allure.attachment_type.TEXT,
            )

        with allure.step("保存商品列表页面截图"):
            self.save_screenshot(
                page=page,
                file_name=(
                    "portal_product_list_from_category.png"
                ),
                allure_name="从分类进入商品列表页面",
            )

    # ========================================================
    # 公共方法：保存截图并添加到 Allure
    # ========================================================

    @staticmethod
    def save_screenshot(
        page: Page,
        file_name: str,
        allure_name: str,
    ):
        """
        保存页面截图，并将截图添加到 Allure 报告。

        参数：
            page：
                Playwright 当前页面对象。

            file_name：
                截图文件名。

            allure_name：
                Allure 报告中显示的附件名称。
        """

        # 如果截图目录不存在，则自动创建。
        SCREENSHOT_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        screenshot_path = SCREENSHOT_DIR / file_name

        # 保存截图到本地目录。
        page.screenshot(
            path=str(screenshot_path),
            full_page=True,
        )

        # 将截图添加到 Allure 报告。
        screenshot_bytes = page.screenshot(
            full_page=True,
        )

        allure.attach(
            screenshot_bytes,
            name=allure_name,
            attachment_type=allure.attachment_type.PNG,
        )