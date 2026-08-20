import requests
import json

def test_post_json_empty_phone():
    url = "https://httpbin.ceshiren.com/post"
    headers = {
        "User-Agent": "test-api",
        "Content-Type": "application/json"
    }
    json_body = {
        "phone": "",
        "name": "测试用户"
    }
    try:
        resp = requests.post(url, headers=headers, json=json_body, timeout=10)
        res = resp.json()
        assert resp.status_code == 200
        assert res["json"]["phone"] == "","预期手机号为空，但接口收到的手机号不为空"
        print("=== 空手机号json请求用例执行成功 ===")
    except AssertionError as e:
        print("断言失败：", e)
        raise
    except Exception as e:
        print("请求异常：", e)
        raise