# -*- coding: utf-8 -*-
"""
RuoYi 通用 HTTP 客户端。

职责：

1. 管理 Requests Session；
2. 统一处理 API 地址；
3. 统一处理 Token；
4. 统一设置超时时间；
5. 遇到 401 自动重新登录；
6. 提供原始 Response 和 JSON 两种调用方式；
7. 统一处理网络异常和业务错误。
"""

from __future__ import annotations

from typing import Any

import requests

from common.config import (
    API_BASE_URL,
    API_PASSWORD,
    API_TIMEOUT,
    API_USERNAME,
)


class RuoYiApiError(RuntimeError):
    """
    RuoYi API 业务异常。

    当登录失败、响应格式异常或业务 code 不符合预期时抛出。
    """


class RuoYiHttpClient:
    """
    RuoYi 通用接口客户端。

    测试用例不应该直接到处使用 requests.request，
    而是通过这个客户端统一发送请求。
    """

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

        # 使用 Session 可以复用 TCP 连接，
        # 也可以统一管理请求头和 Cookie。
        self.session = requests.Session()

        # Token 初始为空，第一次访问需要鉴权的接口时自动登录。
        self._token: str | None = None

    @property
    def token(self) -> str | None:
        """返回当前 Token。"""
        return self._token

    @token.setter
    def token(self, value: str | None) -> None:
        """
        设置当前 Token。

        鉴权异常测试可以注入伪造 Token，
        也可以传入 None 清空 Token。
        """
        self._token = value

    def _build_url(self, path: str) -> str:
        """
        将相对路径转换为完整 URL。

        例如：
        /login
        -> http://localhost:8081/login
        """
        if path.startswith("http://") or path.startswith("https://"):
            return path

        if not path.startswith("/"):
            path = f"/{path}"

        return f"{self.base_url}{path}"

    @staticmethod
    def _parse_json(response: requests.Response) -> dict[str, Any]:
        """
        解析 JSON 响应，并确保响应格式是字典。
        """
        try:
            data = response.json()
        except ValueError as exc:
            raise RuoYiApiError(
                "RuoYi API 返回的内容不是合法 JSON："
                f"{response.text[:300]}"
            ) from exc

        if not isinstance(data, dict):
            raise RuoYiApiError(
                f"RuoYi API 返回的数据不是对象：{data!r}"
            )

        return data

    def login(self) -> dict[str, Any]:
        """
        调用登录接口并保存 Token。
        """
        login_url = self._build_url("/login")

        try:
            response = self.session.post(
                login_url,
                json={
                    "username": self.username,
                    "password": self.password,
                },
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            raise RuoYiApiError(
                f"登录接口网络异常：{login_url}"
            ) from exc

        data = self._parse_json(response)

        # RuoYi 通常 HTTP 200 也可能代表业务失败，
        # 所以 HTTP 状态码和业务 code 都需要校验。
        if response.status_code != 200:
            raise RuoYiApiError(
                f"login failed: HTTP {response.status_code}, data={data}"
            )

        if data.get("code") != 200:
            raise RuoYiApiError(
                f"login failed: {data.get('msg', data)}"
            )

        token = data.get("token")

        if not token:
            raise RuoYiApiError(
                f"login failed: response does not contain token: {data}"
            )

        self._token = str(token)

        return data

    def _build_headers(
        self,
        auth: bool,
        custom_headers: dict[str, str] | None,
    ) -> dict[str, str]:
        """
        组装请求头。

        custom_headers 的优先级高于默认请求头。
        """
        headers: dict[str, str] = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        if auth:
            if not self._token:
                self.login()

            headers["Authorization"] = f"Bearer {self._token}"

        if custom_headers:
            headers.update(custom_headers)

        return headers

    def request_raw(
        self,
        method: str,
        path: str,
        *,
        auth: bool = True,
        retry_on_401: bool = True,
        **kwargs: Any,
    ) -> requests.Response:
        """
        发送原始 HTTP 请求，返回 requests.Response。

        auth=True：
            自动带 Token。

        auth=False：
            不自动登录，也不自动添加 Token，
            适用于无 Token 权限测试。

        retry_on_401=True：
            第一次收到 401 后自动重新登录并重试一次。
        """
        url = self._build_url(path)

        custom_headers = kwargs.pop("headers", None)
        timeout = kwargs.pop("timeout", self.timeout)

        headers = self._build_headers(
            auth=auth,
            custom_headers=custom_headers,
        )

        try:
            response = self.session.request(
                method=method.upper(),
                url=url,
                headers=headers,
                timeout=timeout,
                **kwargs,
            )
        except requests.RequestException as exc:
            raise RuoYiApiError(
                f"接口网络异常：{method.upper()} {url}"
            ) from exc

        # 401 通常代表 Token 过期或 Token 无效。
        # 自动重新登录后只重试一次，避免无限重试。
        if (
            auth
            and retry_on_401
            and response.status_code == 401
        ):
            self._token = None
            self.login()

            return self.request_raw(
                method,
                path,
                auth=True,
                retry_on_401=False,
                headers=custom_headers,
                timeout=timeout,
                **kwargs,
            )

        return response

    def request_json(
        self,
        method: str,
        path: str,
        *,
        expected_code: int | None = 200,
        auth: bool = True,
        retry_on_401: bool = True,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        发送接口请求，并返回 JSON 字典。

        expected_code=200：
            默认要求 RuoYi 业务 code 为 200。

        expected_code=None：
            只解析 JSON，不校验业务 code。
        """
        response = self.request_raw(
            method,
            path,
            auth=auth,
            retry_on_401=retry_on_401,
            **kwargs,
        )

        data = self._parse_json(response)

        if response.status_code >= 400:
            raise RuoYiApiError(
                f"request failed: HTTP {response.status_code}, "
                f"{method.upper()} {path}, data={data}"
            )

        if (
            expected_code is not None
            and data.get("code") != expected_code
        ):
            raise RuoYiApiError(
                f"request failed: {method.upper()} {path}, "
                f"data={data}"
            )

        return data

    def close(self) -> None:
        """关闭 Session。"""
        self.session.close()