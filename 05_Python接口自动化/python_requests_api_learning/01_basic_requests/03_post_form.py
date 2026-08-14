import requests
def post_form():
    url = "https://httpbin.org/post"
    # 表单参数 data
    data = {"username": "admin", "password": "123456"}
    try:
        # post + data传表单
        resp = requests.post(url, data=data, timeout=5)
        if resp.status_code == 200:
            print("=== POST表单提交成功 ===")
            print("状态码：", resp.status_code)
            print("返回内容：\n", resp.text)
        else:
            print("提交失败，状态码：", resp.status_code)
    except Exception as e:
        print("请求异常：", e)

if __name__ == "__main__":
    post_form()