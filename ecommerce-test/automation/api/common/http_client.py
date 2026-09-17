"""
HTTP 请求公共封装。

后续所有接口测试都通过这个类发送请求，
这样可以统一处理超时时间、请求头和响应结果。
"""

from typing import Any, Dict, Optional

import requests


class HttpClient:
    """项目接口请求客户端。"""

    def __init__(self, timeout: int = 15):
        self.timeout = timeout
        self.session = requests.Session()

    def request(
        self,
        method: str,
        url: str,
        *,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
    ) -> requests.Response:
        """
        发送 HTTP 请求。

        注意：
        这里暂时不直接 raise_for_status，
        因为登录失败、Token 失效等场景本身就是需要验证的测试场景。
        """

        response = self.session.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            data=data,
            json=json,
            timeout=self.timeout,
        )

        return response

    @staticmethod
    def json_body(response: requests.Response) -> Dict[str, Any]:
        """安全读取 JSON 响应。"""

        try:
            return response.json()
        except ValueError:
            return {
                "raw_text": response.text,
            }