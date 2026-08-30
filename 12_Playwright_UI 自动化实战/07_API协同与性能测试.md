# 07 API 协同与性能测试

## 1. UI 和 API 的职责边界

| 能力 | UI 自动化 | API 自动化 |
|---|---|---|
| 验证真实用户路径 | 强 | 弱 |
| 执行速度 | 较慢 | 快 |
| 页面布局和交互 | 强 | 无法验证 |
| 数据准备/清理 | 易受页面影响 | 稳定高效 |
| 批量回归 | 资源消耗较高 | 更适合 |

合理的自动化不是所有事情都用 UI，也不是完全绕过 UI，而是按风险和成本分层。

## 2. Requests API 客户端结构

项目 API 客户端：

```text
../Ruoyi_full_auto_test/common/user_api.py
```

主要职责：

```text
创建 Session
  → 登录获取 token
  → 设置 Authorization 请求头
  → 统一发送请求
  → 解析 JSON
  → 检查业务 code
  → 提供用户增删改查方法
```

核心鉴权逻辑：

```python
response = session.post(
    f"{base_url}/login",
    json={"username": username, "password": password},
)
token = response.json()["token"]
session.headers.update({
    "Authorization": f"Bearer {token}"
})
```

## 3. HTTP 状态码和业务码要同时断言

只判断 HTTP 200 不够：

```python
assert response.status_code == 200
```

RuoYi 接口可能 HTTP 请求成功，但业务操作失败，因此还要检查：

```python
assert data["code"] == 200
```

完整判断：

```text
网络层：HTTP 状态码是否正常
业务层：JSON 中 code 是否成功
数据层：查询结果是否符合预期
```

## 4. 测试数据生命周期

API 用例推荐结构：

```python
user = build_unique_user(prefix="api_test_")
try:
    user_api.add_user(build_api_payload(user))
    ids = user_api.find_user_ids(user.username)
    assert len(ids) == 1
finally:
    user_api.cleanup_user_by_username(user.username)
```

数据状态应当是：

```text
不存在 → 创建 → 查询确认 → 修改/删除 → 再次查询确认不存在
```

## 5. JMeter 测试计划

文件位置：

```text
../Ruoyi_full_auto_test/performance/RuoYi_login_user_list.jmx
```

请求链路：

```text
登录 POST /login
  → JSON 提取器提取 $.token
  → Authorization: Bearer ${token}
  → 查询 GET /system/user/list
```

默认参数：

- 线程数：5
- Ramp-up：10 秒
- 每个线程循环：2 次
- Host：`localhost`
- Port：`8081`

命令行执行：

```powershell
jmeter -n `
  -t performance/RuoYi_login_user_list.jmx `
  -Jhost=localhost `
  -Jport=8081 `
  -Jusername=admin `
  -Jpassword=admin123 `
  -l reports/jmeter-results.jtl `
  -e -o reports/jmeter-html
```

## 6. 性能指标

| 指标 | 含义 |
|---|---|
| 平均响应时间 | 所有请求耗时的平均值 |
| P90/P95 | 90%/95% 请求不超过的响应时间 |
| 吞吐量 | 单位时间内完成的请求数量 |
| 错误率 | 失败请求占总请求的比例 |
| 并发用户数 | 同时发起业务操作的虚拟用户数量 |

性能测试不能只看平均值。平均值正常时，P95 可能已经很高，说明部分用户体验较差。

## 7. 性能测试执行原则

1. 先用 GUI 单线程验证登录和 token 提取。
2. 再用 5 并发建立基线。
3. 每次只改变一个主要变量，例如线程数或循环次数。
4. 同时记录服务端 CPU、内存、数据库连接数和错误日志。
5. 逐步加压，不要直接对开发机做大压力测试。
6. 性能结果要注明环境、时间、数据量和脚本参数。

## 8. 本章练习

- 用 Requests 手工调用登录接口并打印 token。
- 为用户查询接口增加一个筛选条件。
- 在 JMeter 中把线程数从 5 改为 10，比较 P95 和错误率。
- 解释为什么登录 token 不能写死在性能脚本里。