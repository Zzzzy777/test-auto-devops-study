# Pytest基础知识
## 学习目标
1. 了解 pytest 是什么，作用是什么
2. 掌握 pytest 文件、函数命名规则
3. 熟练使用常用执行命令
4. 看懂执行结果 PASS / FAIL
5. 生成 HTML 测试报告
6. 区分原生 requests、assert、pytest 三者关系

## 1、什么是 pytest
pytest 是 Python 的第三方测试框架。
- 作用：管理大量测试用例、批量运行用例、统计结果、生成测试报告
- 不需要复杂模板，遵循命名规则就可以自动识别用例
- 接口自动化、Web自动化都会使用这个框架

> 关系梳理
> requests：负责发http接口请求
> assert：python原生断言，用来判断结果是否符合预期
> pytest：测试框架，批量执行脚本，统计用例结果

## 2、pytest 自动识别用例规则（非常重要）
1. **py文件名称**：必须以 `test_` 开头，例如 `test_01_get.py`
2. **函数名称**：函数名必须以 `test_` 开头，例如 `def test_get_demo():`

> 如果不遵守这个命名，pytest不会识别为测试用例，不会执行。

示例简单用例模板
```python
import requests

def test_api_demo():
    url = "https://httpbin.ceshiren.com/get"
    try:
        resp = requests.get(url, timeout=10)
        print("响应状态码：", resp.status_code)
        print("响应数据：", resp.json())
        # 断言：判断响应状态码等于200
        assert resp.status_code == 200
        print("=== 用例执行成功 ===")
    except AssertionError as e:
        print("断言失败：", e)
        raise
    except Exception as e:
        print("请求发生异常：", e)
        raise

if __name__ == '__main__':
    test_api_demo()
```

## 3、pytest 常用命令
 >需要在脚本所在文件夹打开 cmd 执行
 1. 基础执行，简要输出:pytest
 2. -v 详细模式，打印每个用例名字、执行结果 PASS / FAILED:pytest -v
 3. -vs 最常用，详细模式 + 打印脚本内部 print 输出内容，调试用例必用:pytest -vs
 4. --lf（--last‑failed）只运行上一次失败的用例，成功用例直接跳过，调试 bug 节省时间:pytest -v --lf
 5. 生成 HTML 可视化测试报告:pytest -vs --html=report.html(执行完成，双击 report.html 用浏览器打开，查看统计、日志。)
 6. 只执行某一个脚本:pytest test_01_get_no_params.py -vs
 7. 直接运行 py 文件（不经过 pytest 框架）:python test_01_get_no_params.py

 ## 4、执行结果标识
 1. PASSED：用例通过，断言全部满足
 2. FAILED：用例失败，断言不成立、网络异常、代码报错

