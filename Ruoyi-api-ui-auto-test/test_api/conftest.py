"""
API 测试专用 Fixture。

Fixture 的作用是向 API 测试用例注入不同领域的客户端。
"""

from __future__ import annotations

import pytest

from common.role_api import RuoYiRoleApi
from common.system_api import RuoYiSystemApi
from common.user_api import RuoYiUserApi


@pytest.fixture
def user_api() -> RuoYiUserApi:
    """
    提供用户模块 API 客户端。
    """
    return RuoYiUserApi()


@pytest.fixture
def role_api() -> RuoYiRoleApi:
    """
    提供角色模块 API 客户端。
    """
    return RuoYiRoleApi()


@pytest.fixture
def system_api() -> RuoYiSystemApi:
    """
    提供菜单、部门等系统查询 API 客户端。
    """
    return RuoYiSystemApi()