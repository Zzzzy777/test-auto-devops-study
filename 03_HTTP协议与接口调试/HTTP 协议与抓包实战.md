# 一、完整HTTP请求与响应通信流程

# HTTP报错排查清单.md
## 常用状态码
### 2xx 成功
- 200 OK：请求成功
- 201 Created：创建资源成功

### 4xx 客户端错误
- 400 Bad Request：参数格式错误，JSON写错、参数缺失
- 401 Unauthorized：Token失效/没带token，未认证
- 403 Forbidden：权限不足，认证成功但是不让访问
- 404 Not Found：接口地址写错，服务没有这个路径
- 405 Method Not Allowed：请求方法错，接口是POST你发了GET

### 5xx 服务端错误
- 500 Internal Server Error：后端代码异常
- 502 Bad Gateway：网关/代理没拿到后端响应，后端服务挂了
- 503 Service Unavailable：服务不可用，服务停机、过载

## 1. 客户端到服务器完整6步通信逻辑
1. DNS域名解析：将域名翻译成服务器IP地址，确定访问目标机器
2. TCP三次握手：客户端与服务器建立稳定可靠的数据传输通道
3. 客户端组装并发送HTTP请求报文
4. 服务端分层处理请求：鉴权校验 → 参数校验 → 执行业务逻辑
5. 服务器组装HTTP响应报文返回客户端，携带状态码、业务数据或报错信息
6. TCP四次挥手：通信结束，断开网络连接释放资源

## 2. HTTP报文完整结构（抓包、接口测试核心查看内容）
### 2.1 请求报文（客户端发送给服务器）
整体分为三部分：请求行、请求头Headers、请求体Body
1. 请求行：固定格式 `请求方法 接口路径 HTTP版本`
   示例：`POST /auth HTTP/1.1`
2. 请求头Headers（测试重点，Token存放位置）
   - `Content-Type`：声明请求体参数格式，接口传JSON必须配置`application/json`
   - `Authorization: Bearer Token`：前后端分离项目登录鉴权核心字段
   - Host：当前请求访问的域名地址
   - User-Agent：标记发起请求的客户端（Edge浏览器/Apifox工具）
3. 请求体Body
   - GET请求：无请求体，参数拼接在URL后方Params中
   - POST/PUT/DELETE请求：JSON、表单、文件等业务参数存放位置

### 2.2. HTTP响应组成
1. 状态行：HTTP版本 + 状态码 + 描述 例：`HTTP/1.1 200 OK`
2. 响应头：服务器返回的配置、缓存、Cookie信息
3. 响应体：接口返回的业务数据（JSON格式为主）

> 补充：HTTP协议本身是无状态协议，服务器不会记录用户登录信息，因此必须依靠Token/Cookie完成登录身份识别，这也是Token鉴权方案存在的核心原因。

## 3. Token鉴权实操（接口关联实战）
### 3.1 鉴权核心流程
1. 调用登录POST接口，传入账号密码，服务端校验通过返回Token字符串；
2. 提取响应体中的token值，存入Apifox/Postman环境变量；
3. 后续所有需要登录权限的接口，在请求头添加：`Authorization: Bearer {{token变量名}}`；
4. 服务端解析Header内Token，校验登录身份，未携带/失效则返回401未授权。

### 3.2 关键请求头说明
- `Authorization: Bearer xxx`：标准Token鉴权格式，Bearer和token之间必须带空格；
- 无Token/Token过期响应码：`401 Unauthorized`；
- Token权限不足响应码：`403 Forbidden`。

### 3.3 实操踩坑记录
1. 漏写Bearer关键字，直接传token，服务端识别失败，返回401；
2. 环境变量作用域选错（全局/项目/环境），变量读取不到，鉴权失效；
3. Token有有效期，过期后必须重新调用登录接口刷新变量；
4. GET请求同样需要携带Token，不能误以为只有POST才需要鉴权。

## 4、Fiddler抓包工具实操知识点
### 4.1. 界面核心区域
1. Web Sessions（左侧列表）：捕获所有HTTP/HTTPS请求，展示状态码、请求方式、域名
2. 顶部工具栏核心按钮
    - Decode：HTTPS解密开关，开启后才能查看明文JSON数据
    - Composer：自定义构造请求，替代Apifox临时调试接口
    - Inspectors：查看请求详情、响应返回数据
    - Clear：清空所有抓包会话
3. 右侧会话详细（Inspectors）面板
    - Request：查看请求头、请求入参、Body
    - Response：查看状态码、后端返回JSON报错信息
4. 底部命令行：输入`select json`快速筛选所有返回JSON的接口

### 4.2. 必备基础配置
1. HTTPS证书配置（解决抓包乱码）
    - 顶部菜单 Tools → Options → HTTPS
    - 勾选 Decrypt HTTPS traffic，一路确认安装根证书
2. 代理端口配置
    - Connections标签默认端口8888，端口被占用时修改端口号，重启Fiddler生效
3. 弹窗屏蔽
    - AppContainer Configuration弹窗直接点击Cancel，永久关闭提示
4. 请求过滤（Filters）
    - 切换Filters标签，勾选Use Filters，筛选指定域名，过滤无关网页流量

### 4.3. 标准抓包操作流程
1. 启动Fiddler，点击Decode开启HTTPS解密
2. 使用浏览器/Apifox发起接口请求
3. 左侧Web Sessions选中目标接口会话
4. 右侧切换Inspectors查看完整请求与响应数据
5. Replay按钮：重放请求，稳定复现接口报错
6. Composer面板：修改参数、Token，自定义发送请求复现问题

### 4.4. Fiddler常见问题解决
1. 抓不到HTTPS接口：未安装根证书、Decode解密未开启
2. 关闭Fiddler后浏览器无法上网：系统代理未关闭，手动关闭代理
3. 无任何请求捕获：8888端口被其他程序占用，修改端口重启工具
4. Edge/微软商店应用抓不到流量：工具栏WinConfig开启AppContainer捕获

## 5. Fiddler抓包查看完整指南
### 5.1 请求基础概览（抓包列表顶部首行）
- 每行抓包第一条信息固定格式：请求方法 接口路径 HTTP版本 + 右侧响应状态码
1. 请求方法：GET/POST/PUT/DELETE/PATCH/OPTIONS
- 问题场景：接口限定 POST，使用 GET 请求 → 返回 405
2. 接口 URL 路径
- 问题场景：路径拼写错误、漏写层级 → 返回 404
3. HTTP 版本：HTTP/1.0、HTTP/1.1、HTTP/2
4. 响应状态码（故障第一判断依据）：
- ①2xx：请求正常成功；
- ②4xx：客户端侧错误（参数、Token、权限、地址）；
- ③5xx：服务端侧错误（服务崩溃、代码异常、网关故障）

### 5.2 上半区：Request Headers 客户端请求头（客户端发给服务器）
1. 身份认证类（接口测试高频）
- ·Authorization：承载 Token、Bearer 令牌、Basic 账号密码
 - 故障：无该头部、Token 过期、Token 篡改 → 401 未认证
- ·Cookie：会话凭证、登录缓存信息
 - 故障：Cookie 丢失导致登录失效、重复跳转登录页
2. 客户端标识类
- ·User-Agent：标识请求来源（浏览器、Apifox、Postman、APP）
 - 故障：服务端限制客户端，UA 异常直接拦截返回 403
- ·Accept：客户端支持接收的返回数据格式（application/json/text/html）
3. 传输与基础配置
- ·Host：目标服务器域名 / IP，域名错误无法建立连接
- ·Content-Type（POST 请求核心）：请求入参格式
 - application/json：JSON 传参
 - application/x-www-form-urlencoded：表单参数
 - multipart/form-data：文件上传
 - 故障：传参格式和接口要求不匹配 → 400 参数错误
- Content-Length：请求体数据长度
- Connection: keep-alive：长连接复用

### 5.3 下半区：Response Headers 服务端响应头（服务器返回客户端）
1. 返回数据描述
- ·Content-Type：服务器返回数据格式
 - 故障：预期 JSON，实际返回 HTML 报错页面，程序解析失败
- ·Content-Length：响应数据字节大小
2. 跨域配置（前端接口高频问题）
- ·Access-Control-Allow-Origin：允许访问的前端域名
 - 故障：前端页面报跨域报错，该字段未配置或限制域名
3. 缓存与时间
- ·Date：服务器处理请求时间
- ·Cache-Control/Expires：缓存策略
4. 服务与连接
- ·server：后端服务类型
- ·Connection: keep-alive：服务端保持长连接

### 5.4 下方标签栏（核心实操查看区域，所有场景通用）
1. 数据标签
- GET：无请求体，仅看 URL 参数
- POST/PUT：查看完整请求入参、表单、JSON 报文
- 故障定位：参数缺失、参数值错误、JSON 格式写错
2. JSON / XML
- 格式化展示后端返回业务数据、错误提示
- 排查重点：后端自定义错误码、报错描述、缺失字段
3. 文本查看
- 原始完整报文，处理中文乱码、特殊加密字符调试
4. 认证标签
- 单独提取、查看 Token、Cookie、登录凭证，快速核对认证信息
5. 十六进制查看
- 二进制、文件上传、加密接口底层报文排查

### 5.5 通用故障排查完整流程
1. 第一步：查看状态码，区分客户端 / 服务端问题
2. 第二步：核对 Request 请求信息
- 请求方法、URL 路径是否正确
- 请求头：是否携带 Token、Content-Type 格式是否匹配
- 请求体：参数是否完整、格式是否合规
3. 第三步：查看 Response 响应信息
- 响应数据格式是否符合预期
- JSON 返回的业务错误提示
- 跨域、权限相关响应头配置
4. 第四步：根据报文定位根因
- 401：缺少 Token/Token 失效
- 403：认证通过，但无访问权限
- 404：接口地址不存在
- 405：请求方法不匹配
- 400：请求参数错误、格式错误
- 500/502/503：后端服务异常、宕机、网关故障
