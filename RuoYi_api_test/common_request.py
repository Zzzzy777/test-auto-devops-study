import requests
from config import BASE_URL, USERNAME, PASSWORD
# 全局变量存储token
global_token = None


def login_get_token():
    """
    执行登录接口，获取新token
    :return: 返回最新token字符串
    """
    global global_token
    login_url = f"{BASE_URL}/login"
    data = {
        "username": USERNAME,
        "password": PASSWORD
    }
    # 发送登录请求
    try:
        resp = requests.post(url=login_url, json=data, timeout=10)
    # 捕获所有requests网络异常：超时、连接拒绝、断网
    except requests.exceptions.RequestException as e:
        print(f"【登录接口网络异常】 url:{login_url}，异常详情: {e}")
        # 捕获后重新抛出异常，交给pytest识别用例失败，不能吞报错
        raise

    # 打印完整响应，排查问题用
    print("登录接口HTTP状态码：", resp.status_code)
    res = resp.json()
    print("登录接口返回内容：", res)  # 运行后终端会显示完整报错
    assert resp.status_code == 200
    assert res["code"] == 200, f"登录失败，错误信息：{res.get('msg')}"
    global_token = res["token"]
    return global_token


def send_request(method: str, url: str, **kwargs):
    """
    统一封装http请求方法
    ✨能力：自动维护token，遇到401鉴权失效自动重登录，仅重试1次，防止死循环
    ✨增强：捕获网络层异常，打印日志，不吞噬异常
    :param method: 请求方式 "GET" / "POST"
    :param url: 接口完整地址
    :param kwargs: 可变参数，可以传json、params、headers等requests原生参数
    :return: requests响应对象response
    """
    global global_token
    # 如果全局没有token，先登录获取token
    if global_token is None:
        login_get_token()

    # 组装默认鉴权请求头，若依要求 Authorization: Bearer 空格+token
    inner_headers = {
        "Authorization": f"Bearer {global_token}",
        "Content-Type": "application/json"
    }

    # 如果调用方传入自定义headers，自定义headers优先级更高，覆盖默认头
    if "headers" in kwargs:
        inner_headers.update(kwargs["headers"])
    kwargs["headers"] = inner_headers

    # 第一次发起接口请求
    try:
        resp = requests.request(method=method, url=url, timeout=10, **kwargs)
    except requests.exceptions.RequestException as e:
        print(f"【接口请求网络异常】method:{method} url:{url}，异常:{e}")
        raise

    # 判断返回401 → token过期 / token无效，触发重登逻辑
    if resp.status_code == 401:
        # 重新登录拿全新token
        login_get_token()
        # 更新鉴权头里面的token
        inner_headers["Authorization"] = f"Bearer {global_token}"
        kwargs["headers"] = inner_headers
        # 使用新token重试本次接口，只重试1次，避免死循环
        try:
            resp = requests.request(method=method, url=url, timeout=10, **kwargs)
        except requests.exceptions.RequestException as e:
            print(f"【401重登后重试网络异常】method:{method} url:{url}，异常:{e}")
            raise

    return resp
