# -*- coding: utf-8 -*-
"""
响应断言引擎。
支持状态码、响应体包含、JSON 点路径取值比较。
"""


def run_assertions(case, response):
    """
    对单条用例执行 YAML 中声明的断言。

    支持的 assert 字段：
    - status_code: 200
    - body_contains: ["关键字", ...]
    - json_equals:
        args.foo: bar          # 点路径等于
    - json_contains:
        url: /get              # 点路径的字符串包含
    - headers:
        Content-Type: json     # 响应头包含指定子串（不区分大小写键名）

    :return: (是否全部通过, 失败原因列表)
    """
    failures = []
    expect = case.get("assert") or {}
    if not isinstance(expect, dict):
        return False, ["assert 节点必须是字典"]

    if response.get("error"):
        return False, [response["error"]]

    expected_status = expect.get("status_code")
    if expected_status is not None:
        actual = response.get("status_code")
        if actual != int(expected_status):
            failures.append("状态码期望 %s，实际 %s" % (expected_status, actual))

    for keyword in expect.get("body_contains") or []:
        keyword = str(keyword)
        if keyword not in (response.get("text") or ""):
            failures.append("响应体未包含：%s" % keyword)

    json_data = response.get("json")
    for path, value in (expect.get("json_equals") or {}).items():
        actual = extract_by_path(json_data, path)
        if _stringify(actual) != _stringify(value):
            failures.append("JSON 路径 %s 期望 %s，实际 %s" % (path, value, actual))

    for path, fragment in (expect.get("json_contains") or {}).items():
        actual = extract_by_path(json_data, path)
        if fragment is None or str(fragment) not in _stringify(actual):
            failures.append("JSON 路径 %s 未包含 %s，实际 %s" % (path, fragment, actual))

    expected_headers = expect.get("headers") or {}
    actual_headers = response.get("headers") or {}
    lowered = {str(k).lower(): str(v) for k, v in actual_headers.items()}
    for header_name, fragment in expected_headers.items():
        actual_value = lowered.get(str(header_name).lower(), "")
        if str(fragment) not in actual_value:
            failures.append(
                "响应头 %s 期望包含 %s，实际 %s" % (header_name, fragment, actual_value)
            )

    return len(failures) == 0, failures


def extract_by_path(data, path):
    """
    按点路径从嵌套 JSON 中取值，例如 args.foo 或 headers.Host。
    路径不存在时返回 None。
    """
    if data is None:
        return None
    current = data
    for part in str(path).split("."):
        if isinstance(current, dict) and part in current:
            current = current[part]
        elif isinstance(current, list) and part.isdigit():
            index = int(part)
            if index < 0 or index >= len(current):
                return None
            current = current[index]
        else:
            return None
    return current


def _stringify(value):
    """比较前统一转成字符串，避免 YAML 数字与 JSON 字符串类型不一致。"""
    if value is None:
        return "null"
    return str(value)
