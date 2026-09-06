"""
登录接口测试。
覆盖：
1. 正确账号密码登录；
2. 错误密码登录；
3. Token 是否返回；
4. 登录失败是否能被统一异常捕获。
5. 密码为空
6. 登录成功后获取 token
7. token 失效访问接口
8. 未携带 token 访问接口
"""

import allure
import pytest

from common.http_client import RuoYiApiError
from common.user_api import RuoYiUserApi


@pytest.mark.api
@allure.feature("登录鉴权模块")
class TestLoginApi:
    """登录接口测试类。"""

    @allure.story("正确账号密码登录")
    def test_login_success(self) -> None:
        """
        正向场景：

        正确账号密码应登录成功，
        并返回非空 Token。
        """
        api = RuoYiUserApi()
        result = api.login()

        assert result["code"] == 200
        assert result.get("token")

    @allure.story("错误密码登录")
    def test_login_wrong_password(self) -> None:
        """
        反向场景：

        错误密码不应登录成功，
        客户端应抛出统一的 RuoYiApiError。
        """
        api = RuoYiUserApi(
            username="admin",
            password="wrong-password"
        )

        with pytest.raises(
            RuoYiApiError,
            match=r".*用户不存在/密码错误.*",
        ):
            api.login()

    @allure.story("不存在的账号登陆")
    def test_no_exist_account(self) -> None:
        """
        反向场景：
    
        不存在的账户不应登录成功，
        客户端应抛出统一的 RuoYiApiError。
        """
        api = RuoYiUserApi(
        username="no_exist_username",
        password="admin123"
        )
    
        with pytest.raises(
        RuoYiApiError,
        match=r".*用户不存在/密码错误.*",
        ):
            api.login()

    @allure.story("用户名为空登陆")
    def test_no_username_login(self) -> None:
        """
        反向场景：
        
        用户名为空不应登录成功，
        客户端应抛出统一的 RuoYiApiError。
        """
        api = RuoYiUserApi(
        username="",
        password="admin123"
        )
        
        with pytest.raises(
        RuoYiApiError,
        match=r".*用户不存在/密码错误.*",
        ):
            api.login()

    @allure.story("密码为空")
    def test_no_password_login(self) -> None:
        """
        反向场景：
        密码为空不应登录成功，
        客户端应抛出统一的 RuoYiApiError。
        """
        api = RuoYiUserApi(
            username="admin",
            password=""
        )
        with pytest.raises(
            RuoYiApiError,
            match=r".*用户不存在/密码错误.*",
        ):
            api.login()

    @allure.story("登录成功后获取token")
    def test_login_success_obtain_token(self) -> None:
        """
        正向场景：
        登录成功，校验实例拿到不为空的token。
        """
        api = RuoYiUserApi()
        res = api.login()
        assert res["code"] == 200
        # 校验响应有token，同时校验api对象内部token赋值成功
        assert res.get("token") is not None
        assert len(res.get("token")) > 10

    @allure.story("失效token访问接口")
    def test_access_api_invalid_token(self) -> None:
        """
        反向场景：使用伪造 Token 访问需要鉴权的接口。
        后端应返回业务 code=401，且客户端不应自动重新登录。
        """
        api = RuoYiUserApi()
        api.token = "fake_token_1234567890_fake_fake"

        with pytest.raises(RuoYiApiError, match=r"认证失败|code.?401"):
            api.get_user_list(
                auth=True, #表示正常使用鉴权，会携带 Token。
                retry_on_401=False, #表示收到鉴权失败后不自动重新登录，专门用于验证失效 Token。
            )

    @allure.story("未携带token访问接口")
    def test_access_api_without_token(self) -> None:
        """
        反向场景：明确关闭鉴权访问用户列表。
        请求不应触发自动登录，后端应返回业务 code=401。
        """
        api = RuoYiUserApi()
        api.token = None

        with pytest.raises(RuoYiApiError, match=r"认证失败|code.?401"):
            api.get_user_list(
                auth=False, #表示明确不登录、不携带 Token，专门用于测试未授权访问。
                retry_on_401=False, #表示收到鉴权失败后不自动重新登录，专门用于验证失效 Token。
            )

