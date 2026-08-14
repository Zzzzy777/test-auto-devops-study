# Python今日核心知识点（接口测试/运维入门专用）
## 目录
1. 代码注释
2. Python两种运行模式
3. 变量与基础数据类型
4. 字符串操作
5. print() 输出打印
6. 字典 dict（接口核心重点）
7. 模块导入 import
8. 自定义函数 def
9. for 循环（字典遍历）
10. 拓展必学（测试运维刚需）
11. 常见报错识别

---

## 1. 代码注释
python
- 单行注释：# 注释内容
- 多行注释："""多行文字""" / '''多行文字'''

## 2. Python 两种运行模式
1. 交互模式（临时调试）:
- ①CMD 输入 python 进入 >>> 交互环境
- ②单行代码即时运行，适合小段代码测试
- ③退出交互终端：exit()
2. 文件模式（写作业 / 正式脚本）
- ①文件后缀必须为 .py
- ②终端执行命令：python demo.py

## 3. 变量与基础数据类型
### 变量命名规则：
- 只能由字母、数字、下划线构成；
- 不能以数字开头，不推荐中文命名；
- 赋值格式：变量名 = 值

### 四大基础数据类型
# 字符串 str：文本、链接、文案，用双引号/单引号包裹
url = "https://httpbin.org/get"

# 整数 int：纯数字，状态码、ID、计数
status_code = 200

# 布尔 bool：只有 True / False，用于判断接口是否成功
is_success = True

# 空值 None：代表无数据、接口返回空
res_data = None

## 4.字符串操作
1. f-string 格式化（高频推荐）:
- code = 200
- print(f"接口状态码：{code}")
2. 字符串拼接
- prefix = "请求地址："
- api_url = "https://httpbin.org"
- full_text = prefix + api_url
- print(full_text)

## 5. print () 输出打印函数
# 基础打印
print(200)

# 多参数混合打印
print("接口状态码", 200, "请求正常")

## 6. 字典 dict（接口核心，重中之重）
1. 字典定义:
- headers = {
-     "User-Agent": "Chrome Browser",
-     "token": "abc123456"
- }
2. 根据键获取值:print(headers["User-Agent"])
3. 新增 / 修改字典键值:headers["username"] = "test_student"
4. 遍历字典全部键值对:
- for k, v in headers.items():
-   print(f"键：{k}，值：{v}")

## 7. 模块导入 import
所有第三方库脚本首行固定语法:
- # 导入requests库（接口专用）
- import requests

## 8. 自定义函数 def
1. 定义函数:
- def send_get_request(url):
-     headers = {"User-Agent": "test"}
-     return headers
2. 调用函数:
- result = send_get_request("https://httpbin.org")
- print(result)
3. 上述步骤合并之后运行结果：{'User-Agent': 'test'}

## 9. for 循环（仅字典遍历）
- user_info = {"name": "student", "age": 18}
- for key, value in user_info.items():
-     print(key, value)

## 10. 拓展必学（测试 / 运维刚需）
1. 列表 list
- 批量存放 URL、测试用例：
- url_list = ["api1", "api2", "api3"]

- # 下标取值，从0开始
- print(url_list[0])

- # 追加元素
- url_list.append("api4")

2. if 判断语句（判断接口返回状态）:
- code = 200
- if code == 200:
-     print("接口请求成功")
- else:
-     print("接口请求失败")

3. try-except 异常捕获
防止脚本报错直接终止:
- try:
-     num = 10 / 0
- except Exception as e:
-     print(f"程序异常：{e}")

- try:
-    # 可能报错、出问题的代码放这里
-    危险代码
- except 异常类型:
-    # 出错后执行这里，不会程序崩溃
-   处理错误

## 11. 常见基础报错识别
1. SyntaxError：语法错误，引号、冒号、括号书写错误
2. KeyError：字典中不存在该 key，取值失败
3. NameError：变量未定义 / 库未 import 导入
4. IndentationError：缩进错乱，Python 强制缩进规范