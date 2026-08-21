# -*- coding: utf-8 -*-
"""
使用 Jinja2 渲染静态 HTML 质量看板。
生成的是本地 HTML 文件，不启动任何 Web 服务。
"""

import os
from datetime import datetime

from jinja2 import Environment, FileSystemLoader, select_autoescape


def render_html_report(summary, output_dir, template_dir):
    """
    把执行汇总渲染成 HTML 文件。

    :param summary: runner.run_suite 的返回值
    :param output_dir: 报告输出目录
    :param template_dir: Jinja2 模板所在目录
    :return: 生成的 HTML 绝对路径
    """
    os.makedirs(output_dir, exist_ok=True)

    env = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=select_autoescape(["html", "xml"]),
    )
    template = env.get_template("dashboard.html.j2")
    html = template.render(summary=summary)

    filename = "quality_dashboard_%s.html" % datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(output_dir, filename)
    with open(output_path, "w", encoding="utf-8") as handle:
        handle.write(html)
    return os.path.abspath(output_path)
