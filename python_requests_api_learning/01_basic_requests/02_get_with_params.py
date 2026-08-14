import requests
def get_params():
    url = 'https://httpbin.ceshiren.com/get'
    params = {"name":"测试用户","id":10086}
    try:
        resp = requests.get(url,params=params,timeout=5)
        if resp.status_code  == 200:
           print("=== GET带参数请求成功 ===")
           print("状态码:",resp.status_code)
           print("json返回:",resp.json())
        else:
           print("请求失败，状态码:",resp.status_code)
    except Exception as e:
        print("请求异常：", e)

if __name__ == "__main__":
    get_params()