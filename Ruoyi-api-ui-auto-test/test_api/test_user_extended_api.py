"""???????????"""

from __future__ import annotations

import allure
import pytest

from common.config import DEFAULT_DEPT_ID
from common.http_client import RuoYiApiError
from common.test_data import build_unique_user, build_user_payload


@pytest.mark.api
@allure.feature("??????")
class TestUserExtendedApi:
    """???????????????????"""

    @allure.story("????????")
    def test_query_user_by_phone(self, user_api) -> None:
        user = build_unique_user("api_test_")
        try:
            user_api.add_user(build_user_payload(user))
            result = user_api.get_user_list({
                "phonenumber": user.phone,
                "pageNum": 1,
                "pageSize": 10,
            })
            assert result["code"] == 200
            rows = result.get("rows") or []
            assert any(row.get("userName") == user.username for row in rows)
        finally:
            user_api.cleanup_user_by_username(user.username)

    @allure.story("??????")
    def test_change_user_status(self, user_api) -> None:
        user = build_unique_user("api_test_")
        try:
            user_api.add_user(build_user_payload(user))
            user_id = user_api.find_user_ids(user.username)[0]
            assert user_api.change_status(user_id, "1")["code"] == 200
            disabled = user_api.get_user_detail(user_id)
            assert disabled["data"]["status"] == "1"
            # ????????????????????
            assert user_api.change_status(user_id, "0")["code"] == 200
            enabled = user_api.get_user_detail(user_id)
            assert enabled["data"]["status"] == "0"
        finally:
            user_api.cleanup_user_by_username(user.username)

    @allure.story("?????????")
    def test_add_user_without_username(self, user_api) -> None:
        user = build_unique_user("api_test_")
        payload = build_user_payload(user)
        payload.pop("userName")
        with pytest.raises(RuoYiApiError, match="request failed"):
            user_api.add_user(payload)
