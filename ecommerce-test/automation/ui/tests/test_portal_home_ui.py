"""
商城前台首页 UI 自动化测试。

测试页面：
http://localhost:8060/#/

测试范围：
1. 首页正常打开；
2. 首页标题校验；
3. 首页核心模块展示；
4. 首页商品数据展示；
5. 底部导航展示；
6. 首页截图保存；
7. 生成 Allure 测试结果。
"""

from pathlib import Path

import allure
import pytest
from playwright.sync_api import Page, expect


# ============================================================
# 基础配置
# ============================================================

# 商城首页地址
HOME_URL = "http://localhost:8060/#/"

# 截图目录
SCREENSHOT_DIR = Path("screenshots")


# ============================================================
# 公共方法
# ============================================================

def open_home_page(page: Page) -> None:
    """
    打开商城前台首页。

    参数：
        page：Playwright 页面对象
    """

    # 设置 Playwright 默认操作超时时间
    page.set_default_timeout(15000)

    # 创建截图目录
    SCREENSHOT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # 打开商城首页
    page.goto(
        HOME_URL,
        wait_until="domcontentloaded",
    )

    # 获取首页主体
    home_page = page.locator(
        "uni-page[data-page='pages/index/index']"
    )

    # 等待首页主体显示
    home_page.wait_for(
        state="visible",
        timeout=15000,
    )

    # 等待首页接口数据加载
    page.wait_for_timeout(2000)


def get_home_page(page: Page):
    """
    获取商城首页主体元素。
    """

    return page.locator(
        "uni-page[data-page='pages/index/index']"
    )


def save_screenshot(
    page: Page,
    file_name: str,
) -> None:
    """
    保存首页截图。

    参数：
        page：Playwright 页面对象；
        file_name：截图文件名。
    """

    # 确保目录存在
    SCREENSHOT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # 保存全页面截图
    page.screenshot(
        path=str(
            SCREENSHOT_DIR / file_name
        ),
        full_page=True,
    )


# ============================================================
# 测试用例 1：首页正常打开及核心模块展示
# ============================================================

@pytest.mark.smoke
@pytest.mark.portal
@allure.epic("商城前台 UI 自动化测试")
@allure.feature("商城首页模块")
@allure.story("商城首页正常展示")
@allure.title("商城首页可以正常打开并展示核心内容")
def test_portal_home_page_display(page: Page):
    """
    验证商城首页可以正常打开并展示核心内容。

    测试步骤：
    1. 打开商城首页；
    2. 校验页面标题；
    3. 校验首页主体存在；
    4. 校验首页核心模块；
    5. 校验商品数据；
    6. 校验底部导航；
    7. 保存首页截图。
    """

    # ========================================================
    # 1. 打开商城首页
    # ========================================================

    with allure.step("打开商城前台首页"):
        open_home_page(page)

        # 输出当前页面信息
        print("商城首页地址：", page.url)
        print("商城首页标题：", page.title())

    # 获取首页主体
    home_page = get_home_page(page)

    # ========================================================
    # 2. 页面标题校验
    # ========================================================

    with allure.step("校验商城首页标题"):
        expect(page).to_have_title("Mall商城")

    # ========================================================
    # 3. 首页主体校验
    # ========================================================

    with allure.step("校验商城首页主体"):
        expect(home_page).to_be_visible()

        # 首页正文不能为空
        home_text = home_page.inner_text()

        print("商城首页页面文本：")
        print(home_text[:2000])

        assert home_text.strip(), (
            "商城首页没有展示任何页面内容"
        )

    # ========================================================
    # 4. 首页功能分类校验
    # ========================================================

    with allure.step("校验首页功能分类"):
        # 首页源码中的功能分类：
        # 专题、话题、优选、特惠
        category_section = home_page.locator(
            ".cate-section"
        )

        expect(category_section).to_be_visible()

        expect(
            category_section.get_by_text(
                "专题",
                exact=True,
            )
        ).to_be_visible()

        expect(
            category_section.get_by_text(
                "话题",
                exact=True,
            )
        ).to_be_visible()

        expect(
            category_section.get_by_text(
                "优选",
                exact=True,
            )
        ).to_be_visible()

        expect(
            category_section.get_by_text(
                "特惠",
                exact=True,
            )
        ).to_be_visible()

    # ========================================================
    # 5. 品牌制造商模块校验
    # ========================================================

    with allure.step("校验品牌制造商直供模块"):
        brand_header = home_page.locator(
            ".f-header"
        ).filter(
            has_text="品牌制造商直供"
        )

        expect(brand_header).to_be_visible()

        expect(
            brand_header.get_by_text(
                "品牌制造商直供",
                exact=True,
            )
        ).to_be_visible()

        expect(
            brand_header.get_by_text(
                "工厂直达消费者，剔除品牌溢价",
                exact=True,
            )
        ).to_be_visible()

        # 第一个 guess-section 对应品牌列表
        brand_list = home_page.locator(
            ".guess-section"
        ).nth(0)

        expect(brand_list).to_be_visible()

        # 至少展示一个品牌
        brand_count = brand_list.locator(
            ".guess-item"
        ).count()

        print("首页品牌数量：", brand_count)

        assert brand_count > 0, (
            "首页品牌制造商模块没有展示品牌数据"
        )

    # ========================================================
    # 6. 新鲜好物模块校验
    # ========================================================

    with allure.step("校验新鲜好物模块"):
        new_product_header = home_page.locator(
            ".f-header"
        ).filter(
            has_text="新鲜好物"
        )

        expect(new_product_header).to_be_visible()

        expect(
            new_product_header.get_by_text(
                "新鲜好物",
                exact=True,
            )
        ).to_be_visible()

        expect(
            new_product_header.get_by_text(
                "为你寻觅世间好物",
                exact=True,
            )
        ).to_be_visible()

        # 新鲜好物商品使用 .floor-item
        new_product_list = home_page.locator(
            ".floor-list .floor-item"
        )

        new_product_count = new_product_list.count()

        print(
            "新鲜好物商品数量：",
            new_product_count,
        )

        assert new_product_count > 0, (
            "新鲜好物模块没有展示商品数据"
        )

    # ========================================================
    # 7. 人气推荐模块校验
    # ========================================================

    with allure.step("校验人气推荐模块"):
        hot_header = home_page.locator(
            ".f-header"
        ).filter(
            has_text="人气推荐"
        )

        expect(hot_header).to_be_visible()

        expect(
            hot_header.get_by_text(
                "人气推荐",
                exact=True,
            )
        ).to_be_visible()

        expect(
            hot_header.get_by_text(
                "大家都赞不绝口的",
                exact=True,
            )
        ).to_be_visible()

        # 人气推荐商品列表
        hot_product_list = home_page.locator(
            ".hot-section .guess-item"
        )

        hot_product_count = hot_product_list.count()

        print(
            "人气推荐商品数量：",
            hot_product_count,
        )

        assert hot_product_count > 0, (
            "人气推荐模块没有展示商品数据"
        )

    # ========================================================
    # 8. 猜你喜欢模块校验
    # ========================================================

    with allure.step("校验猜你喜欢模块"):
        recommend_header = home_page.locator(
            ".f-header"
        ).filter(
            has_text="猜你喜欢"
        )

        expect(recommend_header).to_be_visible()

        expect(
            recommend_header.get_by_text(
                "猜你喜欢",
                exact=True,
            )
        ).to_be_visible()

        expect(
            recommend_header.get_by_text(
                "你喜欢的都在这里了",
                exact=True,
            )
        ).to_be_visible()

    # ========================================================
    # 9. 底部导航校验
    # ========================================================

    with allure.step("校验底部导航栏"):
        # uni-app H5 的底部导航栏
        tabbar = page.locator(
            "uni-tabbar"
        )

        expect(tabbar).to_be_visible()

        # 校验首页导航
        expect(
            tabbar.get_by_text(
                "首页",
                exact=True,
            )
        ).to_be_visible()

        # 校验分类导航
        expect(
            tabbar.get_by_text(
                "分类",
                exact=True,
            )
        ).to_be_visible()

        # 校验购物车导航
        expect(
            tabbar.get_by_text(
                "购物车",
                exact=True,
            )
        ).to_be_visible()

        # 校验我的导航
        expect(
            tabbar.get_by_text(
                "我的",
                exact=True,
            )
        ).to_be_visible()

    # ========================================================
    # 10. 首页截图
    # ========================================================

    with allure.step("保存商城首页截图"):
        save_screenshot(
            page,
            "portal-home-page-display.png",
        )

    # 输出测试结果
    print("商城首页核心模块校验通过")