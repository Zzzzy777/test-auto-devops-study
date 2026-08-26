import allure
from common_request import send_request
from config import BASE_URL

# allure模块标记：部门管理模块
@allure.feature("部门管理模块")
#部门接口测试类
class TestDeptApi:
    @allure.story("查询部门列表")
    @allure.description("查询系统部门树形列表接口")
    # 查询部门列表用例
    def test_query_dept_list(self):
        # 拼接部门列表接口url
        url = f"{BASE_URL}/system/dept/list"
        # 调用封装请求，内部自动处理token和401重登
        resp = send_request("GET", url)
        assert resp.status_code == 200

        # 响应转为json字典
        res = resp.json()
        # 核心：打印完整返回，看真实字段，不要凭脑子记
        print(f"接口完整返回:{res}")
        # 断言业务返回码200
        assert res["code"] == 200
        # 断言返回rows字段
        assert "data" in res