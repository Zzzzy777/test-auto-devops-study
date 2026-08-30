from __future__ import annotations

from typing import Any

import requests

from common.config import API_BASE_URL, API_PASSWORD, API_TIMEOUT, API_USERNAME


class RuoYiApiError(RuntimeError):
    """Raised when the RuoYi API returns an unusable response."""


class RuoYiUserApi:
    """Small API client used to clean up users created by the UI test."""

    def __init__(
        self,
        base_url: str = API_BASE_URL,
        username: str = API_USERNAME,
        password: str = API_PASSWORD,
        timeout: int = API_TIMEOUT,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.username = username
        self.password = password
        self.timeout = timeout
        self.session = requests.Session()
        self._token: str | None = None

    def login(self) -> dict[str, Any]:
        response = self.session.post(
            f"{self.base_url}/login",
            json={"username": self.username, "password": self.password},
            timeout=self.timeout,
        )
        response.raise_for_status()
        data = self._json(response)
        token = data.get("token")
        if data.get("code") != 200 or not token:
            raise RuoYiApiError(f"RuoYi login failed: {data}")

        self._token = str(token)
        self.session.headers.update({"Authorization": f"Bearer {self._token}"})
        return data

    def _json(self, response: requests.Response) -> dict[str, Any]:
        try:
            data = response.json()
        except ValueError as exc:
            raise RuoYiApiError(
                f"RuoYi API returned non-JSON response: {response.text[:300]}"
            ) from exc
        if not isinstance(data, dict):
            raise RuoYiApiError(f"RuoYi API returned unexpected JSON: {data!r}")
        return data

    def _request(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        if self._token is None:
            self.login()

        kwargs.setdefault("timeout", self.timeout)
        response = self.session.request(method, f"{self.base_url}{path}", **kwargs)
        if response.status_code == 401:
            self.login()
            response = self.session.request(method, f"{self.base_url}{path}", **kwargs)

        response.raise_for_status()
        data = self._json(response)
        if data.get("code") != 200:
            raise RuoYiApiError(f"RuoYi API request failed: {method} {path}: {data}")
        return data

    def find_user_ids(self, username: str) -> list[int]:
        """Return IDs whose username exactly equals ``username``."""
        data = self._request(
            "GET",
            "/system/user/list",
            params={"userName": username, "pageNum": 1, "pageSize": 100},
        )
        rows = data.get("rows") or []
        user_ids: list[int] = []
        for row in rows:
            if not isinstance(row, dict) or row.get("userName") != username:
                continue
            user_id = row.get("userId")
            if user_id is not None:
                user_ids.append(int(user_id))
        return user_ids

    def delete_user(self, user_id: int) -> dict[str, Any]:
        return self._request("DELETE", f"/system/user/{user_id}")

    def cleanup_user_by_username(self, username: str) -> dict[str, Any]:
        """Delete only a generated UI-test user and verify that no copy remains.

        The prefix guard is intentional: it prevents a mistaken cleanup call from
        deleting a real account. The UI test generates names as ``ui_test_<uuid>``.
        """
        if not username.startswith("ui_test_"):
            raise ValueError(
                "Refusing cleanup for a non-test username; expected prefix 'ui_test_'."
            )

        user_ids = self.find_user_ids(username)
        deleted_ids: list[int] = []
        for user_id in user_ids:
            self.delete_user(user_id)
            deleted_ids.append(user_id)

        remaining_ids = self.find_user_ids(username)
        if remaining_ids:
            raise RuoYiApiError(
                f"Cleanup verification failed for {username}: remaining IDs {remaining_ids}"
            )

        return {
            "username": username,
            "found_ids": user_ids,
            "deleted_ids": deleted_ids,
            "remaining_ids": remaining_ids,
            "status": "clean" if deleted_ids else "already_clean",
        }