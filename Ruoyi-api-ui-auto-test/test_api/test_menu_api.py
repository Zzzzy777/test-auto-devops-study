"""
菜单接口测试。

对应旧项目中的 test_menu.py。
"""

import allure
import pytest


@pytest.mark.api
@allure.feature("菜单管理模块")
class TestMenuApi:
    """菜单管理接口测试类。"""

    @allure.story("查询菜单树")
    def test_query_menu_tree(
        self,
        system_api,
    ) -> None:
        """
        查询菜单树并验证返回结构。
        """
        result = system_api.get_menu_tree()

        assert result["code"] == 200

        # 不同 RuoYi 版本可能使用 data 或 rows，
        # 因此这里先兼容两种返回结构。
        assert (
            "data" in result
            or "rows" in result
        )