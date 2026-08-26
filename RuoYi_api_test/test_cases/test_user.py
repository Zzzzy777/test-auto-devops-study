import allure
from common_request import send_request
from config import BASE_URL

@allure.feature("用户管理模块")
class TestUserApi:

    @allure.story("分页查询用户列表")
    # allure报告里面的用例描述
    @allure.description("查询系统用户列表，传入分页参数pageNum、pageSize，校验返回rows、total")
    def  test_query_user_list(self):
        #拼接查询用户列表
        url = f"{BASE_URL}/system/user/list"
        # get接口的查询参数，分页：第1页，每页10条
        params = {
            "pageNum": "1",
            "pageSzie": "10"
        }
        # get请求，带上鉴权头params传分页参数
        resp = send_request("GET", url, params=params)

        #http状态码校验
        assert resp.status_code == 200
        res = resp.json()
        # 业务成功码
        assert res["code"] == 200
        # 校验返回数据必须包含rows（数据列表）、total（总条数）
        assert "rows" in res
        assert "total" in res

    @allure.story("获取admin用户详情")
    # allure用例描述
    @allure.description("查询userId=1管理员详情，校验用户名称为admin")
    def test_get_user_detail(self):
        # 拼接id=1的用户详情接口地址
        url = f"{BASE_URL}/system/user/1"
        # 调用封装请求方法，不需要自己写token、headers
        resp = send_request("GET", url)

        #http状态码校验
        assert  resp.status_code == 200
        res = resp.json()
        # 业务成功码
        assert res["code"] == 200
        #校验是否为admin
        assert res["data"]["userName"] == "admin"
