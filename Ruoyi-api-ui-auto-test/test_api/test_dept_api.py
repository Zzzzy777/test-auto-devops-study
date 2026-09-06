"""
部门接口测试。

对应旧项目中的 test_dept.py。
"""

import allure
import pytest


@pytest.mark.api
@allure.feature("部门管理模块")
class TestDeptApi:
    """部门管理接口测试类。"""

    @allure.story("查询部门列表")
    def test_query_dept_tree(
        self,
        system_api,
    ) -> None:
        """
        查询部门树形列表，
        并校验业务返回码和数据字段。
        """
        result = system_api.get_dept_tree()

        assert result["code"] == 200

        # RuoYi 不同版本可能返回 data 或 rows。
        assert (
            "data" in result
            or "rows" in result
        )