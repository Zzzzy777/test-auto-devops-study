#!/usr/bin/env python3
"""生成不依赖 JavaScript 的 JMeter 静态 HTML 报告。

Jenkins 的归档 HTML 页面可能受到 Content-Security-Policy 限制，导致 JMeter
官方 dashboard 的 JavaScript、图表和 JSON 请求被拦截。本脚本只生成普通
HTML 表格，不包含 script 标签或内联样式，因此可以在 Jenkins HTML Publisher
的 iframe 中直接显示真实 JTL 统计结果。
"""

from __future__ import annotations

import argparse
import csv
import html
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

from check_jtl import as_bool, as_float, percentile


def read_records(path: Path) -> list[dict[str, object]]:
    """读取 JMeter CSV/XML JTL，返回报告需要的字段。"""
    with path.open("r", encoding="utf-8-sig") as file:
        first = next((line.lstrip() for line in file if line.strip()), "")

    records: list[dict[str, object]] = []
    if first.startswith("<"):
        root = ET.parse(path).getroot()
        for node in root.iter("sample"):
            attrs = node.attrib
            records.append(
                {
                    "label": attrs.get("lb", attrs.get("label", "(unknown)")),
                    "timestamp": as_float(attrs, "ts", "timeStamp", default=0.0),
                    "elapsed": as_float(attrs, "t", "elapsed"),
                    "success": as_bool(attrs.get("s", attrs.get("success", "true"))),
                    "code": attrs.get("rc", attrs.get("responseCode", "")),
                    "message": attrs.get("rm", attrs.get("responseMessage", "")),
                }
            )
        return records

    with path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        if not reader.fieldnames:
            raise ValueError("JTL CSV 缺少表头")
        for row in reader:
            if not row:
                continue
            records.append(
                {
                    "label": row.get("label", "(unknown)"),
                    "timestamp": as_float(row, "timeStamp", "timestamp", "Timestamp", default=0.0),
                    "elapsed": as_float(row, "elapsed", "Elapsed"),
                    "success": as_bool(row.get("success", row.get("Success", "true"))),
                    "code": row.get("responseCode", row.get("ResponseCode", "")),
                    "message": row.get("responseMessage", row.get("ResponseMessage", "")),
                }
            )
    return records


def fmt_ms(value: float) -> str:
    return f"{value:.2f} ms"


def fmt_pct(value: float) -> str:
    return f"{value:.2f}%"


def cell(value: object) -> str:
    return f"<td>{html.escape(str(value))}</td>"


def make_report(records: list[dict[str, object]], args: argparse.Namespace) -> str:
    elapsed_all = [float(item["elapsed"]) for item in records]
    failed_all = sum(not bool(item["success"]) for item in records)
    total = len(records)
    successful = total - failed_all
    timestamps = [float(item["timestamp"]) for item in records if float(item["timestamp"]) > 0]
    if len(timestamps) >= 2 and max(timestamps) > min(timestamps):
        duration_seconds = (max(timestamps) - min(timestamps)) / 1000.0
    else:
        duration_seconds = sum(elapsed_all) / 1000.0 if elapsed_all else 0.0
    throughput = total / duration_seconds if duration_seconds > 0 else 0.0
    error_rate = failed_all / total * 100 if total else 100.0

    groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    for record in records:
        groups[str(record["label"])].append(record)

    summary_rows = [
        ("JTL 文件", args.jtl.name),
        ("样本数", total),
        ("成功数", successful),
        ("失败数", failed_all),
        ("错误率", fmt_pct(error_rate)),
        ("平均响应时间", fmt_ms(sum(elapsed_all) / total if total else 0.0)),
        ("P90", fmt_ms(percentile(elapsed_all, 90))),
        ("P95", fmt_ms(percentile(elapsed_all, 95))),
        ("P99", fmt_ms(percentile(elapsed_all, 99))),
        ("近似吞吐量", f"{throughput:.2f} samples/s"),
    ]
    if args.threads is not None:
        summary_rows.extend(
            [
                ("线程数", args.threads),
                ("Ramp-up", f"{args.ramp_up} 秒"),
                ("每线程循环数", args.loops),
            ]
        )

    summary_html = "\n".join(f"<tr>{cell(name)}{cell(value)}</tr>" for name, value in summary_rows)
    group_html: list[str] = []
    error_html: list[str] = []
    for label, items in groups.items():
        elapsed = [float(item["elapsed"]) for item in items]
        failed = sum(not bool(item["success"]) for item in items)
        group_html.append(
            "<tr>"
            + cell(label)
            + cell(len(items))
            + cell(len(items) - failed)
            + cell(failed)
            + cell(fmt_pct(failed / len(items) * 100 if items else 0.0))
            + cell(fmt_ms(sum(elapsed) / len(elapsed) if elapsed else 0.0))
            + cell(fmt_ms(percentile(elapsed, 95)))
            + cell(fmt_ms(min(elapsed) if elapsed else 0.0))
            + cell(fmt_ms(max(elapsed) if elapsed else 0.0))
            + "</tr>"
        )
        for item in items:
            if not bool(item["success"]):
                error_html.append(
                    "<tr>"
                    + cell(label)
                    + cell(item["code"])
                    + cell(item["message"] or "失败样本")
                    + cell(fmt_ms(float(item["elapsed"])))
                    + "</tr>"
                )

    if not group_html:
        group_html.append('<tr><td colspan="9">JTL 中没有样本记录</td></tr>')
    if not error_html:
        error_html.append('<tr><td colspan="4">没有失败请求</td></tr>')

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>JMeter Performance Report</title>
</head>
<body>
<h1>JMeter Performance Report</h1>
<p>这是基于 JMeter 实际 JTL 结果生成的静态报告。页面不依赖 JavaScript，适用于 Jenkins HTML Publisher。</p>
<h2>总体结果</h2>
<table border="1" cellpadding="6" cellspacing="0">
<thead><tr><th>指标</th><th>结果</th></tr></thead>
<tbody>{summary_html}</tbody>
</table>
<h2>按请求统计</h2>
<table border="1" cellpadding="6" cellspacing="0">
<thead><tr><th>请求名称</th><th>样本数</th><th>成功数</th><th>失败数</th><th>错误率</th><th>平均响应时间</th><th>P95</th><th>最小值</th><th>最大值</th></tr></thead>
<tbody>{''.join(group_html)}</tbody>
</table>
<h2>失败请求</h2>
<table border="1" cellpadding="6" cellspacing="0">
<thead><tr><th>请求名称</th><th>响应码</th><th>响应信息</th><th>响应时间</th></tr></thead>
<tbody>{''.join(error_html)}</tbody>
</table>
</body>
</html>
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a CSP-friendly static JMeter report")
    parser.add_argument("--jtl", required=True, type=Path, help="JMeter CSV/XML JTL path")
    parser.add_argument("--output-dir", required=True, type=Path, help="Output directory for index.html")
    parser.add_argument("--threads", type=int)
    parser.add_argument("--ramp-up", type=int, default=0)
    parser.add_argument("--loops", type=int)
    args = parser.parse_args()

    if not args.jtl.is_file():
        print(f"JTL 文件不存在: {args.jtl}", file=sys.stderr)
        return 2
    try:
        records = read_records(args.jtl)
        report = make_report(records, args)
        args.output_dir.mkdir(parents=True, exist_ok=True)
        (args.output_dir / "index.html").write_text(report, encoding="utf-8")
    except (OSError, ValueError, ET.ParseError) as exc:
        print(f"生成静态 JMeter 报告失败: {exc}", file=sys.stderr)
        return 2

    print(f"Static JMeter report: {args.output_dir / 'index.html'}")
    print(f"Reported samples: {len(records)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())