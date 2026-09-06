"""
跨接口业务链路测试。

这个文件用于体现：

新增角色
    ↓
查询角色
    ↓
查询详情
    ↓
删除角色
    ↓
删除后校验
"""

import allure
import pytest

from common.test_data import build_role_payload, build_unique_role


@pytest.mark.api
@allure.feature("业务链路测试")
class TestBusinessApi:
    """角色业务链路测试类。"""

    @allure.story("角色新增查询删除完整链路")
    def test_role_create_query_delete_flow(
        self,
        role_api,
    ) -> None:
        """
        验证一个完整的角色业务流程。
        """
        role = build_unique_role()

        try:
            # 第一步：新增角色
            add_result = role_api.add_role(
                build_role_payload(role)
            )

            assert add_result["code"] == 200

            # 第二步：根据唯一 roleKey 查询
            role_ids = role_api.find_role_ids(
                role_key=role.role_key
            )

            assert len(role_ids) == 1

            role_id = role_ids[0]

            # 第三步：查询角色详情
            detail_result = (
                role_api.get_role_detail(role_id)
            )

            assert detail_result["code"] == 200

            # 第四步：验证角色详情中的 roleKey
            detail = detail_result.get("data") or {}

            if isinstance(detail, dict):
                assert detail.get("roleKey") == (
                    role.role_key
                )

        finally:
            # 无论前面哪一步失败，都清理角色
            role_api.cleanup_role_by_key(
                role.role_key
            )

        # 第五步：删除后再次查询
        assert role_api.find_role_ids(
            role_key=role.role_key
        ) == []