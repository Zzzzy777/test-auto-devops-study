"""
角色管理接口测试。

对应旧项目中的 test_role.py。
"""

from __future__ import annotations

import allure
import pytest

from common.test_data import build_role_payload, build_unique_role


@pytest.mark.api
@allure.feature("角色管理模块")
class TestRoleApi:
    """角色管理 API 测试类。"""

    @allure.story("查询角色列表")
    def test_list_roles(
        self,
        role_api,
    ) -> None:
        """查询角色列表并校验 rows 字段。"""
        result = role_api.list_roles()

        assert result["code"] == 200
        assert "rows" in result
        assert isinstance(
            result["rows"],
            list,
        )

    @allure.story("新增角色并查询")
    def test_add_and_query_role(
        self,
        role_api,
    ) -> None:
        """
        新增角色后，根据 roleKey 查询，
        再查询角色详情。
        """
        role = build_unique_role()

        try:
            result = role_api.add_role(
                build_role_payload(role)
            )

            assert result["code"] == 200

            role_ids = role_api.find_role_ids(
                role_key=role.role_key
            )

            assert len(role_ids) == 1

            detail = role_api.get_role_detail(
                role_ids[0]
            )

            assert detail["code"] == 200

        finally:
            role_api.cleanup_role_by_key(
                role.role_key
            )

    @allure.story("角色业务链路")
    def test_role_business_flow(
        self,
        role_api,
    ) -> None:
        """
        角色新增 -> 查询 -> 查询详情 -> 删除 -> 删除后校验。
        """
        role = build_unique_role()
        role_id = None

        try:
            role_api.add_role(
                build_role_payload(role)
            )

            role_ids = role_api.find_role_ids(
                role_key=role.role_key
            )

            assert len(role_ids) == 1
            role_id = role_ids[0]

            detail = role_api.get_role_detail(
                role_id
            )

            assert detail["code"] == 200

        finally:
            role_api.cleanup_role_by_key(
                role.role_key
            )

        assert role_id is not None