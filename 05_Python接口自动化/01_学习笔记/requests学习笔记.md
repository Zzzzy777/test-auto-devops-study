# Requests 核心知识

> 适用于 Python 接口测试入门笔记，主要整理 `requests` 的安装、GET/POST 请求模板、响应数据提取、超时设置和异常捕获。

## 目录

- [1. requests 安装](#1-requests-安装)
- [2. GET、POST 请求传参代码示例](#2-getpost-请求传参代码示例)
  - [2.1 通用基础结构](#21-通用基础结构)
  - [2.2 通用请求模板代码](#22-通用请求模板代码)
  - [2.3 模板替换说明](#23-模板替换说明)
  - [2.4 具体代码示例](#24-具体代码示例)
- [3. 响应数据提取](#3-响应数据提取)
- [4. timeout 超时与异常捕获](#4-timeout-超时与异常捕获)
- [5.  接口自动化断言（新增）](#5-接口自动化断言)
  - [5.1 assert 断言基础语法](#51-assert-断言基础语法)
  - [5.2 两种核心对象：resp /res 区分](#52-两种核心对象resp-res-区分)
  - [5.3 分层异常捕获（断言异常独立区分）](#53-分层异常捕获（断言异常独立区分)
  - [5.4 5.4 常用断言场景汇总](#54-常用断言场景汇总)
  - [5.5 5.5 高频报错 & 踩坑总结](#55-高频报错--踩坑总结)
## 1. requests 安装

### 安装命令

```bash
pip install requests
```

如果电脑上有多个 Python 版本，可以使用：

    ```bash
    pip3 install requests
    ```

## 2. GET、POST 请求传参代码示例

### 2.1 通用基础结构

所有接口请求脚本建议固定为以下 5 层结构，便于阅读、维护和复用：

1. 导入库：`import requests`，建议放在文件第一行。
2. 定义函数：使用规范函数名，方便后续复用。
3. 编写请求地址：定义接口地址 `url`。
4. 使用 `try-except` 包裹请求，避免网络异常导致脚本直接崩溃。
5. 在底部使用 `if __name__ == "__main__":` 调用函数运行。

第 4 步中建议包含：

- 发送请求时设置 `timeout=5`，避免脚本长时间卡住。
- 使用 `status_code == 200` 判断请求是否成功。
- 打印常用响应信息，例如状态码、返回内容、响应头等。

### 2.2 通用请求模板代码

```python
import requests


def 自定义函数名():
    url = "https://httpbin.ceshiren.com/get"

    try:
        resp = requests.请求方式(url, timeout=5)

        if resp.status_code == 200:
            print("请求成功")
            print("状态码：", resp.status_code)
            print("返回数据：", resp.数据格式)
        else:
            print("请求失败，错误码：", resp.status_code)

    except Exception as e:
        print("请求出错：", e)


if __name__ == "__main__":
    自定义函数名()
```

### 2.3 模板替换说明

| 模板内容 | 替换说明 | 示例 |
| --- | --- | --- |
| `自定义函数名` | 根据脚本功能命名 | `get_no_params`、`post_json` |
| `requests.请求方式` | 根据请求方法替换 | GET 使用 `requests.get`，POST 使用 `requests.post` |
| `resp.数据格式` | 根据接口返回类型选择 | 普通文本使用 `resp.text`，JSON 数据使用 `resp.json()` |
| `url` | 替换为实际接口地址 | `https://httpbin.ceshiren.com/get` |

> 示例接口地址使用 `https://httpbin.ceshiren.com`，国内访问相对稳定，可减少访问超时问题。

### 2.4 具体代码示例

| 场景 | 文件名 |
| --- | --- |
| GET 无参请求 | `01_get_no_params.py` |
| GET 带 `params` 参数 | `02_get_with_params.py` |
| POST 表单 `data` 提交 | `03_post_form_data.py` |
| POST `json` 结构体提交 | `04_post_json_body.py` |

## 3. 响应数据提取

### 示例代码

```python
import requests


resp = requests.get("https://httpbin.ceshiren.com/get")

# 1. 状态码
print(resp.status_code)

# 2. 响应头
print(resp.headers)

# 3. 请求携带的 cookie
print(resp.cookies)

# 4. 响应原始文本字符串
print(resp.text)

# 5. 自动转字典，接口返回 JSON 时使用
print(resp.json())

# 6. 二进制响应内容，下载文件、图片时使用
print(resp.content)

# 7. 实际请求的完整 URL
print(resp.url)

# 8. 编码格式
print(resp.encoding)
```

### 常用属性总结

| 属性 / 方法 | 说明 | 常见使用场景 |
| --- | --- | --- |
| `status_code` | 接口响应状态码，例如 `200` 成功、`4xx` 客户端错误、`5xx` 服务端错误 | 判断接口请求是否成功 |
| `text` | 字符串格式的响应内容 | 普通文本、HTML 页面 |
| `json()` | 将 JSON 字符串转换为 Python 字典 | 接口测试最常用 |
| `content` | 二进制字节流 | 图片、文件下载 |
| `headers` | 服务器返回的全部响应头信息 | 获取响应头字段 |
| `cookies` | 接口返回的 cookie 会话信息 | 登录态、会话校验 |
| `url` | 完整请求地址 | 校验 `params` 参数是否拼接正确 |
| `encoding` | 响应内容编码格式 | 处理中文乱码等编码问题 |

## 4. timeout 超时与异常捕获

### timeout 说明

`timeout=数字` 表示超时时间，单位是秒。

如果服务器在规定时间内没有响应，`requests` 会直接抛出超时异常。设置超时时间可以防止脚本一直卡住。

### 完整异常捕获模板

```python
import requests
from requests.exceptions import ReadTimeout, ConnectionError, RequestException


def test_timeout():
    url = "https://httpbin.ceshiren.com/get"

    try:
        # 设置 1 秒超时，模拟网络缓慢时报错
        resp = requests.get(url, timeout=1)
        print(resp.status_code)

    except ReadTimeout:
        print("异常：读取超时，服务器响应太慢")

    except ConnectionError:
        print("异常：网络连接失败，无法访问网址")

    except RequestException as e:
        print("通用请求异常：", e)


if __name__ == "__main__":
    test_timeout()
```

### 常见异常分类

| 异常类型 | 说明 |
| --- | --- |
| `ReadTimeout` | 读取超时，服务端长时间不返回数据 |
| `ConnectionError` | 连接失败，例如网址打不开、断网 |
| `RequestException` | `requests` 所有异常的父类，通常用于兜底捕获 |

## 5. 接口自动化断言
### 5.1 assert 断言基础语法

#### 语言格式
```python
assert 判断条件, "断言失败时打印的提示文字"
```

- 条件成立：代码正常往下执行，无任何输出；
- 条件不成立：抛出 AssertionError 异常，打印自定义提示；
- 作用：自动化校验接口返回是否符合预期，是接口测试核心校验手段。

#### 简单示例
```python
# 校验状态码必须是200
assert resp.status_code == 200, f"请求失败，实际状态码：{resp.status_code}"
```

### 5.2 两种核心对象：resp /res 区分
1. resp = requests.get/post(...)
- 完整响应 Response 对象，包含请求全部底层信息：状态码、响应头、原始文本、cookie、请求 url 等；
- 可用属性：resp.status_code、resp.headers、resp.text、resp.cookies
2. res = resp.json()
- 仅接口返回的 JSON 业务数据，自动转为 Python 字典，只能读取业务字段；
- 取值方式：res["键名"]，不能读取状态码、响应头。

直观对比
```python
resp = requests.get(url)  # 完整响应包
res = resp.json()          # 解析后的业务json字典

# resp独有（底层信息校验）
assert resp.status_code == 200

# res独有（业务数据校验）
assert res["args"]["username"] == "admin"
```

### 5.3 分层异常捕获（断言异常独立区分）
断言失败属于 AssertionError，要单独捕获，和网络、键缺失等异常分开，方便定位问题：
```python
try:
    resp = requests.get(url, timeout=10)
    res = resp.json()
    # 一堆断言
    assert resp.status_code == 200
except AssertionError as e:
    # 业务校验不通过（参数错误、状态码不对、cookie不匹配）
    print("❌ 断言校验失败：", e)
except Exception as e:
    # 网络、接口无json、键不存在、超时等其他错误
    print("❌ 请求异常：", e)
```

### 5.4 常用断言场景汇总
| 校验需求 | 代码写法 | 使用对象 |
| --- | --- | --- |
| 校验接口响应成功 | assert resp.status_code == 200	| resp |
| 校验 GET 查询参数 | assert res["args"]["key"] == "预期值" | res |
| 校验 POST 表单参数 | assert res["form"]["key"] == "预期值" | res |
| 校验 Cookie 会话 | assert res["cookies"]["session_id"] == "xxx" | res（仅 GET 接口） |
| 校验自定义请求头 | assert res["headers"]["User-Agent"] == "xxx" | res |
| 打印真实值方便排错 | assert a == b, f"预期{b}，实际{a}" | 通用 |

### 5.5 高频报错 & 踩坑总结
1. 语法错误：assert ["args"]["username"]
- 漏写 res，[] 单独创建列表，列表只能用数字下标；正确：assert res["args"]["username"]
2. KeyError: 'cookies'
- 在 /post 接口读取 res["cookies"]，POST 接口无顶层 cookies 字段，删除该行或换 GET 接口。
3. 类型不匹配断言失败
- GET params 传数字 id=10086，接口返回字符串 "10086"；
- 错误：assert res["args"]["id"] == 10086
- 正确：assert res["args"]["id"] == "10086"
4. if name = "main"
- 赋值单等号，判断相等必须双等号 ==
5. f-string 逗号放引号内部
- 错误：assert xxx == "值"f"提示"
- 正确：assert xxx == "值", f"提示文案"
6. 全角中文符号、空格会直接代码报错，所有标点统一英文。