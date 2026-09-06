import allure
from common_request import send_request
from config import BASE_URL


@allure.feature("角色管理模块")
class TestRoleApi:
    @allure.story("查询角色列表")
    @allure.description("查询系统全部角色列表接口，校验返回rows数组")
    def test_query_role_list(self):
        url = f"{BASE_URL}/system/role/list"
        resp = send_request("GET", url)
        assert resp.status_code == 200
        res = resp.json()
        assert res["code"] == 200
        assert "rows" in res

    @allure.story("角色菜单分配")
    @allure.description("异常场景：给角色分配不存在的menuId，校验后端处理逻辑")
    def test_role_assign_not_exist_menu(self):
        url = f"{BASE_URL}/system/role/menu"
        body = {
            "roleId": 2,
            "menuIds": [99999]   # 传入不存在菜单ID
        }
        resp = send_request("PUT", url, json=body)
        print(f"状态码: {resp.status_code}")
        print(f"返回报文: {resp.text}")
    
        assert resp.status_code == 200
        res = resp.json()
        print(f"接口完整返回:{res}")


@allure.feature("角色管理模块")
@allure.story("角色新增")
@allure.description("正向场景：新增测试角色，查询校验，最后自动清理脏数据")
def test_role_add_assign_menu():
    role_id = None
    try:
        # 步骤1：新增角色
        add_role_url = f"{BASE_URL}/system/role"
        add_role_body = {
            "roleName": "自动化测试角色",
            "roleKey": "auto_test_role",
            "roleSort": 1,
            "status": "0",
            "menuCheckStrictly": True,
            "deptCheckStrictly": True,
            "menuIds": []
        }
        add_resp = send_request("POST", add_role_url, json=add_role_body)
        add_res = add_resp.json()
        print(f"新增角色接口返回完整:{add_res}")
        assert add_resp.status_code == 200
        assert add_res["code"] == 200

        # 步骤2：查询获取roleId
        query_url = f"{BASE_URL}/system/role/list"
        query_resp = send_request("GET", query_url, params={"roleName": "自动化测试角色"})
        query_res = query_resp.json()
        role_id = query_res["rows"][0]["roleId"]

        # ==========这里暂时注释分配菜单，接口版本对不上，后续抓包后再补==========
        # assign_url = f"{BASE_URL}/system/role/menu"
        # assign_body = {
        #     "roleId": role_id,
        #     "menuIds": [100, 101]
        # }
        # assign_resp = send_request("POST", assign_url, json=assign_body)
        # assign_res = assign_resp.json()
        # print(f"分配权限接口返回：{assign_res}")
        # assert assign_res["code"] == 200

        # 步骤3：查询角色详情
        detail_url = f"{BASE_URL}/system/role/{role_id}"
        detail_resp = send_request("GET", detail_url)
        detail_res = detail_resp.json()
        print(f"角色详情查询结果：{detail_res}")
        assert detail_res["code"] == 200

    finally:
        if role_id is not None:
            print(f"进入finally，开始清理测试角色 role_id={role_id}")
            del_role_url = f"{BASE_URL}/system/role/{role_id}"
            del_resp = send_request("DELETE", del_role_url)
            del_res = del_resp.json()
            assert del_resp.status_code == 200
            assert del_res["code"] == 200
            print("测试角色清理完成")


