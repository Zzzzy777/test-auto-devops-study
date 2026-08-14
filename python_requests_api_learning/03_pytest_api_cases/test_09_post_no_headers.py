import requests

def test_post_no_headers():
    url = "https://httpbin.ceshiren.com/post"
    form_data = {"username": "testuser"}
    try:
        # 不传入headers参数
        resp = requests.post(url, data=form_data, timeout=10)
        res = resp.json()
        assert resp.status_code == 200
        # 校验使用requests默认ua，无自定义请求头
        assert res["headers"]["User-Agent"].startswith("python-requests")
        print("=== 不带请求头POST用例执行成功 ===")
    except AssertionError as e:
        print("断言失败：", e)
        raise
    except Exception as e:
        print("请求异常：", e)
        raise