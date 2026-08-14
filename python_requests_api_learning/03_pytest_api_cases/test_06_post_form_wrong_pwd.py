import requests
import json

def test_post_form_wrong_pwd():
    url = "https://httpbin.ceshiren.com/post"
    headers = {
        "User-Agent": "test-api"
    }
    form_data = {
        "username":"Zy",
        "password":"wrongpass"
    }

    try:
        resp =requests.post(url,headers=headers,data=form_data,timeout=10)
        res = resp.json()

        assert resp.status_code == 200
        assert res["form"]["password"] != "123456","表单密码参数错误"
        print("=== 表单密码错误用例执行成功 ===")
    except AssertionError as e:
        print("断言失败：", e)
        raise
    except Exception as e:
        print("请求异常：", e)
        raise