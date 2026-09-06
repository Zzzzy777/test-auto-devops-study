"""
RuoYi 用户管理 API 客户端。

这里只放用户领域接口。
底层 HTTP、Token、401 重试等通用能力由 http_client.py 提供。
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


class RuoYiUserApi:
    """RuoYi 用户管理模块 API 客户端。"""

    def __init__(
        self,
        base_url: str = API_BASE_URL,
        username: str = API_USERNAME,
        password: str = API_PASSWORD,
        timeout: int = API_TIMEOUT,
    ) -> None:
        # 用户模块复用通用 HTTP 客户端
        self.client = RuoYiHttpClient(
            base_url=base_url,
            username=username,
            password=password,
            timeout=timeout,
        )

    @property
    def token(self) -> str | None:
        """读取当前 Token，供鉴权测试使用。"""
        return self.client.token

    @token.setter
    def token(self, value: str | None) -> None:
        """设置或清空当前 Token。"""
        self.client.token = value

    def login(self) -> dict[str, Any]:
        """调用登录接口，返回登录结果。"""
        return self.client.login()

    def add_user(
        self,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        """新增用户。"""
        return self.client.request_json(
            "POST",
            "/system/user",
            json=payload,
        )

    def get_user_list(
        self,
        params: dict[str, Any] | None = None,
        *,
        auth: bool = True,
        retry_on_401: bool = True,
    ) -> dict[str, Any]:
        """
        查询用户列表。

        auth=True 会自动携带 Token；auth=False 明确不登录、不添加 Token。
        retry_on_401=False 用于验证失效 Token，避免客户端自动重新登录。
        """
        return self.client.request_json(
            "GET",
            "/system/user/list",
            params=params or {},
            auth=auth,
            retry_on_401=retry_on_401,
        )

    def get_list_user(
        self,
        params: dict[str, Any] | None = None,
        *,
        auth: bool = True,
        retry_on_401: bool = True,
    ) -> dict[str, Any]:
        """兼容旧测试代码中的方法名。"""
        return self.get_user_list(
            params=params,
            auth=auth,
            retry_on_401=retry_on_401,
        )

    def find_user_ids(
        self,
        username: str,
    ) -> list[int]:
        """
        根据精确用户名查询用户 ID。

        只返回 userName 完全匹配的记录，
        避免模糊查询误匹配其他测试数据。
        """
        result = self.get_user_list(
            {
                "userName": username,
                "pageNum": 1,
                "pageSize": 100,
            }
        )

        rows = result.get("rows") or []
        user_ids: list[int] = []

        for row in rows:
            if not isinstance(row, dict):
                continue

            if row.get("userName") != username:
                continue

            user_id = row.get("userId")
            if user_id is not None:
                user_ids.append(int(user_id))

        return user_ids

    def get_user_detail(
        self,
        user_id: int,
    ) -> dict[str, Any]:
        """查询用户详情。"""
        return self.client.request_json(
            "GET",
            f"/system/user/{user_id}",
        )

    def update_user(
        self,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        """修改用户。"""
        return self.client.request_json(
            "PUT",
            "/system/user",
            json=payload,
        )

    def delete_user(
        self,
        user_id: int,
    ) -> dict[str, Any]:
        """删除用户。"""
        return self.client.request_json(
            "DELETE",
            f"/system/user/{user_id}",
        )

    def change_status(
        self,
        user_id: int,
        status: str,
    ) -> dict[str, Any]:
        """????????status=0 ???status=1 ???"""
        return self.client.request_json(
            "PUT",
            "/system/user/changeStatus",
            json={
                "userId": user_id,
                "status": status,
            },
        )

    def cleanup_user_by_username(
        self,
        username: str,
    ) -> dict[str, Any]:
        """
        清理自动化创建的测试用户。

        为了防止误删真实用户，只允许清理指定前缀的数据。
        """
        safe_prefixes = (
            "ui_test_",
            "api_test_",
        )

        if not username.startswith(safe_prefixes):
            raise ValueError(
                "拒绝清理非测试用户，用户名必须以 "
                "ui_test_ 或 api_test_ 开头。"
            )

        user_ids = self.find_user_ids(username)
        deleted_ids: list[int] = []

        for user_id in user_ids:
            self.delete_user(user_id)
            deleted_ids.append(user_id)

        # 删除后再次查询，确认数据确实不存在
        remaining_ids = self.find_user_ids(username)

        if remaining_ids:
            raise RuoYiApiError(
                "用户清理失败："
                f"username={username}, "
                f"remaining_ids={remaining_ids}"
            )

        return {
            "username": username,
            "found_ids": user_ids,
            "deleted_ids": deleted_ids,
            "remaining_ids": remaining_ids,
            "status": (
                "clean"
                if deleted_ids
                else "already_clean"
            ),
        }


__all__ = [
    "RuoYiApiError",
    "RuoYiUserApi",
]