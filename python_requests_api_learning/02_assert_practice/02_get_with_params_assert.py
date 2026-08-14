import requests

def get_with_params():
    url = 'https://httpbin.ceshiren.com/get'
    headers = {
        "Use-Agent":"test-api-scrip",
        "token":"abc123456"
    }

    params = {
        "name":"测试用户",
        "id":10086
    }

    try:
        resp = requests.get(url,headers=headers,params=params,timeout=10)
        res =resp.json()

        assert resp.status_code == 200,f"状态码异常，实际：{resp.status_code}"
        assert res["args"]["name"] == "测试用户","name参数不匹配"
        assert res["args"]["id"] == "10086","id不匹配"
        assert res["headers"]["Token"] == "abc123456","token不匹配"
        print("✅ 全部断言通过")
        print("返回数据:",resp.text)

    except AssertionError as e:
        print("断言失败:",e)
    except Exception as e:
        print("请求异常：", e)

if __name__ == "__main__":
    get_with_params()