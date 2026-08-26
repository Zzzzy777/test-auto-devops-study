import allure
from common_request import send_request
from config import BASE_URL

# allure模块标记：菜单管理模块
@allure.feature("菜单管理模块")
# 菜单接口测试类
class TestMenuApi:
    @allure.story("查询菜单列表")
    @allure.description("查询系统菜单树形列表接口")
    # 查询菜单列表用例
    def test_query_menu_list(self):
        # 拼接菜单列表接口地址
        url = f"{BASE_URL}/system/menu/list"
        # 调用封装后的请求函数，自动处理token
        resp = send_request("GET", url)
        assert resp.status_code == 200

        # 转json
        res = resp.json()
        # 核心：打印完整返回，看真实字段，不要凭脑子记
        print(f"接口完整返回:{res}")
        #断言业务码200
        assert res["code"] == 200
        # 断言存在rows字段
        assert "data" in res