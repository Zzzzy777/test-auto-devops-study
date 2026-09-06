import allure
import pytest

from common.user_api import RuoYiApiError, RuoYiUserApi


@allure.feature("认证接口")
class TestLoginApi:
    @allure.story("登录成功")
    def test_login_success(self):
        result = RuoYiUserApi().login()
        assert result["code"] == 200
        assert result.get("token")

    @allure.story("登录失败")
    def test_login_wrong_password(self):
        with pytest.raises(RuoYiApiError, match="login failed"):
            RuoYiUserApi(password="wrong-password").login()