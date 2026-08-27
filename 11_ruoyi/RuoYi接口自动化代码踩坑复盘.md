# RuoYi接口自动化代码踩坑复盘
> 记录编写pytest接口用例过程中代码层面报错、排查过程、解决方案

## 踩坑1：分页接口断言，部门树形接口执行失败
### 现象
1. 执行 `/system/dept/list` 查询部门树形列表用例，HTTP状态码200，业务返回码`code=200`，但是用例AssertionError断言失败。
2. 报错信息：AssertionError: assert 'rows' in {'msg': ' 操作成功 ', 'code': 200, 'data': [...]}

### 排查过程
1. 接口请求成功，状态码和业务码全部正常，不是token、网络、服务问题。
2. 打印完整响应json，发现接口返回的数组字段是 **`data`**，不是`rows`。
3. 问题根源：直接复制用户分页接口`/system/user/list`的断言代码。
    - `/system/user/list` 用户分页接口：返回 `rows`、`total`
    - `/system/dept/list` 部门树形接口：返回 `data`，无分页

#### 错误代码
```python
# 错误：照搬分页接口，断言rows字段
assert "rows" in res
```

#### 修复代码
```python
# 断言存在data字段
assert "data" in js
# 额外校验data是列表类型
assert isinstance(js["data"], list)
```


## 踩坑2：混淆 requests 库对象与响应状态码
### 现象
1. 登录反向用例执行失败，AssertionError，拿模块对象和数字 200 做对比。
2. 报错：AssertionError: assert <module 'requests.status_codes' ...> == 200

### 问题原因
- 错误书写：`assert requests.status_codes == 200`
- `requests.status_codes` 属于 requests 库内部模块，**不是接口返回的状态码**。
- 接口请求之后，`resp = requests.post(...)`，http 返回状态码保存在响应对象：`resp.status_code`。

#### 错误代码
```python
resp = requests.post(url,json=data,timeout=10)
assert requests.status_codes == 200
```

### 修复代码
```python
resp = requests.post(url,json=data,timeout=10)
assert resp.status_code == 200
```


## 踩坑3：复制分页用例，菜单树形接口错误断言rows字段
### 现象
1. 执行 `/system/menu/list` 查询部门树形列表用例，HTTP状态码200，业务返回码`code=200`，但是用例AssertionError断言失败。
2. 报错信息：AssertionError: assert 'rows' in {'msg': ' 操作成功 ', 'code': 200, 'data': [...]}

### 排查过程
1. 接口请求成功，状态码和业务码全部正常，不是token、网络、服务问题。
2. 打印完整响应json，发现接口返回的数组字段是 **`data`**，不是`rows`。
3. 问题根源：直接复制用户分页接口`/system/user/list`的断言代码。
    - `/system/user/list` 用户分页接口：返回 `rows`、`total`
    - `/system/menu/list` 部门树形接口：返回 `data`，无分页

#### 错误代码
```python
# 错误：照搬分页接口，断言rows字段
assert "rows" in res
```

#### 修复代码
```python
# 断言存在data字段
assert "data" in res
# 额外校验data是列表类型
assert isinstance(js["data"], list)
```


## 踩坑4：RuoYi 新增用户接口 500 内部服务器错误
### 现象
- 调用新增用户接口，HTTP 状态码返回 500，用例直接失败；数据库 deptId 部门 ID 确认真实存在，一开始误以为是部门 ID 或者 token 鉴权问题。

### 排查过程
1. token 请求头携带正常，接口返回 500 不是 401/403，排除鉴权问题。
2. 核对数据库，传入的 deptId 部门 ID 真实存在，排除部门不存在。
3. 打印完整请求 body，发现只传了`userName`、`deptId`两个字段。
4. 对照接口文档，**nickName、password 属于接口必填参数**，缺少字段后端直接抛出异常，返回 500。

### 错误代码
```python
body = {
    "userName": "testauto01",
    "deptId": 105
}
resp = send_request("POST",url,json=body)
assert resp.status_code == 200
```

#### 修复代码
```python
body = {
    "userName": "testauto01",
    "nickName": "自动化测试账号",
    "password": "123456",
    "deptId": 105
}
resp = send_request("POST",url,json=body)
print(f"状态码：{resp.status_code}")
print(f"返回报文：{resp.text}")
assert resp.status_code == 200
res = resp.json()
assert res["code"] == 200
```

>总结:做接口自动化，不能只看示例返回，**要仔细阅读接口入参文档，分清必填、选填字段**；缺少必填字段，部分后端不会返回清晰提示，直接抛出 500 服务端异常。


## 踩坑5：分配菜单接口，不能靠记忆写 URL 和请求方式
### 现象
- 想写角色分配菜单接口用例，记忆中的接口地址、请求方法调用一直报错，提示请求方法不支持。

### 排查过程
1. RuoYi 不同版本，分配菜单接口的 URL、请求 Method 会发生变化，靠记忆写代码很容易出错。
2. 正确做法是启动`ruoyi‑ui`Vue 前端，浏览器 F12 抓包，从`Fetch/XHR`拿到真实的`Request URL`、请求方式、请求体 Payload。
3. 当前本地只有后端 SpringBoot 代码，没有部署前端 ruoyi‑ui，无法抓包获取真实请求。

### 处理方案
>暂时注释分配菜单的用例，保证**新增角色‑查询角色‑删除角色**核心业务链路正常跑通，把问题记录归档，后续部署前端后再补全该用例。

### 总结：前后端分离项目，写自动化脚本优先通过前端抓包拿到真实接口信息，不要依赖记忆；接口自动化只调用后端接口，本身不需要前端运行，只有抓包调试的时候才需要前端。


## 踩坑6：传入非法手机号，接口未做参数格式校验
### 现象
编写异常用例，新增用户传入非法手机号`"123"`，预期后端校验拦截、新增失败。
实际接口返回业务码`code=200`，直接创建用户成功，非法手机号存入数据库。

### 排查过程
1. 打印完整响应报文，确认http状态200，业务返回成功，脚本断言`res["code"] !=200`直接报错用例失败。
2. 核对RuoYi源码，该版本**没有对phonenumber字段增加正则格式校验**，仅做非空判断。
3. 短数字、字母混合字符串都可以当作手机号正常入库。

### 处理方案
1. 保留该自动化用例，**不强制断言业务码不等于200**，把该场景作为接口缺陷留存。
2. 将问题记录复盘文档，记录缺陷现象：接口缺少手机号格式校验，非法号码可成功创建用户。

### 总结
做接口异常测试，不能主观预判后端一定有校验。自动化用例就是用来暴露参数校验类缺陷；
当实际返回和预期不一致，不一定是脚本bug，有可能是被测接口本身存在漏洞。
