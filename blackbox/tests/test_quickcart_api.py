"""Black-box API tests for QuickCart using only documented behavior."""

import pytest

from conftest import pick_id, request_api, unwrap_dict, unwrap_list


# ----------------------
# Header / Auth behavior
# ----------------------

def test_missing_roll_number_header_returns_401(api_session, base_url, user_headers):
    headers = {"X-User-ID": user_headers["X-User-ID"]}
    resp = request_api(api_session, base_url, "GET", "/profile", headers=headers)
    assert resp.status_code == 401


def test_invalid_roll_number_header_returns_400(api_session, base_url, user_headers):
    headers = {"X-Roll-Number": "abc", "X-User-ID": user_headers["X-User-ID"]}
    resp = request_api(api_session, base_url, "GET", "/profile", headers=headers)
    assert resp.status_code == 400


def test_missing_user_header_on_user_endpoint_returns_400(api_session, base_url, admin_headers):
    resp = request_api(api_session, base_url, "GET", "/profile", headers=admin_headers)
    assert resp.status_code == 400


def test_invalid_user_header_returns_400(api_session, base_url, roll_number):
    headers = {"X-Roll-Number": roll_number, "X-User-ID": "invalid"}
    resp = request_api(api_session, base_url, "GET", "/profile", headers=headers)
    assert resp.status_code == 400


def test_admin_endpoint_does_not_require_user_header(api_session, base_url, admin_headers):
    resp = request_api(api_session, base_url, "GET", "/admin/users", headers=admin_headers)
    assert resp.status_code == 200


# -------------
# Admin listings
# -------------

@pytest.mark.parametrize(
    "path",
    [
        "/admin/users",
        "/admin/carts",
        "/admin/orders",
        "/admin/products",
        "/admin/coupons",
        "/admin/tickets",
        "/admin/addresses",
    ],
)
def test_admin_list_endpoints_return_200(api_session, base_url, admin_headers, path):
    resp = request_api(api_session, base_url, "GET", path, headers=admin_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), (dict, list))


def test_admin_get_single_user_returns_200(api_session, base_url, admin_headers, user_id):
    resp = request_api(api_session, base_url, "GET", f"/admin/users/{user_id}", headers=admin_headers)
    assert resp.status_code == 200


# -------
# Profile
# -------


def test_get_profile_returns_200_and_json(api_session, base_url, user_headers):
    resp = request_api(api_session, base_url, "GET", "/profile", headers=user_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), (dict, list))


@pytest.mark.parametrize("name", ["A", "X" * 51])
def test_update_profile_name_boundary_invalid(api_session, base_url, user_headers, name):
    payload = {"name": name, "phone": "9999999999"}
    resp = request_api(api_session, base_url, "PUT", "/profile", headers=user_headers, json=payload)
    assert resp.status_code == 400


@pytest.mark.parametrize("phone", ["123456789", "12345678901", "abcde12345"])
def test_update_profile_phone_invalid(api_session, base_url, user_headers, phone):
    payload = {"name": "Valid Name", "phone": phone}
    resp = request_api(api_session, base_url, "PUT", "/profile", headers=user_headers, json=payload)
    assert resp.status_code == 400


# ---------
# Addresses
# ---------


def test_get_addresses_returns_200(api_session, base_url, user_headers):
    resp = request_api(api_session, base_url, "GET", "/addresses", headers=user_headers)
    assert resp.status_code == 200


@pytest.mark.parametrize(
    "payload",
    [
        {"label": "INVALID", "street": "12345 Main Street", "city": "Hyderabad", "pincode": "500001", "is_default": False},
        {"label": "HOME", "street": "123", "city": "Hyderabad", "pincode": "500001", "is_default": False},
        {"label": "HOME", "street": "12345 Main Street", "city": "H", "pincode": "500001", "is_default": False},
        {"label": "HOME", "street": "12345 Main Street", "city": "Hyderabad", "pincode": "5000", "is_default": False},
    ],
)
def test_create_address_invalid_payload_returns_400(api_session, base_url, user_headers, payload):
    resp = request_api(api_session, base_url, "POST", "/addresses", headers=user_headers, json=payload)
    assert resp.status_code == 400


def test_address_create_and_delete_flow(api_session, base_url, user_headers):
    payload = {
        "label": "HOME",
        "street": "12345 Main Street, Block A",
        "city": "Hyderabad",
        "pincode": "500001",
        "is_default": False,
    }
    create_resp = request_api(api_session, base_url, "POST", "/addresses", headers=user_headers, json=payload)
    assert create_resp.status_code in (200, 201)
    created = unwrap_dict(create_resp.json())
    aid = pick_id(created)
    assert aid is not None

    delete_resp = request_api(api_session, base_url, "DELETE", f"/addresses/{aid}", headers=user_headers)
    assert delete_resp.status_code == 200


def test_delete_nonexistent_address_returns_404(api_session, base_url, user_headers):
    resp = request_api(api_session, base_url, "DELETE", "/addresses/99999999", headers=user_headers)
    assert resp.status_code == 404


# --------
# Products
# --------


def test_products_list_returns_only_active_products(api_session, base_url, user_headers):
    resp = request_api(api_session, base_url, "GET", "/products", headers=user_headers)
    assert resp.status_code == 200
    products = unwrap_list(resp.json())
    for p in products:
        if isinstance(p, dict) and "active" in p:
            assert p["active"] is True


def test_get_product_by_valid_id(api_session, base_url, user_headers, product_id):
    resp = request_api(api_session, base_url, "GET", f"/products/{product_id}", headers=user_headers)
    assert resp.status_code == 200


def test_get_product_nonexistent_returns_404(api_session, base_url, user_headers):
    resp = request_api(api_session, base_url, "GET", "/products/99999999", headers=user_headers)
    assert resp.status_code == 404


@pytest.mark.parametrize("sort", ["asc", "desc"])
def test_products_sort_query_supported(api_session, base_url, user_headers, sort):
    resp = request_api(api_session, base_url, "GET", f"/products?sort={sort}", headers=user_headers)
    assert resp.status_code == 200


# ----
# Cart
# ----


@pytest.mark.parametrize("quantity", [0, -1])
def test_cart_add_invalid_quantity_returns_400(api_session, base_url, user_headers, product_id, clear_cart, quantity):
    payload = {"product_id": product_id, "quantity": quantity}
    resp = request_api(api_session, base_url, "POST", "/cart/add", headers=user_headers, json=payload)
    assert resp.status_code == 400


def test_cart_add_nonexistent_product_returns_404(api_session, base_url, user_headers, clear_cart):
    payload = {"product_id": 99999999, "quantity": 1}
    resp = request_api(api_session, base_url, "POST", "/cart/add", headers=user_headers, json=payload)
    assert resp.status_code == 404


def test_cart_update_invalid_quantity_returns_400(api_session, base_url, user_headers, product_id, clear_cart):
    add_resp = request_api(api_session, base_url, "POST", "/cart/add", headers=user_headers, json={"product_id": product_id, "quantity": 1})
    if add_resp.status_code not in (200, 201):
        pytest.skip("Unable to prepare cart for update quantity test")

    update_resp = request_api(api_session, base_url, "POST", "/cart/update", headers=user_headers, json={"product_id": product_id, "quantity": 0})
    assert update_resp.status_code == 400


def test_cart_remove_missing_item_returns_404(api_session, base_url, user_headers, clear_cart):
    resp = request_api(api_session, base_url, "POST", "/cart/remove", headers=user_headers, json={"product_id": 99999999})
    assert resp.status_code == 404


def test_cart_clear_endpoint_returns_success(api_session, base_url, user_headers, clear_cart):
    resp = request_api(api_session, base_url, "DELETE", "/cart/clear", headers=user_headers)
    assert resp.status_code == 200


# -------
# Coupons
# -------


def test_apply_coupon_missing_code_returns_400(api_session, base_url, user_headers, clear_cart):
    resp = request_api(api_session, base_url, "POST", "/coupon/apply", headers=user_headers, json={})
    assert resp.status_code == 400


def test_remove_coupon_without_coupon_returns_valid_status(api_session, base_url, user_headers, clear_cart):
    resp = request_api(api_session, base_url, "POST", "/coupon/remove", headers=user_headers, json={})
    assert resp.status_code in (200, 400)


# --------
# Checkout
# --------


def test_checkout_empty_cart_returns_400(api_session, base_url, user_headers, clear_cart):
    payload = {"payment_method": "COD"}
    resp = request_api(api_session, base_url, "POST", "/checkout", headers=user_headers, json=payload)
    assert resp.status_code == 400


def test_checkout_invalid_payment_method_returns_400(api_session, base_url, user_headers, clear_cart):
    payload = {"payment_method": "UPI"}
    resp = request_api(api_session, base_url, "POST", "/checkout", headers=user_headers, json=payload)
    assert resp.status_code == 400


# ------
# Wallet
# ------


@pytest.mark.parametrize("amount", [0, -1, 100001])
def test_wallet_add_invalid_amount_boundaries(api_session, base_url, user_headers, amount):
    resp = request_api(api_session, base_url, "POST", "/wallet/add", headers=user_headers, json={"amount": amount})
    assert resp.status_code == 400


def test_wallet_pay_insufficient_balance_returns_400(api_session, base_url, user_headers):
    resp = request_api(api_session, base_url, "POST", "/wallet/pay", headers=user_headers, json={"amount": 99999999})
    assert resp.status_code == 400


# -------
# Loyalty
# -------


def test_loyalty_get_returns_200(api_session, base_url, user_headers):
    resp = request_api(api_session, base_url, "GET", "/loyalty", headers=user_headers)
    assert resp.status_code == 200


@pytest.mark.parametrize("points", [0, -1])
def test_loyalty_redeem_invalid_points_returns_400(api_session, base_url, user_headers, points):
    resp = request_api(api_session, base_url, "POST", "/loyalty/redeem", headers=user_headers, json={"points": points})
    assert resp.status_code == 400


# ------
# Orders
# ------


def test_orders_list_returns_200(api_session, base_url, user_headers):
    resp = request_api(api_session, base_url, "GET", "/orders", headers=user_headers)
    assert resp.status_code == 200


def test_cancel_nonexistent_order_returns_404(api_session, base_url, user_headers):
    resp = request_api(api_session, base_url, "POST", "/orders/99999999/cancel", headers=user_headers)
    assert resp.status_code == 404


# -------
# Reviews
# -------


@pytest.mark.parametrize("rating", [0, 6])
def test_review_rating_outside_range_returns_400(api_session, base_url, user_headers, product_id, rating):
    payload = {"rating": rating, "comment": "boundary-check"}
    resp = request_api(api_session, base_url, "POST", f"/products/{product_id}/reviews", headers=user_headers, json=payload)
    assert resp.status_code == 400


@pytest.mark.parametrize("comment", ["", "x" * 201])
def test_review_comment_length_boundaries(api_session, base_url, user_headers, product_id, comment):
    payload = {"rating": 4, "comment": comment}
    resp = request_api(api_session, base_url, "POST", f"/products/{product_id}/reviews", headers=user_headers, json=payload)
    assert resp.status_code == 400


# -------------
# Support ticket
# -------------


@pytest.mark.parametrize("subject", ["1234", "x" * 101])
def test_support_ticket_subject_boundary_invalid(api_session, base_url, user_headers, subject):
    payload = {"subject": subject, "message": "valid message"}
    resp = request_api(api_session, base_url, "POST", "/support/ticket", headers=user_headers, json=payload)
    assert resp.status_code == 400


@pytest.mark.parametrize("message", ["", "x" * 501])
def test_support_ticket_message_boundary_invalid(api_session, base_url, user_headers, message):
    payload = {"subject": "Valid Subject", "message": message}
    resp = request_api(api_session, base_url, "POST", "/support/ticket", headers=user_headers, json=payload)
    assert resp.status_code == 400


def test_support_tickets_list_returns_200(api_session, base_url, user_headers):
    resp = request_api(api_session, base_url, "GET", "/support/tickets", headers=user_headers)
    assert resp.status_code == 200


# -----------------
# Extended coverage
# -----------------


@pytest.mark.parametrize(
    "headers, expected_statuses",
    [
        ({}, (400, 401)),
        ({"X-Roll-Number": "1.5", "X-User-ID": "1"}, (400,)),
        ({"X-Roll-Number": "1", "X-User-ID": "1.2"}, (400,)),
        ({"X-Roll-Number": "1", "X-User-ID": ""}, (400,)),
    ],
)
def test_profile_header_edge_cases(api_session, base_url, headers, expected_statuses):
    resp = request_api(api_session, base_url, "GET", "/profile", headers=headers)
    assert resp.status_code in expected_statuses


@pytest.mark.parametrize(
    "path",
    [
        "/admin/users",
        "/admin/carts",
        "/admin/orders",
        "/admin/products",
        "/admin/coupons",
        "/admin/tickets",
        "/admin/addresses",
    ],
)
def test_admin_list_endpoints_json_structure(api_session, base_url, admin_headers, path):
    resp = request_api(api_session, base_url, "GET", path, headers=admin_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, (list, dict))


def test_profile_response_structure_contains_profile_data(api_session, base_url, user_headers):
    resp = request_api(api_session, base_url, "GET", "/profile", headers=user_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, (dict, list))
    if isinstance(data, dict):
        assert len(data.keys()) > 0


@pytest.mark.parametrize(
    "payload",
    [
        {"name": "Valid Name", "phone": "9999999999"},
        {"name": "N" * 50, "phone": "8888888888"},
    ],
)
def test_profile_update_valid_inputs(api_session, base_url, user_headers, payload):
    resp = request_api(api_session, base_url, "PUT", "/profile", headers=user_headers, json=payload)
    assert resp.status_code == 200
    assert isinstance(resp.json(), (dict, list))


@pytest.mark.parametrize(
    "payload",
    [
        {"label": "HOME", "street": "12345 Main Street", "city": "Hyderabad", "pincode": "500001", "is_default": False},
        {"label": "OTHER", "street": "X" * 10, "city": "Mumbai", "pincode": "400001", "is_default": True},
    ],
)
def test_create_address_valid_boundaries(api_session, base_url, user_headers, payload):
    resp = request_api(api_session, base_url, "POST", "/addresses", headers=user_headers, json=payload)
    assert resp.status_code in (200, 201)
    assert isinstance(resp.json(), (dict, list))


@pytest.mark.parametrize(
    "payload",
    [
        {"street": "12345 Main Street", "city": "Hyderabad", "pincode": "500001", "is_default": False},
        {"label": "HOME", "city": "Hyderabad", "pincode": "500001", "is_default": False},
        {"label": "HOME", "street": "12345 Main Street", "pincode": "500001", "is_default": False},
        {"label": "HOME", "street": "12345 Main Street", "city": "Hyderabad", "is_default": False},
        {"label": "HOME", "street": "12345 Main Street", "city": "Hyderabad", "pincode": "500001"},
    ],
)
def test_create_address_missing_fields_returns_400(api_session, base_url, user_headers, payload):
    resp = request_api(api_session, base_url, "POST", "/addresses", headers=user_headers, json=payload)
    assert resp.status_code == 400


@pytest.mark.parametrize(
    "payload",
    [
        {"label": 10, "street": "12345 Main Street", "city": "Hyderabad", "pincode": "500001", "is_default": False},
        {"label": "HOME", "street": 10, "city": "Hyderabad", "pincode": "500001", "is_default": False},
        {"label": "HOME", "street": "12345 Main Street", "city": 10, "pincode": "500001", "is_default": False},
        {"label": "HOME", "street": "12345 Main Street", "city": "Hyderabad", "pincode": 500001, "is_default": False},
        {"label": "HOME", "street": "12345 Main Street", "city": "Hyderabad", "pincode": "500001", "is_default": "false"},
    ],
)
def test_create_address_wrong_types_returns_400(api_session, base_url, user_headers, payload):
    resp = request_api(api_session, base_url, "POST", "/addresses", headers=user_headers, json=payload)
    assert resp.status_code == 400


@pytest.mark.parametrize(
    "query",
    [
        "?search=",
        "?category=",
        "?sort=asc&search=phone",
        "?sort=desc&category=electronics",
    ],
)
def test_products_query_boundaries_return_json(api_session, base_url, user_headers, query):
    resp = request_api(api_session, base_url, "GET", f"/products{query}", headers=user_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), (dict, list))


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"product_id": "x", "quantity": 1},
        {"product_id": 1, "quantity": "2"},
        {"product_id": 1},
        {"quantity": 1},
    ],
)
def test_cart_add_missing_or_wrong_types_return_400(api_session, base_url, user_headers, clear_cart, payload):
    resp = request_api(api_session, base_url, "POST", "/cart/add", headers=user_headers, json=payload)
    assert resp.status_code == 400


@pytest.mark.parametrize(
    "payload",
    [
        {"product_id": "x", "quantity": 1},
        {"product_id": 1},
    ],
)
def test_cart_update_missing_or_wrong_types_return_400(api_session, base_url, user_headers, payload):
    resp = request_api(api_session, base_url, "POST", "/cart/update", headers=user_headers, json=payload)
    assert resp.status_code == 400


@pytest.mark.parametrize("payload", [{"code": 12345}, {"coupon": "SAVE10"}])
def test_coupon_apply_missing_or_wrong_type_returns_400(api_session, base_url, user_headers, clear_cart, payload):
    resp = request_api(api_session, base_url, "POST", "/coupon/apply", headers=user_headers, json=payload)
    assert resp.status_code == 400


@pytest.mark.parametrize(
    "payload",
    [
        {"subject": 12345, "message": "Need help with order"},
        {"subject": "Need help", "message": 12345},
    ],
)
def test_support_ticket_wrong_types_return_400(api_session, base_url, user_headers, payload):
    resp = request_api(api_session, base_url, "POST", "/support/ticket", headers=user_headers, json=payload)
    assert resp.status_code == 400
