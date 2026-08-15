import os

import pytest
import requests

from common.logger import get_logger

logger = get_logger(__name__)

def pytest_addoption(parser):
    parser.addoption(
        "--base-url",
        action="store",
        default=os.getenv("API_BASE_URL", "https://httpbin.ceshiren.com"),
        help="Base URL for API testing.",
    )


@pytest.fixture(scope="session")
def base_url(pytestconfig):
    return pytestconfig.getoption("--base-url").rstrip("/")


@pytest.fixture(scope="session")
def api_session():
    session = requests.Session()
    session.headers.update({"User-Agent": "pytest-api-demo/1.0"})
    return session


@pytest.fixture(scope="session")
def api_token(api_session, base_url):
    """Simulate login once and reuse the returned token in auth cases."""
    login_data = {
        "username": "demo_user",
        "password": "demo_password",
        "token": "mock-token-888666",
    }
    logger.info("Start login request and prepare reusable token.")
    resp = api_session.post(f"{base_url}/post", json=login_data, timeout=5)
    assert resp.status_code == 200

    result = resp.json()
    token = result["json"]["token"]
    assert token
    logger.info("Token prepared successfully.")
    return token

