import requests
from requests.exceptions import Timeout

def test_get_timeout():
    url = "https://httpbin.ceshiren.com/delay/3"
    try:
        # 设置1秒超时，接口延迟3s返回，必然超时
        resp = requests.get(url, timeout=1)
        # 正常不会走到这行，走到代表超时失败
        assert False, "接口未触发超时，用例失败"
    except Timeout:
        print("=== 超时场景用例执行成功，捕获超时异常 ===")
    except Exception as e:
        print("请求异常：", e)
        raise