# -*- coding: utf-8 -*-
"""
用例执行器：按顺序批量跑接口、做断言、汇总成功/失败数量。
"""

from datetime import datetime

from src.asserter import run_assertions
from src.http_client import send_request


def run_suite(suite):
    """
    执行一整套用例。

    :param suite: case_loader.load_test_suite 的返回值
    :return: 可供 HTML 看板使用的汇总结果
    """
    started_at = datetime.now()
    records = []
    passed = 0
    failed = 0

    for case in suite["cases"]:
        response = send_request(case)
        ok, failures = run_assertions(case, response)
        if ok:
            passed += 1
            status_text = "成功"
        else:
            failed += 1
            status_text = "失败"

        # 看板里只展示截断后的响应体，避免页面过大
        body_preview = (response.get("text") or "")[:500]
        records.append(
            {
                "id": case["id"],
                "name": case["name"],
                "method": case["method"],
                "url": case["url"],
                "status_code": response.get("status_code"),
                "elapsed_ms": response.get("elapsed_ms"),
                "ok": ok,
                "status_text": status_text,
                "failures": failures,
                "body_preview": body_preview,
            }
        )
        _print_case_line(records[-1])

    finished_at = datetime.now()
    total = len(records)
    pass_rate = round((passed / total) * 100, 2) if total else 0.0
    duration_ms = int((finished_at - started_at).total_seconds() * 1000)

    summary = {
        "source": suite.get("source"),
        "base_url": suite.get("config", {}).get("base_url"),
        "started_at": started_at.strftime("%Y-%m-%d %H:%M:%S"),
        "finished_at": finished_at.strftime("%Y-%m-%d %H:%M:%S"),
        "duration_ms": duration_ms,
        "total": total,
        "passed": passed,
        "failed": failed,
        "pass_rate": pass_rate,
        "records": records,
    }
    _print_summary(summary)
    return summary


def _print_case_line(record):
    """在终端打印单条用例的简要结果。"""
    print(
        "[%s] %s %s %s | HTTP %s | %s ms | %s"
        % (
            record["status_text"],
            record["id"],
            record["method"],
            record["name"],
            record["status_code"],
            record["elapsed_ms"],
            "；".join(record["failures"]) if record["failures"] else "断言通过",
        )
    )


def _print_summary(summary):
    """在终端打印成功/失败统计。"""
    print("-" * 60)
    print(
        "合计 %s 条：成功 %s，失败 %s，通过率 %s%%，耗时 %s ms"
        % (
            summary["total"],
            summary["passed"],
            summary["failed"],
            summary["pass_rate"],
            summary["duration_ms"],
        )
    )
