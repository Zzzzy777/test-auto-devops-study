# Python 接口自动化

> 本目录用于归档 Python 接口自动化学习资料。为了避免内容重复，当前按“学习笔记、阶段练习、完整项目”三类整理。

## 推荐阅读顺序

1. 先看 [01_学习笔记](./01_学习笔记/)：理解 Python、requests、pytest、fixture、Allure 的基础概念。
2. 再看 [02_阶段练习](./02_阶段练习/)：查看早期 GET/POST、断言、pytest 改造过程。
3. 最后看 [03_完整项目](./03_完整项目/)：重点看可写进简历的 `pytest_api_demo`。

## 目录结构

```text
05_Python接口自动化/
├── 01_学习笔记/
│   ├── python核心知识点.md
│   ├── requests学习笔记.md
│   ├── Pytest知识笔记.md
│   ├── Pytest‑Fixture 学习笔记.md
│   └── Pytest+Allure 接口自动化.md
├── 02_阶段练习/
│   └── python_requests_api_learning/
└── 03_完整项目/
    └── pytest_api_demo/
```

## 内容说明

| 分类 | 作用 | 是否重点 |
| --- | --- | --- |
| `01_notes` | 放基础知识笔记，适合复习概念和面试口述 | 需要看懂 |
| `02_阶段练习` | 放学习过程中的小脚本，记录从 requests 到 pytest 的过渡 | 用来回顾 |
| `03_完整项目` | 放完整可运行 demo，适合 GitHub 展示和简历项目 | 重点掌握 |

## 简历项目入口

重点看这个项目：

[pytest_api_demo 接口自动化项目](./03_完整项目/pytest_api_demo/README.md)

该项目覆盖：

- GET / POST 接口请求
- 请求参数、请求头、Cookie 校验
- Token fixture 复用
- 异常场景断言
- pytest-html 报告
- Allure 报告截图

报告说明：

[测试报告与截图说明](./03_完整项目/pytest_api_demo/docs/测试报告与截图说明.md)

## 学习建议

- 面试前优先讲 `03_完整项目/pytest_api_demo`，不要把所有零散练习都当成项目讲。
- `02_阶段练习` 是学习过程证据，适合自己复盘，不需要逐个放进简历。
- 如果面试官问基础，再回到 `01_学习笔记` 解释概念。

