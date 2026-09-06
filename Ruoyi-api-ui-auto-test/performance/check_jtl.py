#!/usr/bin/env python3
"""检查 JMeter JTL 结果并执行性能质量门禁。

该脚本只读取 JMeter 实际产生的结果，不生成或伪造任何性能数据。
JMeter 默认通常输出 CSV JTL；同时兼容常见的 XML JTL，方便本地和 Jenkins 使用。
"""

from __future__ import annotations

import argparse
import csv
import math
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class Sample:
    """JMeter 一个请求样本的最小统计字段。"""

    timestamp_ms: float
    elapsed_ms: float
    success: bool


def percentile(values: list[float], percentile_value: float) -> float:
    """使用线性插值计算百分位数，避免只取某一个离散样本。"""
    if not values:
        return 0.0
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    rank = (len(ordered) - 1) * percentile_value / 100.0
    lower = math.floor(rank)
    upper = math.ceil(rank)
    if lower == upper:
        return ordered[lower]
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (rank - lower)


def as_bool(value: str) -> bool:
    """将 JMeter CSV 中的 success 字段转换为布尔值。"""
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def as_float(row: dict[str, str], *names: str, default: float = 0.0) -> float:
    """从多个可能的 JTL 列名中读取数字。"""
    for name in names:
        value = row.get(name)
        if value not in (None, ""):
            try:
                return float(value)
            except ValueError:
                pass
    return default


def read_csv_samples(path: Path) -> list[Sample]:
    """读取 CSV 格式 JTL。"""
    samples: list[Sample] = []
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        if not reader.fieldnames:
            raise ValueError("JTL CSV 缺少表头")
        for line_number, row in enumerate(reader, start=2):
            if not row:
                continue
            elapsed = as_float(row, "elapsed", "Elapsed")
            timestamp = as_float(row, "timeStamp", "timestamp", "Timestamp", default=0.0)
            success_text = row.get("success", row.get("Success", "true"))
            if elapsed < 0:
                raise ValueError(f"第 {line_number} 行 elapsed 不能为负数")
            samples.append(Sample(timestamp, elapsed, as_bool(success_text)))
    return samples


def read_xml_samples(path: Path) -> list[Sample]:
    """读取 XML 格式 JTL。"""
    samples: list[Sample] = []
    root = ET.parse(path).getroot()
    for sample in root.iter("sample"):
        attributes = sample.attrib
        elapsed = as_float(attributes, "t", "elapsed")
        timestamp = as_float(attributes, "ts", "timeStamp", default=0.0)
        success = attributes.get("s", attributes.get("success", "true"))
        samples.append(Sample(timestamp, elapsed, as_bool(success)))
    return samples


def read_samples(path: Path) -> list[Sample]:
    """根据首个非空字符判断 CSV/XML，并返回样本列表。"""
    with path.open("r", encoding="utf-8-sig") as file:
        first_non_empty = next((line.lstrip() for line in file if line.strip()), "")
    if first_non_empty.startswith("<"):
        return read_xml_samples(path)
    return read_csv_samples(path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Check JMeter JTL metrics and quality gates")
    parser.add_argument("--jtl", required=True, type=Path, help="JMeter CSV/XML JTL path")
    parser.add_argument("--max-error-rate", type=float, default=0.0, help="Maximum error rate in percent")
    parser.add_argument("--max-p95-ms", type=float, default=2000.0, help="Maximum P95 latency in milliseconds")
    parser.add_argument("--min-samples", type=int, default=1, help="Minimum expected sample count")
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.max_error_rate < 0 or args.max_p95_ms < 0 or args.min_samples < 0:
        print("质量门禁参数不能为负数", file=sys.stderr)
        return 2
    if not args.jtl.is_file():
        print(f"JTL 文件不存在: {args.jtl}", file=sys.stderr)
        return 2

    try:
        samples = read_samples(args.jtl)
    except (OSError, ValueError, ET.ParseError) as exc:
        print(f"读取 JTL 失败: {exc}", file=sys.stderr)
        return 2

    total = len(samples)
    failed = sum(not sample.success for sample in samples)
    successful = total - failed
    elapsed_values = [sample.elapsed_ms for sample in samples]
    error_rate = failed / total * 100 if total else 100.0
    average = sum(elapsed_values) / total if total else 0.0
    p90 = percentile(elapsed_values, 90)
    p95 = percentile(elapsed_values, 95)
    p99 = percentile(elapsed_values, 99)

    timestamps = [sample.timestamp_ms for sample in samples if sample.timestamp_ms > 0]
    if len(timestamps) >= 2 and max(timestamps) > min(timestamps):
        duration_seconds = (max(timestamps) - min(timestamps)) / 1000.0
    else:
        # 没有时间戳时只能用响应时间总和估算，明确标注为近似值。
        duration_seconds = sum(elapsed_values) / 1000.0
    throughput = total / duration_seconds if duration_seconds > 0 else 0.0

    print("JMeter performance summary")
    print(f"  samples       : {total}")
    print(f"  successful    : {successful}")
    print(f"  failed        : {failed}")
    print(f"  error_rate    : {error_rate:.2f}%")
    print(f"  average_ms    : {average:.2f}")
    print(f"  p90_ms        : {p90:.2f}")
    print(f"  p95_ms        : {p95:.2f}")
    print(f"  p99_ms        : {p99:.2f}")
    print(f"  throughput    : {throughput:.2f} samples/s (approx.)")

    violations: list[str] = []
    if total < args.min_samples:
        violations.append(f"samples {total} < min_samples {args.min_samples}")
    if error_rate > args.max_error_rate:
        violations.append(f"error_rate {error_rate:.2f}% > max {args.max_error_rate:.2f}%")
    if p95 > args.max_p95_ms:
        violations.append(f"p95 {p95:.2f}ms > max {args.max_p95_ms:.2f}ms")

    if violations:
        print("QUALITY GATE: FAILED")
        for violation in violations:
            print(f"  - {violation}")
        return 1

    print("QUALITY GATE: PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())