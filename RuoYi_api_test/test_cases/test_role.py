import allure
from common_request import send_request
from config import BASE_URL

# allure标记模块：角色管理模块
@allure.feature("角色管理模块")
# 角色接口测试类
class TestRoleApi:
    # allure故事标签
    @allure.story("查询角色列表")
    # allure用例描述
    @allure.description("查询系统全部角色列表接口，校验返回rows数组")
    # 查询角色列表用例
    def test_query_role_list(self):
        # 拼接角色列表接口url
        url = f"{BASE_URL}/system/role/list"
        # 调用封装请求，自动处理token鉴权
        resp = send_request("GET", url)
        #http状态码校验
        assert resp.status_code == 200


        # 响应转json
        res = resp.json()
        # 断言业务码200
        assert res["code"] == 200
        # 断言返回rows字段
        assert "rows" in res
