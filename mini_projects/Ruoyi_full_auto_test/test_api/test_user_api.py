import allure
import pytest

from common.test_data import UserData, build_unique_user
from common.user_api import RuoYiApiError


DEFAULT_DEPT_ID = 105


def build_api_payload(user: UserData) -> dict[str, object]:
    return {
        "userName": user.username,
        "nickName": user.nickname,
        "password": user.password,
        "deptId": DEFAULT_DEPT_ID,
    }


@pytest.fixture
def created_api_user(user_api):
    user = build_unique_user(prefix="api_test_")
    payload = build_api_payload(user)
    try:
        result = user_api.add_user(payload)
        assert result["code"] == 200
        yield user
    finally:
        user_api.cleanup_user_by_username(user.username)


@allure.feature("用户管理接口")
class TestUserApi:
    @allure.story("用户查询")
    def test_query_user_by_exact_username(self, user_api, created_api_user):
        user_ids = user_api.find_user_ids(created_api_user.username)
        assert len(user_ids) == 1

        detail = user_api.get_user_detail(user_ids[0])
        assert detail["data"]["userName"] == created_api_user.username

    @allure.story("用户新增")
    def test_add_user(self, user_api):
        user = build_unique_user(prefix="api_test_")
        try:
            result = user_api.add_user(build_api_payload(user))
            assert result["code"] == 200
            assert user_api.find_user_ids(user.username)
        finally:
            user_api.cleanup_user_by_username(user.username)

    @allure.story("重复用户名")
    def test_add_user_duplicate_username(self, user_api, created_api_user):
        with pytest.raises(RuoYiApiError, match="request failed"):
            user_api.add_user(build_api_payload(created_api_user))

    @allure.story("用户删除和删除后校验")
    def test_delete_user_and_verify_absent(self, user_api, created_api_user):
        user_ids = user_api.find_user_ids(created_api_user.username)
        assert len(user_ids) == 1
        user_api.delete_user(user_ids[0])
        assert user_api.find_user_ids(created_api_user.username) == []

    @allure.story("删除不存在用户")
    def test_delete_nonexistent_user(self, user_api):
        with pytest.raises(RuoYiApiError, match="request failed"):
            user_api.delete_user(999999)