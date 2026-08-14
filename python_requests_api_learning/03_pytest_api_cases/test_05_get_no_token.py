import requests
import json

def test_get_no_token():
    url = "https://httpbin.ceshiren.com/get"
    headers = {
         "User-Agent": "test-api"
    }

    try:
        resp =requests.get(url,headers=headers,timeout=10)
        res = resp.json()

        assert resp.status_code == 200
        assert "authorization" not in res["headers"], "无Token请求，响应头不应包含authorization"

        print("=== 无Token请求用例执行成功 ===")
    except AssertionError as e:
        print("断言失败：",e)
        raise
    except Exception as e:
        print("请求异常：",e)
        raise