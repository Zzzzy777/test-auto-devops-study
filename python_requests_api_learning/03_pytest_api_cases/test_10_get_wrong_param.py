import requests

def test_get_wrong_param():
    url = "https://httpbin.ceshiren.com/get"
    # 预期参数id，错误传user_id
    params = {"user_id": "1001"}
    try:
        resp = requests.get(url, params=params, timeout=10)
        res = resp.json()
        assert resp.status_code == 200
        assert "id" not in res["args"], "正确参数id不存在"
        assert res["args"]["user_id"] == "1001", "错误参数user_id正常携带"
        print("=== 错误查询参数用例执行成功 ===")
    except AssertionError as e:
        print("断言失败：", e)
        raise
    except Exception as e:
        print("请求异常：", e)
        raise