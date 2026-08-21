# -*- coding: utf-8 -*-
"""
本地接口测试入口脚本。
读取 YAML 用例 -> 批量请求 -> 断言 -> 统计 -> 生成 HTML 看板。
不是 Web 服务，执行完即退出。
"""

import argparse
import os
import sys

from src.case_loader import load_test_suite
from src.reporter import render_html_report
from src.runner import run_suite


def build_parser():
    """组装命令行参数。"""
    parser = argparse.ArgumentParser(description="轻量 YAML 数据驱动接口测试工具")
    parser.add_argument(
        "--cases",
        default=os.path.join("cases", "httpbin_cases.yaml"),
        help="YAML 用例文件路径，默认 cases/httpbin_cases.yaml",
    )
    parser.add_argument(
        "--reports",
        default="reports",
        help="HTML 报告输出目录，默认 reports/",
    )
    return parser


def main(argv=None):
    """程序主流程。失败用例数大于 0 时以退出码 1 结束，方便接入 CI。"""
    args = build_parser().parse_args(argv)
    project_root = os.path.dirname(os.path.abspath(__file__))
    cases_path = args.cases
    if not os.path.isabs(cases_path):
        cases_path = os.path.join(project_root, cases_path)

    reports_dir = args.reports
    if not os.path.isabs(reports_dir):
        reports_dir = os.path.join(project_root, reports_dir)

    template_dir = os.path.join(project_root, "templates")

    print("加载用例：%s" % cases_path)
    suite = load_test_suite(cases_path)
    summary = run_suite(suite)
    report_path = render_html_report(summary, reports_dir, template_dir)
    print("HTML 质量看板已生成：%s" % report_path)

    return 1 if summary["failed"] else 0


if __name__ == "__main__":
    sys.exit(main())
