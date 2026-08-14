import requests


def post_json_body():
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
      assert res["json"]["name"] == "Zy"
      assert res["json"]["id"] == 107
      print("✅全部断言通过")
      print("返回文本:\n",resp.text)

    except AssertionError as e:
        print("断言失败",e)
    except Exception as e:
          print("请求异常：", e)

if __name__ == "__main__":
    post_json_body()