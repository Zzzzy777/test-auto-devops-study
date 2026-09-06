import pytest

from pages.login_page import LoginPage
from pages.user_page import UserPage


@pytest.fixture
def user_page(page: "Page"):
    """Log in and open the user-management page for UI user tests."""
    LoginPage(page).login()
    users = UserPage(page)
    users.open()
    return users