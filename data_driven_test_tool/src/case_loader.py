# -*- coding: utf-8 -*-
"""
把 YAML 解析结果转换成结构化用例。
这里只做字段校验与默认值填充，不再依赖任何 YAML 测试插件。
"""

from src.yaml_parser import load_yaml_file


class CaseLoadError(ValueError):
    """用例文件结构不合法时抛出。"""


def load_test_suite(yaml_path):
    """
    加载一套接口测试用例。

    期望 YAML 结构：
    config:
      base_url: https://httpbin.org
      timeout: 15
    cases:
      - name: 用例名
        method: GET
        path: /get
        ...

    :param yaml_path: YAML 文件路径
    :return: dict，包含 config 与标准化后的 cases 列表
    """
    data = load_yaml_file(yaml_path)
    if not isinstance(data, dict):
        raise CaseLoadError("YAML 根节点必须是字典")

    config = data.get("config") or {}
    if not isinstance(config, dict):
        raise CaseLoadError("config 必须是字典")

    base_url = str(config.get("base_url") or "").rstrip("/")
    timeout = config.get("timeout", 15)
    try:
        timeout = float(timeout)
    except (TypeError, ValueError):
        raise CaseLoadError("config.timeout 必须是数字")

    raw_cases = data.get("cases")
    if not isinstance(raw_cases, list) or not raw_cases:
        raise CaseLoadError("cases 必须是非空列表")

    cases = []
    for index, item in enumerate(raw_cases, start=1):
        cases.append(_normalize_case(item, index, base_url, timeout))

    return {
        "source": yaml_path,
        "config": {
            "base_url": base_url,
            "timeout": timeout,
        },
        "cases": cases,
    }


def _normalize_case(item, index, base_url, default_timeout):
    """把单条 YAML 用例规范成运行器可直接使用的字典。"""
    if not isinstance(item, dict):
        raise CaseLoadError("第 %s 条用例必须是字典" % index)

    name = str(item.get("name") or "未命名用例-%s" % index).strip()
    method = str(item.get("method") or "GET").strip().upper()
    path = str(item.get("path") or item.get("url") or "").strip()
    if path == "":
        raise CaseLoadError("用例 [%s] 缺少 path 或 url" % name)

    # 既支持相对 path（拼 base_url），也支持写完整 http(s) 地址
    if path.startswith("http://") or path.startswith("https://"):
        url = path
    else:
        if not path.startswith("/"):
            path = "/" + path
        if base_url == "":
            raise CaseLoadError("用例 [%s] 使用相对路径时必须配置 base_url" % name)
        url = base_url + path

    timeout = item.get("timeout", default_timeout)
    try:
        timeout = float(timeout)
    except (TypeError, ValueError):
        raise CaseLoadError("用例 [%s] 的 timeout 必须是数字" % name)

    return {
        "id": index,
        "name": name,
        "method": method,
        "url": url,
        "headers": item.get("headers") or {},
        "params": item.get("params") or {},
        "json_body": item.get("json") if item.get("json") is not None else item.get("body"),
        "data": item.get("data"),
        "timeout": timeout,
        "assert": item.get("assert") or {},
    }
