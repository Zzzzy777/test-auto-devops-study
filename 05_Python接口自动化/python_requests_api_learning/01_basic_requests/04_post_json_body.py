import requests

def post_json():
    url = "https://httpbin.ceshiren.com/post"
    json_data = {"phone":"18024667788","code":"123456"}
    try:
        resp = requests.post(url,json=json_data,timeout=5)
        if resp.status_code == 200:
            print("=== POST-JSON请求成功 ===")
            print("状态码:",resp.status_code)
            print("结构化json:",resp.json())
            print("cookies:",resp.cookies)
        else:
            print("请求失败，状态码：", resp.status_code)
    except Exception as e:
        print("请求异常：", e)

if __name__ == "__main__":
    post_json()