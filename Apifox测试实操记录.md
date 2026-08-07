# Apifox 接口测试实操记录
## 实验目的
练习HTTP接口调试、环境变量Token传递、完整业务场景自动化执行，模拟后端登录‑鉴权‑业务操作真实流程。

## 使用工具
Apifox，公共测试接口 httpbin.org

## 一、单接口调试清单
1. POST 登录接口
- 作用：模拟登录，后置脚本提取token，存入【测试环境】环境变量 `access_token`
- 请求地址：http://httpbin.org/post
- 请求方式：POST
- 后置脚本（提取token存入环境变量）

- js代码
- //模拟拿到返回的token，写入环境变量
- pm.environment.set("access_token","mock‑token‑123456");

### 方式 A：图形化后置操作
1. ①切换标签【后置操作】②添加后置操作③提取变量 
- ·提取源：Response JSON
- ·提取选项：JSONPath
- ·JSONPath 表达式：$.json.token
- ·变量类型：环境变量
- ·变量名：access_token

2. 添加后置操作 → 断言
- ·断言 1：HTTP Code 等于 200，校验接口请求成功

- 实操记录：发送请求后，右上角【测试环境】可以查看到环境变量access_token自动生成，值为 mock‑token‑123456。

### 方式 B：JS 脚本后置脚本
- // 真实业务登录接口后置脚本示例
- // 从接口返回的json响应体取出token值
- let token = pm.response.json().data.token;
- // 将token存入当前选中的环境变量，变量名叫access_token
- pm.environment.set("access_token", token);

- 断言：响应状态码等于 200

2. GET 用户列表 (需要 token 鉴权)
- 作用：携带 token 访问受保护接口
- 请求头新增：Authorization: Bearer {{access_token}}
- 请求方式：GET
- 断言：状态码 200

3. POST 新增用户 (需要 token 鉴权)
- 作用：执行业务新增操作，必须携带合法 token
- 请求头新增：Authorization: Bearer {{access_token}}
- 请求地址：http://httpbin.org/post
- 请求方式：POST
- 请求 Body JSON 示例：{"username":"admin"}
- 断言：状态码 200

## 场景用例：登录‑用户列表‑新增用户 全流程
1. 优先级：P2
2. 执行顺序：
- ①POST 登录接口（生成环境变量 access_token）；
- ②GET 用户列表（自动读取环境变量 token 鉴权）；
- ③POST 新增用户（复用同一个 token）；
3. 场景用例价值：模拟用户真实完整业务操作流程，验证接口之间的数据依赖关系，多用于业务链路测试；也可用于版本迭代后的回归验证。
4. 常见失败点：
- 选错运行环境，读取不到环境变量
- 请求头 Authorization 格式写错（Bearer 后面有空格）
- 接口执行顺序颠倒，未登录就调用鉴权接口 


## 二、Token鉴权接口实操记录
接口地址：GET https://httpbin.ceshiren.com/headers

### 1. token 异常场景测试实操
| 用例场景 | 请求头Authorization值 | 实际返回状态码 | 真实项目预期状态码 |
| ---- | ---- | ---- | ---- |
| 正常携带有效token | mock‑token‑888666 | 200 | 200 |
| 传入错误无效token | abc‑wrong‑token‑123 | 200 | 401 |
| 传入已过期token | mock‑token‑expire‑999 | 200 | 401 |
| Token传空字符串 | （留空） | 200 | 401 |
| 不携带Authorization请求头 | 删除该header | 200 | 401 |

>备注：当前测试网站不做鉴权校验，全部返回200；真实业务系统异常场景会返回401未授权。
知识点：401代表身份认证失败，一般是token缺失、错误、过期。

### 2.登录接口入参异常测试实操
>模拟登录接口，请求体为JSON格式
- 正常请求体：
- json
- {
-     "username":"admin",
-    "password":"123456"
- }

| 用例场景 | 请求 JSON 参数 | 实际返回状态码 | 真实项目预期 |
| ---- | ---- | ---- | ---- |
| 账号正常，密码为空 | {"username":"admin","password":""} | 200 | 业务提示：密码不能为空 |
| 账号为空，密码正常 | {"username":"","password":"123456"} | 200 | 业务提示：账号不能为空 |
| 账号、密码全部为空 | {"username":"","password":""} | 200 | 业务提示：账号、密码不能为空 |
| 账号正确，密码错误 | {"username":"admin","password":"654321"} | 200 | 业务提示：账号或密码错误 |
| 账号不存在，密码随意填写 | {"username":"test999","password":"123456"} | 200 | 业务提示：账号或密码错误 |


>知识点：
1. 登录类业务接口，参数校验错误大多HTTP状态码依旧是200，依靠返回体内部业务code、message做业务判断；
2. 401一般用于**鉴权阶段**（token问题），不是登录账号密码参数错误；
3. POST接口请求体务必选择raw‑JSON格式，格式错误接口会解析失败。

> 面试：我使用场景用例完成正向业务流程自动化，通过环境变量完成接口之间 token 参数传递；同时设计异常场景，验证接口在无 token、非法 token 情况下鉴权拦截逻辑是否符合预期。