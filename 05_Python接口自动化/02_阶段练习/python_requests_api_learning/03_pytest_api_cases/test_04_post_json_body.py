import requests
import json

def test_post_json_body():
    url  = "https://httpbin.ceshiren.com/post"
    headers = {
        "User-Agent":"test-api-scrip",
        "Authorizaton":"Bearer json_token_789"
    }
    json_body= {
        "name":"Zy",
        "id":107}
    try:
      resp = requests.post(url,headers=headers,json=json_body,timeout=10)
      res = resp.json()

      assert resp.status_code == 200
      assert res["headers"]["Authorizaton"] == "Bearer json_token_789"
      assert res["json"]["name"] == "Zy","用户名错误"
      assert res["json"]["id"] == 107,"id不正确"

      print("=== JSON POST请求成功 ===")
      print("返回文本:\n",json.dumps(res , indent=2,ensure_ascii=False))
      print("cookies:",resp.cookies)
    except AssertionError as e:
        print("断言失败",e)
        raise
    except Exception as e:
        print("请求异常：", e)
        raise

