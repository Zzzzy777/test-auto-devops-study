"""???????????"""

from __future__ import annotations

import allure
import pytest

from common.config import API_BASE_URL
from common.http_client import RuoYiHttpClient


@pytest.mark.api
@allure.feature("??????")
class TestPermissionExtendedApi:
    """????? Token ????????????????????"""

    @allure.story("??????????")
    def test_admin_access_protected_user_api(self) -> None:
        client = RuoYiHttpClient(base_url=API_BASE_URL)
        result = client.request_json(
            "GET",
            "/system/user/list",
            params={"pageNum": 1, "pageSize": 1},
        )
        assert result["code"] == 200
        assert isinstance(result.get("rows"), list)

    @allure.story("?????????")
    def test_role_menu_permission_tree(self, role_api) -> None:
        # ??????????????????????? checkedKeys?
        from common.test_data import build_role_payload, build_unique_role

        role = build_unique_role()
        try:
            role_api.add_role(build_role_payload(role))
            role_id = role_api.find_role_ids(role_key=role.role_key)[0]
            role_api.assign_menus(role_id, [1001])
            tree = role_api.get_role_menu_tree(role_id)
            assert tree["code"] == 200
            assert 1001 in (tree.get("checkedKeys") or [])
        finally:
            role_api.cleanup_role_by_key(role.role_key)
