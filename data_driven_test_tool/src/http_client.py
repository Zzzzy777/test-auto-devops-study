# -*- coding: utf-8 -*-
"""
基于 requests 的轻量 HTTP 客户端封装。
只负责发请求、收集响应摘要，不做断言。
"""

import time

import requests


def send_request(case):
    """
    按用例字段发送一次 HTTP 请求。

    :param case: 标准化后的用例字典
    :return: 响应摘要字典（无论成功失败都返回，异常写入 error 字段）
    """
    started = time.time()
    result = {
        "ok": False,
        "elapsed_ms": 0,
        "status_code": None,
        "headers": {},
        "text": "",
        "json": None,
        "error": None,
    }

    try:
        response = requests.request(
            method=case["method"],
            url=case["url"],
            headers=case.get("headers") or None,
            params=case.get("params") or None,
            json=case.get("json_body") if case.get("json_body") is not None else None,
            data=case.get("data") if case.get("json_body") is None else None,
            timeout=case.get("timeout") or 15,
        )
        result["status_code"] = response.status_code
        result["headers"] = dict(response.headers)
        result["text"] = response.text or ""
        # 响应不一定是 JSON，解析失败时保持 json 为 None
        try:
            result["json"] = response.json()
        except ValueError:
            result["json"] = None
        result["ok"] = True
    except requests.RequestException as exc:
        result["error"] = "请求异常：%s" % exc
    finally:
        result["elapsed_ms"] = int((time.time() - started) * 1000)

    return result
