"""?????????????"""

from __future__ import annotations

import allure
import pytest

from common.config import DEFAULT_DEPT_ID
from common.test_data import build_unique_user, build_user_payload


@pytest.mark.api
@allure.feature("??????")
class TestBusinessUserFlowApi:
    """????????????????????????"""

    @allure.story("????-??-??-??????")
    def test_user_create_query_update_delete_flow(self, user_api) -> None:
        user = build_unique_user("api_test_")
        user_id = None
        try:
            # 1. ????? Token ???????
            assert user_api.add_user(build_user_payload(user))["code"] == 200

            # 2. ??????????
            ids = user_api.find_user_ids(user.username)
            assert len(ids) == 1
            user_id = ids[0]

            # 3. ?????????
            new_nickname = f"????_{user.username[-6:]}"
            new_phone = "13812345678"
            assert user_api.update_user({
                "userId": user_id,
                "userName": user.username,
                "nickName": new_nickname,
                "phonenumber": new_phone,
                "deptId": DEFAULT_DEPT_ID,
            })["code"] == 200

            # 4. ????????????
            detail = user_api.get_user_detail(user_id)["data"]
            assert detail["nickName"] == new_nickname
            assert detail["phonenumber"] == new_phone

            # 5. ?????????????
            assert user_api.delete_user(user_id)["code"] == 200
            assert user_api.find_user_ids(user.username) == []
        finally:
            # ???????????????
            user_api.cleanup_user_by_username(user.username)
