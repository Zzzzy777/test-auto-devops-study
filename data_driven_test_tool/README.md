# 轻量接口测试数据驱动工具

本地脚本：读取 YAML 用例，批量请求公开 httpbin 接口，断言响应，并用 Jinja2 生成 HTML 质量看板。不启动 Web 服务，不使用 pytest-yaml。

## 目录结构

```text
data_driven_test_tool/
├── main.py                      # 入口：加载用例、执行、出报告
├── requirements.txt             # Python 依赖
├── cases/
│   └── httpbin_cases.yaml       # httpbin 示例用例
├── src/
│   ├── yaml_parser.py           # 手写 YAML 解析
│   ├── case_loader.py           # 用例结构校验与标准化
│   ├── http_client.py           # requests 封装
│   ├── asserter.py              # 响应断言
│   ├── runner.py                # 批量执行与成功/失败统计
│   └── reporter.py              # Jinja2 渲染 HTML 看板
├── templates/
│   └── dashboard.html.j2        # 质量看板模板
└── reports/                     # 生成的 HTML 报告输出目录
```

## 安装与运行

在项目根目录执行：

```bash
pip install -r requirements.txt
python main.py
```

指定用例文件和报告目录：

```bash
python main.py --cases cases/httpbin_cases.yaml --reports reports
```

执行结束后，用浏览器打开 `reports/quality_dashboard_*.html` 即可查看看板。示例中最后一条用例会故意失败，用于验证失败计数。
