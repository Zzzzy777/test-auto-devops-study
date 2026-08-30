# 测试用例矩阵

| 编号 | 层级 | 场景 | 前置条件 | 关键步骤 | 预期结果 | 自动化位置 |
|---|---|---|---|---|---|---|
| UI-LOGIN-001 | UI | 管理员登录成功 | 前端可用，账号有效 | 输入账号密码并登录 | 跳转首页，出现系统首页特征元素 | `test_ui/test_ruoyi_login.py` |
| UI-USER-001 | UI | 新增用户成功 | 已登录 | 打开用户管理，填写唯一用户并提交 | 成功提示出现，列表可搜索到用户 | `test_ui/test_ruoyi_user_add.py` |
| UI-USER-002 | UI | 必填校验 | 已登录 | 新增弹窗不填必填项直接提交 | 表单提示必填，不能创建 | `test_ui/test_ruoyi_user_required.py` |
| UI-USER-003 | UI | 重复用户名 | 已存在同名用户 | 再次提交相同用户名 | 出现业务错误提示，不误判为成功 | `test_ui/test_ruoyi_user_duplicate.py` |
| UI-USER-004 | UI | 用户搜索 | 存在目标用户 | 输入用户名搜索 | 表格只展示目标用户 | `test_ui/test_ruoyi_user_search.py` |
| UI-USER-005 | UI | 编辑用户 | 存在目标用户 | 修改昵称和手机号并保存 | 成功提示出现，列表显示新值 | `test_ui/test_ruoyi_user_edit.py` |
| API-LOGIN-001 | API | 登录成功 | 后端可用，账号有效 | POST `/login` | HTTP 200，业务 `code=200`，返回 token | `test_api/test_login_api.py` |
| API-LOGIN-002 | API | 登录失败 | 后端可用 | 使用错误密码登录 | 返回业务失败，不返回有效 token | `test_api/test_login_api.py` |
| API-USER-001 | API | 新增用户 | 已获取 token | POST `/system/user` | 创建成功，可按用户名查询 | `test_api/test_user_api.py` |
| API-USER-002 | API | 删除后查询 | 已创建测试用户 | DELETE 后再次 GET 列表 | 查询不到该测试用户 | `test_api/test_user_api.py` |
| PERF-001 | 性能 | 登录基线 | 后端可用 | JMeter 5 并发、2 循环 | 记录平均响应时间、P95、吞吐量、错误率 | `performance/RuoYi_login_user_list.jmx` |
