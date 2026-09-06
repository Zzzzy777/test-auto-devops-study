"""
RuoYi 角色管理 API 客户端。

对应旧项目中的：

- test_role.py
- test_business_link.py
"""

from __future__ import annotations

from typing import Any

from common.config import (
    API_BASE_URL,
    API_PASSWORD,
    API_TIMEOUT,
    API_USERNAME,
)
from common.http_client import (
    RuoYiApiError,
    RuoYiHttpClient,
)


class RuoYiRoleApi:
    """RuoYi 角色管理模块 API 客户端。"""

    def __init__(
        self,
        base_url: str = API_BASE_URL,
        username: str = API_USERNAME,
        password: str = API_PASSWORD,
        timeout: int = API_TIMEOUT,
    ) -> None:
        self.client = RuoYiHttpClient(
            base_url=base_url,
            username=username,
            password=password,
            timeout=timeout,
        )

    def list_roles(
        self,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """查询角色列表。"""
        return self.client.request_json(
            "GET",
            "/system/role/list",
            params=params or {},
        )

    def find_role_ids(
        self,
        *,
        role_key: str | None = None,
        role_name: str | None = None,
    ) -> list[int]:
        """
        根据 roleKey 或 roleName 查询角色 ID。
        """
        params: dict[str, Any] = {
            "pageNum": 1,
            "pageSize": 100,
        }

        if role_key:
            params["roleKey"] = role_key

        if role_name:
            params["roleName"] = role_name

        result = self.list_roles(params)
        rows = result.get("rows") or []

        role_ids: list[int] = []

        for row in rows:
            if not isinstance(row, dict):
                continue

            if role_key and row.get("roleKey") != role_key:
                continue

            if role_name and row.get("roleName") != role_name:
                continue

            role_id = row.get("roleId")
            if role_id is not None:
                role_ids.append(int(role_id))

        return role_ids

    def add_role(
        self,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        """新增角色。"""
        return self.client.request_json(
            "POST",
            "/system/role",
            json=payload,
        )

    def get_role_detail(
        self,
        role_id: int,
    ) -> dict[str, Any]:
        """查询角色详情。"""
        return self.client.request_json(
            "GET",
            f"/system/role/{role_id}",
        )

    def update_role(
        self,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        """修改角色。"""
        return self.client.request_json(
            "PUT",
            "/system/role",
            json=payload,
        )

    def delete_role(
        self,
        role_id: int,
    ) -> dict[str, Any]:
        """删除角色。"""
        return self.client.request_json(
            "DELETE",
            f"/system/role/{role_id}",
        )

    def assign_menus(
        self,
        role_id: int,
        menu_ids: list[int],
    ) -> dict[str, Any]:
        """????????

        RuoYi 3.9.x ????? /system/role/menu ?????
        ?????? PUT /system/role ????????????
        ??????????????? menuIds??????????
        """
        detail_result = self.get_role_detail(role_id)
        detail = detail_result.get("data") or {}

        if not isinstance(detail, dict):
            raise RuoYiApiError(
                f"?????????role_id={role_id}, data={detail}"
            )

        payload = {
            "roleId": role_id,
            "roleName": detail.get("roleName", ""),
            "roleKey": detail.get("roleKey", ""),
            "roleSort": detail.get("roleSort", 1),
            "status": detail.get("status", "0"),
            "remark": detail.get("remark") or "",
            "menuCheckStrictly": detail.get("menuCheckStrictly", True),
            "deptCheckStrictly": detail.get("deptCheckStrictly", True),
            "menuIds": menu_ids,
        }
        return self.update_role(payload)

    def get_role_menu_tree(
        self,
        role_id: int,
    ) -> dict[str, Any]:
        """??????????????? ID?"""
        return self.client.request_json(
            "GET",
            f"/system/menu/roleMenuTreeselect/{role_id}",
        )

    def assign_departments(
        self,
        role_id: int,
        dept_ids: list[int],
        *,
        data_scope: str = "2",
    ) -> dict[str, Any]:
        """????????????

        dataScope=2 ???????????????? deptIds ???
        """
        return self.client.request_json(
            "PUT",
            "/system/role/dataScope",
            json={
                "roleId": role_id,
                "dataScope": data_scope,
                "deptIds": dept_ids,
            },
        )

    def cleanup_role_by_key(
        self,
        role_key: str,
    ) -> dict[str, Any]:
        """
        根据唯一 roleKey 清理测试角色。

        只允许清理 api_test_role_ 开头的数据。
        """
        if not role_key.startswith("api_test_role_"):
            raise ValueError(
                "拒绝清理非测试角色，roleKey 必须以 "
                "api_test_role_ 开头。"
            )

        role_ids = self.find_role_ids(role_key=role_key)
        deleted_ids: list[int] = []

        for role_id in role_ids:
            self.delete_role(role_id)
            deleted_ids.append(role_id)

        remaining_ids = self.find_role_ids(role_key=role_key)

        if remaining_ids:
            raise RuoYiApiError(
                "角色清理失败："
                f"role_key={role_key}, "
                f"remaining_ids={remaining_ids}"
            )

        return {
            "role_key": role_key,
            "found_ids": role_ids,
            "deleted_ids": deleted_ids,
            "remaining_ids": remaining_ids,
            "status": (
                "clean"
                if deleted_ids
                else "already_clean"
            ),
        }