import requests
import json

def test_post_form_data():
    url = "https://httpbin.ceshiren.com/post"
    headers = {
        "User-Agent": "test-api-script"
    }
    cookies = {"session_id":"abc666"}
    data = {
        "username":"admin",
        "password":"123456"
    }
    try:
        resp = requests.post(url,headers=headers,data=data,cookies=cookies,timeout=10)
        res = resp.json()

        assert resp.status_code == 200,f"状态码异常，实际:{resp.status_code}"
        assert res["form"]["username"] == "admin","用户名不匹配"
        assert res["form"]["password"] == "123456","密码不匹配"

        print("=== 表单POST请求成功 ===")
        print("返回数据:\n",json.dumps(res , indent=2,ensure_ascii=False))

    except AssertionError as e:
        print("断言失败",e)
        raise
    except Exception as e:
        print("请求异常:",e)
        raise
