"""
用户管理接口测试。

覆盖：

- 用户查询；
- 用户新增；
- 重复用户名；
- 用户修改；
- 用户删除；
- 删除后校验；
- 删除不存在用户；
- 动态数据和自动清理。
"""

from __future__ import annotations

import allure
import pytest

from common.http_client import RuoYiApiError
from common.config import DEFAULT_DEPT_ID
from common.test_data import (
    UserData,
    build_unique_user,
    build_user_payload,
)


# RuoYi 默认部门 ID。
# 如果你的环境部门 ID 不同，后续可以放进 config.py。
DEFAULT_DEPT_ID = 105


@pytest.fixture
def created_api_user(user_api):
    """
    创建一个 API 测试用户。

    测试结束后无论成功失败都会清理。
    """
    user = build_unique_user(
        prefix="api_test_"
    )

    try:
        result = user_api.add_user(
            build_user_payload(user)
        )

        assert result["code"] == 200

        yield user

    finally:
        user_api.cleanup_user_by_username(
            user.username
        )


@pytest.mark.api
@allure.feature("用户管理接口")
class TestUserApi:
    """用户管理 API 测试类。"""

    @allure.story("查询用户详情")
    def test_query_user(
        self,
        user_api,
        created_api_user,
    ) -> None:
        """
        创建用户后，根据用户名查询 ID，
        再查询详情并校验用户名。
        """
        user_ids = user_api.find_user_ids(
            created_api_user.username
        )

        assert len(user_ids) == 1

        detail = user_api.get_user_detail(
            user_ids[0]
        )

        assert detail["data"]["userName"] == (
            created_api_user.username
        )

    @allure.story("新增用户")
    def test_add_user(
        self,
        user_api,
    ) -> None:
        """
        验证用户新增成功，
        并且新增数据可以被查询到。
        """
        user = build_unique_user(
            prefix="api_test_"
        )

        try:
            result = user_api.add_user(
                build_user_payload(user)
            )

            assert result["code"] == 200
            assert user_api.find_user_ids(
                user.username
            )

        finally:
            user_api.cleanup_user_by_username(
                user.username
            )

    @allure.story("重复用户名")
    def test_duplicate_username(
        self,
        user_api,
        created_api_user,
    ) -> None:
        """
        同一个用户名不能重复创建。
        """
        duplicate_payload = build_user_payload(
            created_api_user
        )

        with pytest.raises(
            RuoYiApiError,
            match="request failed",
        ):
            user_api.add_user(
                duplicate_payload
            )

    @allure.story("修改用户")
    def test_update_user(
        self,
        user_api,
        created_api_user,
    ) -> None:
        """
        创建用户后修改昵称和手机号，
        再查询详情确认修改结果。
        """
        user_ids = user_api.find_user_ids(
            created_api_user.username
        )

        assert len(user_ids) == 1

        user_id = user_ids[0]
        new_nickname = (
            f"修改后_{created_api_user.username[-6:]}"
        )
        new_phone = "13812345678"

        result = user_api.update_user(
            {
                "userId": user_id,
                "userName": created_api_user.username,
                "nickName": new_nickname,
                "phonenumber": new_phone,
                "deptId": DEFAULT_DEPT_ID,
            }
        )

        assert result["code"] == 200

        detail = user_api.get_user_detail(
            user_id
        )

        assert detail["data"]["nickName"] == (
            new_nickname
        )
        assert detail["data"]["phonenumber"] == (
            new_phone
        )

    @allure.story("删除用户")
    def test_delete_user(
        self,
        user_api,
        created_api_user,
    ) -> None:
        """
        删除用户后，列表中不应再存在该用户。
        """
        user_ids = user_api.find_user_ids(
            created_api_user.username
        )

        assert len(user_ids) == 1

        user_api.delete_user(user_ids[0])

        assert user_api.find_user_ids(
            created_api_user.username
        ) == []

    @allure.story("删除不存在用户")
    def test_delete_nonexistent_user(
        self,
        user_api,
    ) -> None:
        """
        删除不存在的用户 ID，
        后端应返回业务错误。
        """
        with pytest.raises(
            RuoYiApiError,
            match="request failed",
        ):
            user_api.delete_user(999999)