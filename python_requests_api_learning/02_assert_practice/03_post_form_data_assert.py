import requests


def post_form_data():
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
        resp = requests.post(url,headers=headers,data=data,timeout=10)
        res = resp.json()
        assert resp.status_code == 200,f"状态码异常，实际:{resp.status_code}"
        assert res["form"]["username"] == "admin","用户名不匹配"
        assert res["form"]["password"] == "123456","密码不匹配"
        print("✅ 全部断言通过")
        print(resp.text)

    except AssertionError as e:
        print("断言失败",e)
    except Exception as e:
        print("请求异常:",e)

if __name__== "__main__":
    post_form_data()