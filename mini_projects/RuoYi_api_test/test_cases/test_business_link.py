import allure
from common_request import send_request
from config import BASE_URL


@allure.feature("业务链路_角色管理")
class TestBusinessRoleLink:

    @allure.story("角色完整业务链路：新增-查询-自动删除")
    @allure.description("业务链路用例：创建测试角色，查询校验，执行完成后finally自动删除，避免数据库残留脏数据。"
                        "角色分配菜单接口因版本差异暂注释，需要前端F12抓包拿到真实接口后再启用。")
    def test_role_business_flow(self):
        # 定义变量，接收新增出来的角色id
        role_id = None

        try:
            # ==========1、新增角色 POST /system/role ==========
            add_url = f"{BASE_URL}/system/role"
            add_body = {
                "roleName": "链路测试角色",
                "roleKey": "link_test_role",
                "roleSort": 2,
                "status": "0",
                "menuCheckStrictly": True,
                "deptCheckStrictly": True,
                "menuIds": []
            }
            resp_add = send_request("POST", add_url, json=add_body)
            res_add = resp_add.json()
            print(f"【新增角色】返回：{res_add}")

            # 断言新增成功
            assert resp_add.status_code == 200
            assert res_add["code"] == 200

            # ==========2、查询角色列表，拿到刚创建的roleId ==========
            list_url = f"{BASE_URL}/system/role/list"
            resp_list = send_request("GET", list_url, params={"roleName": "链路测试角色"})
            res_list = resp_list.json()
            print(f"【查询角色列表】返回：{res_list}")

            # 取出角色ID
            role_id = res_list["rows"][0]["roleId"]

            # ==========3、查询角色详情 ==========
            detail_url = f"{BASE_URL}/system/role/{role_id}"
            resp_detail = send_request("GET", detail_url)
            res_detail = resp_detail.json()
            print(f"【查询角色详情】返回：{res_detail}")
            assert res_detail["code"] == 200

            # ==========【待完善】分配菜单接口（当前版本不匹配，需要F12抓包获取真实接口再打开注释 ==========
            # assign_url = f"{BASE_URL}/xxx真实路径"
            # assign_body = {
            #     "roleId": role_id,
            #     "menuIds": [100,101]
            # }
            # resp_assign = send_request("PUT", assign_url, json=assign_body)
            # res_assign = resp_assign.json()
            # assert res_assign["code"] == 200

        finally:
            """无论上面用例成功还是失败，一定会执行，清理测试数据，防止脏数据留在数据库"""
            if role_id is not None:
                print(f"【finally执行】开始删除脏数据，role_id={role_id}")
                del_url = f"{BASE_URL}/system/role/{role_id}"
                resp_del = send_request("DELETE", del_url)
                res_del = resp_del.json()
                assert resp_del.status_code == 200
                assert res_del["code"] == 200
                print(f"【finally执行】角色删除完成")

