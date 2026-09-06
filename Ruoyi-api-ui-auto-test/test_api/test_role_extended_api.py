"""
???????????

???????????????
- ???????
- ???????
- ?????
- ????????
- ????????????
- ?????????
"""

from __future__ import annotations

import allure
import pytest

from common.http_client import RuoYiApiError
from common.test_data import build_role_payload, build_unique_role


@pytest.mark.api
@allure.feature("??????")
class TestRoleExtendedApi:
    """?????????????????"""

    @allure.story("??????")
    def test_duplicate_role_name(self, role_api) -> None:
        first = build_unique_role()
        second = build_unique_role()
        second_payload = build_role_payload(second)
        second_payload["roleName"] = first.role_name

        try:
            assert role_api.add_role(build_role_payload(first))["code"] == 200
            with pytest.raises(RuoYiApiError, match="request failed"):
                role_api.add_role(second_payload)
        finally:
            role_api.cleanup_role_by_key(first.role_key)
            role_api.cleanup_role_by_key(second.role_key)

    @allure.story("??????")
    def test_duplicate_role_key(self, role_api) -> None:
        first = build_unique_role()
        second = build_unique_role()
        second_payload = build_role_payload(second)
        second_payload["roleKey"] = first.role_key

        try:
            assert role_api.add_role(build_role_payload(first))["code"] == 200
            with pytest.raises(RuoYiApiError, match="request failed"):
                role_api.add_role(second_payload)
        finally:
            role_api.cleanup_role_by_key(first.role_key)
            role_api.cleanup_role_by_key(second.role_key)

    @allure.story("????")
    def test_update_role(self, role_api) -> None:
        role = build_unique_role()
        try:
            assert role_api.add_role(build_role_payload(role))["code"] == 200
            role_id = role_api.find_role_ids(role_key=role.role_key)[0]
            new_name = f"{role.role_name}_???"
            result = role_api.update_role({
                "roleId": role_id,
                "roleName": new_name,
                "roleKey": role.role_key,
                "roleSort": 2,
                "status": "0",
                "remark": "???????",
                "menuCheckStrictly": True,
                "deptCheckStrictly": True,
                "menuIds": [],
            })
            assert result["code"] == 200
            detail = role_api.get_role_detail(role_id)
            assert detail["data"]["roleName"] == new_name
            assert detail["data"]["roleSort"] == 2
        finally:
            role_api.cleanup_role_by_key(role.role_key)

    @allure.story("???????")
    def test_assign_role_menus(self, role_api) -> None:
        role = build_unique_role()
        try:
            role_api.add_role(build_role_payload(role))
            role_id = role_api.find_role_ids(role_key=role.role_key)[0]
            assert role_api.assign_menus(role_id, [100, 1001])["code"] == 200
            tree = role_api.get_role_menu_tree(role_id)
            assert tree["code"] == 200
            assert 1001 in (tree.get("checkedKeys") or [])
        finally:
            role_api.cleanup_role_by_key(role.role_key)

    @allure.story("???????????")
    def test_assign_role_departments(self, role_api) -> None:
        role = build_unique_role()
        try:
            role_api.add_role(build_role_payload(role))
            role_id = role_api.find_role_ids(role_key=role.role_key)[0]
            result = role_api.assign_departments(role_id, [105])
            assert result["code"] == 200
            detail = role_api.get_role_detail(role_id)
            assert detail["data"]["dataScope"] == "2"
        finally:
            role_api.cleanup_role_by_key(role.role_key)

    @allure.story("????????")
    def test_delete_nonexistent_role(self, role_api) -> None:
        with pytest.raises(RuoYiApiError, match="request failed"):
            role_api.delete_role(999999)
