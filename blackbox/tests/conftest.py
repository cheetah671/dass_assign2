"""Shared fixtures and helpers for QuickCart black-box API tests."""

import os
from typing import Any

import pytest
import requests


API_PREFIX = "/api/v1"


def _unwrap(payload: Any) -> Any:
    """Best-effort unwrap for common API response envelope shapes."""
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in (
            "data",
            "items",
            "results",
            "users",
            "products",
            "orders",
            "addresses",
            "tickets",
            "coupons",
            "cart",
        ):
            if key in payload:
                return payload[key]
    return payload


def unwrap_list(payload: Any) -> list:
    """Return a list from payload when possible, else empty list."""
    value = _unwrap(payload)
    return value if isinstance(value, list) else []


def unwrap_dict(payload: Any) -> dict:
    """Return a dict from payload when possible, else empty dict."""
    value = _unwrap(payload)
    return value if isinstance(value, dict) else {}


def pick_id(record: dict) -> Any:
    """Extract common identifier keys from a response object."""
    for key in ("id", "user_id", "product_id", "address_id", "order_id", "ticket_id"):
        if key in record:
            return record[key]
    return None


def request_api(session: requests.Session, base_url: str, method: str, path: str, **kwargs):
    """Call QuickCart API under /api/v1 with given method and path."""
    full_url = f"{base_url.rstrip('/')}{API_PREFIX}{path}"
    return session.request(method=method, url=full_url, timeout=15, **kwargs)


@pytest.fixture(scope="session")
def base_url() -> str:
    """Base URL for API server (override using QC_BASE_URL)."""
    return os.getenv("QC_BASE_URL", "http://localhost:8080")


@pytest.fixture(scope="session")
def roll_number() -> str:
    """Valid integer roll number used in mandatory API header."""
    return os.getenv("QC_ROLL_NUMBER", "1")


@pytest.fixture(scope="session")
def api_session() -> requests.Session:
    """Reusable HTTP session for API tests."""
    with requests.Session() as session:
        yield session


@pytest.fixture(scope="session")
def admin_headers(roll_number: str) -> dict:
    """Headers for admin endpoints requiring only roll number."""
    return {"X-Roll-Number": roll_number}


@pytest.fixture(scope="session")
def user_id(api_session: requests.Session, base_url: str, admin_headers: dict) -> int:
    """Resolve an existing user ID from admin listing for user-scoped endpoint tests."""
    resp = request_api(api_session, base_url, "GET", "/admin/users", headers=admin_headers)
    if resp.status_code != 200:
        pytest.skip("QuickCart API is not reachable or admin/users is unavailable")

    payload = resp.json()
    users = unwrap_list(payload)
    if not users:
        pytest.skip("No users available in QuickCart seed data")

    uid = pick_id(users[0])
    if uid is None:
        pytest.skip("Could not resolve user id from admin/users response")
    return int(uid)


@pytest.fixture(scope="session")
def user_headers(roll_number: str, user_id: int) -> dict:
    """Headers for user-scoped endpoints."""
    return {"X-Roll-Number": roll_number, "X-User-ID": str(user_id)}


@pytest.fixture(scope="session")
def product_id(api_session: requests.Session, base_url: str, admin_headers: dict) -> int:
    """Resolve one product id from admin data for product/cart/review tests."""
    resp = request_api(api_session, base_url, "GET", "/admin/products", headers=admin_headers)
    if resp.status_code != 200:
        pytest.skip("admin/products unavailable")

    products = unwrap_list(resp.json())
    if not products:
        pytest.skip("No products available")

    pid = pick_id(products[0])
    if pid is None:
        pytest.skip("Could not resolve product id")
    return int(pid)


@pytest.fixture
def clear_cart(api_session: requests.Session, base_url: str, user_headers: dict):
    """Ensure cart starts empty for cart-sensitive tests."""
    request_api(api_session, base_url, "DELETE", "/cart/clear", headers=user_headers)
    yield
    request_api(api_session, base_url, "DELETE", "/cart/clear", headers=user_headers)
