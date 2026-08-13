# request核心知识
# 1.requests安装
1. 安装命令：pip install requests
2. 如果有多 Python 版本，使用 pip3：pip3 install requests

# 1.GET、POST 请求传参代码示例
## 万能基础壳（所有脚本共用骨架）：
所有接口请求脚本，固定 5 层结构，顺序不能乱：
1. 导入库：import requests（必须第一行）
2. 定义函数（规范写法，方便复用）
3. 写请求地址 url
4. try-except 包裹请求（防止网络卡死、报错崩溃）
- ·发送请求（get/post），加 timeout=5 超时限制
- · if 判断 status_code == 200 区分成功 / 失败
- ·打印全套响应信息（状态码、返回内容、请求头）
5. 底部 if __name__ == "__main__": 调用函数运行

### 1.模板代码如下：
- #1.导入库
- import requests
- #2.定义函数
- def 自定义函数名():
-     # 3.接口地址
-    url = "https://httpbin.ceshiren.com/get"
-    try:
-        # 4.发送请求，超时5秒
-        resp = requests.请求方式(url, timeout=5)
-        # 判断成功
-        if resp.status_code == 200:
-            print("请求成功")
-            print("状态码：", resp.status_code)
-            print("返回数据：", resp.数据格式)
-        else:
-            print("请求失败，错误码：", resp.status_code)
-    except Exception as e:
-        # 捕获所有网络异常
-        print("请求出错：", e)

- #执行函数
- if __name__ == "__main__":
-     自定义函数名()

### 2.模板替换说明
1. 自定义函数名：根据脚本修改，如 get_no_params、post_json
2. requests.请求方式：GET 填get，POST 填post
3. resp.数据格式
- ·普通文本、网页：resp.text
- ·JSON 接口返回数据：resp.json()
4. 接口地址替换为国内可用地址 https://httpbin.ceshiren.com，避免访问超时

### 3.具体代码示例
1. GET 无参请求（文件：01_get_no_params.py）
2. GET 带 params 参数（文件：02_get_with_params.py）
3. POST 表单 data 提交（文件：03_post_form_data.py）
4. POST json 结构体提交（文件：04_post_json_body.py）

### 4.响应数据提取各个属性说明
import requests

resp = requests.get("https://httpbin.ceshiren.com/get")

#### 1. 状态码
print(resp.status_code)
#### 2. 响应头
print(resp.headers)
#### 3. 请求携带的cookie
print(resp.cookies)
#### 4. 响应原始文本字符串
print(resp.text)
#### 5. 自动转字典（接口返回json时使用）
print(resp.json())
#### 6. 二进制响应内容（下载文件、图片）
print(resp.content)
#### 7. 实际请求的完整url
print(resp.url)
#### 8. 编码格式
print(resp.encoding)

>属性总结：
1. status_code：接口响应状态码，200 成功，4xx 客户端错误，5xx 服务端错误
2. text：字符串格式返回数据，普通文本 / HTML 页面使用
3. json()：方法，将 json 字符串转为 Python 字典，接口测试最常用
4. content：二进制字节流，图片、文件下载场景使用
5. headers：服务器返回的全部响应头信息
6. cookies：接口返回的 cookie 会话信息
7. url：完整请求地址，可校验 params 拼接是否正确

### 5.timeout 超时 + 异常捕获代码
1. 超时说明:timeout=数字 单位秒，规定时间内服务器无响应直接抛出超时异常，防止脚本卡死。
2. 完整异常捕获模板:

- import requests

- from requests.exceptions import ReadTimeout, ConnectionError, RequestException

- def test_timeout():
-     url = "https://httpbin.ceshiren.com/get"
-     try:
-         # 设置1秒超时，模拟网络缓慢报错
-         resp = requests.get(url, timeout=1)
-         print(resp.status_code)
-     except ReadTimeout:
-         print("异常：读取超时，服务器响应太慢")
-     except ConnectionError:
-         print("异常：网络连接失败，无法访问网址")
-     except RequestException as e:
-         print("通用请求异常：", e)

- if __name__ == "__main__":
-     test_timeout()


3. 异常分类：
- ①ReadTimeout：读取超时，服务端长时间不返回数据
- ②ConnectionError：连接失败，网址打不开、断网
- ③RequestException：requests 所有异常的父类，兜底捕获