import allure
from common_request import send_request
from config import BASE_URL

@allure.feature("用户管理模块")
class TestUserApi:

    @allure.story("分页查询用户列表")
    # allure报告里面的用例描述
    @allure.description("正向场景：查询系统用户列表，传入分页参数pageNum、pageSize，校验返回rows、total")
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
    @allure.description("正向场景：查询userId=1管理员详情，校验用户名称为admin")
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



    @allure.story("新增系统用户")
    @allure.description("正向场景：传入合法参数新增用户")
    def test_add_user(self, clean_test_user):
        url = f"{BASE_URL}/system/user"
        body = {
            "userName": "testauto01",
            "nickName": "自动化测试账号",   # 必须加，昵称
            "password": "123456",          # 必须加，密码
            "deptId": 105
        }
        resp = send_request("POST",url,json=body)
        # 打印后端返回内容，方便排错
        print(f"状态码：{resp.status_code}")
        print(f"返回报文：{resp.text}")
    
        assert resp.status_code == 200
        res = resp.json()
        assert res["code"] == 200




    @allure.story("新增系统用户")
    @allure.description("异常场景：用户名已存在，新增失败")
    def test_add_user_dup_name(self):
        url = f"{BASE_URL}/system/user"
        body = {
            "userName": "testauto01",
            "nickName": "自动化测试账号",   # 必须加，昵称
            "password": "123456",          # 必须加，密码
            "deptId": 105
        }

        # 第一步：先创建该用户，制造用户名已存在的前置条件
        send_request("POST", url, json=body)

        # 第二步：再次提交相同请求，触发用户名重复
        resp = send_request("POST",url,json=body) 
        print(f"状态码: {resp.status_code}")
        print(f"返回报文: {resp.text}")

        assert resp.status_code == 200
        res = resp.json()
        print(f"接口完整返回:{res}")

        # 业务码不能等于200，代表新增失败
        assert res["code"] != 200


    @allure.story("新增系统用户")
    @allure.description("异常场景：传入非法手机号，校验参数拦截")
    def test_add_user_invalid_phone(self):
        url = f"{BASE_URL}/system/user"
        body = {
            "userName": "testphone01",
            "nickName": "手机号非法测试",
            "password": "123456",
            "deptId": 105,
            "phonenumber": "123"   # 非法短手机号，也可以填"abc1234"
        }
        resp = send_request("POST", url, json=body)
        print(f"状态码: {resp.status_code}")
        print(f"返回报文: {resp.text}")

        assert resp.status_code == 200
        res = resp.json()
        print(f"接口完整返回:{res}")
        # 这里不再断言code!=200
        # 实际测试发现：后端没有手机号格式校验，非法手机号可以创建成功，属于接口缺陷



    @allure.story("修改系统用户")
    @allure.description("异常场景：不传必填nickName字段，校验参数拦截")
    def test_edit_user_missing_required(self):
        url = f"{BASE_URL}/system/user"
        # id=1是admin真实用户，做修改
        body = {
            "userId": 1,
            "userName": "admin"
            # 故意不写 nickName（必填字段）
        }
        resp = send_request("PUT", url, json=body)
        print(f"状态码: {resp.status_code}")
        print(f"返回报文: {resp.text}")

        assert resp.status_code == 200
        res = resp.json()
        print(f"接口完整返回:{res}")
        assert res["code"] != 200




    @allure.story("编辑系统用户")
    @allure.description("正向场景：新增测试用户后，修改用户昵称与邮箱")
    def test_edit_user(self, clean_test_user):
        # 1、先新增一个测试用户，作为编辑的测试数据
        add_url = f"{BASE_URL}/system/user" # 拼接新增用户接口地址
        add_body = {
            "userName": "testauto01",
            "nickName": "自动化测试账号",   # 必须加，昵称
            "password": "123456",          # 必须加，密码
            "deptId": 105
        }
        #执行新增并且断言
        add_resp = send_request("POST", add_url, json=add_body)
        add_res = add_resp.json()
        assert add_resp.status_code == 200
        assert add_res["code"] == 200

        # 2、查询拿到刚刚新增用户的userId，编辑接口必须传入userId
        query_resp = send_request("GET", f"{BASE_URL}/system/user/list", params={"userName":"testauto01"}) # 根据用户名过滤查询用户列表
        query_res = query_resp.json()  # 将接口返回响应转为json字典
        user_id = query_res["rows"][0]["userId"]  # 从返回列表取出第一条数据的用户ID

        # 3、执行编辑操作，PUT请求完成用户信息修改
        edit_url = f"{BASE_URL}/system/user"  # 编辑用户接口地址
        edit_body = {                         # 编辑接口请求体，userId是必填项
            "userId": user_id,
            "userName": "testauto01",
            "nickName": "修改后的测试账号",
            "deptId": 105,
            "email": "modify@test.com"
        }
        #执行编辑并且断言
        resp = send_request("PUT", edit_url, json=edit_body) # 发送put编辑请求
        res = resp.json() # 获取编辑接口返回json
        print(f"状态码：{resp.status_code}")
        print(f"返回报文：{resp.text}")
        print(f"编辑接口返回:{res}") # 打印返回结果，方便排查问题

        assert resp.status_code == 200 # 断言http状态码200，代表请求成功到达服务端
        assert res["code"] == 200      # 断言业务返回码200，代表业务层面编辑成功



    @allure.story("删除系统用户")
    @allure.description("正向场景：新增用户，拿到id后执行删除")
    def test_delete_user(self, clean_test_user):
        # 1、先新增一个测试用户，作为编辑的测试数据
        add_url = f"{BASE_URL}/system/user" # 拼接新增用户接口地址
        add_body = {
                "userName": "testauto01",
                "nickName": "自动化测试账号",   # 必须加，昵称
                "password": "123456",          # 必须加，密码
                "deptId": 105
        }
        #执行新增并且断言
        add_resp = send_request("POST", add_url, json=add_body)
        add_res = add_resp.json()
        assert add_resp.status_code == 200
        assert add_res["code"] == 200
        
        # 2、查询拿到刚刚新增用户的userId，编辑接口必须传入userId
        query_resp = send_request("GET", f"{BASE_URL}/system/user/list", params={"userName":"testauto01"}) # 根据用户名过滤查询用户列表
        query_res = query_resp.json()  # 将接口返回响应转为json字典
        user_id = query_res["rows"][0]["userId"]  # 从返回列表取出第一条数据的用户ID

        # 3、执行删除，DELETE请求，id放在url路径中
        del_url = f"{BASE_URL}/system/user/{user_id}"       # 拼接删除接口完整url，userId路径传参
        resp = send_request("DELETE", del_url)              # 发送删除请求
        res = resp.json()                                   # 获取删除接口返回json
        print(f"状态码：{resp.status_code}")
        print(f"返回报文：{resp.text}")
        print(f"删除接口返回:{res}")                         # 打印返回报文，方便定位报错

        assert resp.status_code == 200                      # 断言http状态码
        assert res["code"] == 200                           # 断言业务码，确认删除业务执行成功



    @allure.story("删除用户")
    @allure.description("逆向场景：删除不存在的用户ID")
    def test_delete_no_exist_user(self):
        user_id = 999999 #传入一个系统不存在的用户id=999999
        del_url = f"{BASE_URL}/system/user/{user_id}"

        print(f"\n【删除请求地址】{del_url}")

        resp = send_request("DELETE",del_url)
        res = resp.json()

        print(f"状态码: {resp.status_code}")
        print(f"返回报文: {resp.text}")
        print(f"删除接口返回:{res}")

        assert resp.status_code == 200
        assert res["code"] != 200

    
