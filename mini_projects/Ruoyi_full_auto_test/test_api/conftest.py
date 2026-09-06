import pytest

from common.user_api import RuoYiUserApi


@pytest.fixture
def user_api():
    return RuoYiUserApi()