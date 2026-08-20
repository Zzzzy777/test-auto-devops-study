import requests
import json

def test_get_no_param():
    url = "https://httpbin.ceshiren.com/get"
    headers = {
        "User-Agent":"test-api-script",
        "token":"abc123456"
    }
    try:
        #GET无参，只传url和timeout
        resp = requests.get(url,headers=headers,timeout=10)
        res = resp.json()

        #断言
        assert resp.status_code == 200,f"状态码异常，实际:{resp.status_code}"
        assert res["headers"]["Token"] == "abc123456","token传递失败"
        assert res["args"] == {},"无参接口不应该携带参数"

        print("=== 无参GET请求成功 ===")
        print("返回数据:\n", json.dumps(res, indent=2, ensure_ascii=False))
    except AssertionError as e:
        print("❌ 断言失败：",e)
        raise # 抛出异常，让pytest标记用例失败
    except Exception as e:
        print("❌ 请求异常:",e)
        raise