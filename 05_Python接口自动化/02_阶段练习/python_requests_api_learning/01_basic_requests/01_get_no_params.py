import requests
def get_no_param():
    url = "https://httpbin.ceshiren.com/get"
    try:
        #GET无参，只传url和timeout
        resp = requests.get(url,timeout=5)
        if resp.status_code == 200:
            print("=== GET无参请求成功 ===")
            print("状态码:",resp.status_code)
            print("响应文本:\n",resp.text)
            print("响应头:",resp.headers)
        else:
            print("请求头异常，状态码：",resp.status_code)
    except Exception as e:
        print("请求异常:",e)

if __name__ == "__main__":
    get_no_param()