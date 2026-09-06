"""
RuoYi 系统查询接口客户端。

当前用于封装：

- 菜单树查询；
- 部门树查询；
- 其他只读系统接口。
"""

from __future__ import annotations

from typing import Any

from common.config import (
    API_BASE_URL,
    API_PASSWORD,
    API_TIMEOUT,
    API_USERNAME,
)
from common.http_client import RuoYiHttpClient


class RuoYiSystemApi:
    """RuoYi 系统管理查询 API 客户端。"""

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

    def get_menu_tree(self) -> dict[str, Any]:
        """查询菜单树。"""
        return self.client.request_json(
            "GET",
            "/system/menu/treeselect",
        )

    def get_menu_list(self) -> dict[str, Any]:
        """查询菜单列表。"""
        return self.client.request_json(
            "GET",
            "/system/menu/list",
        )

    def get_dept_tree(self) -> dict[str, Any]:
        """查询部门树。"""
        return self.client.request_json(
            "GET",
            "/system/dept/list",
        )

    def get_role_menu_tree(self, role_id: int) -> dict[str, Any]:
        """?????????????????"""
        return self.client.request_json(
            "GET",
            f"/system/menu/roleMenuTreeselect/{role_id}",
        )
