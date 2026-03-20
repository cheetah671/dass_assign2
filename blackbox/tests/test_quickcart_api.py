"""Black-box API tests for QuickCart using only documented behavior."""

import uuid

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


# -----------------------------
# Additional expansion: TC-101+
# -----------------------------


def test_profile_update_missing_body_returns_400(api_session, base_url, user_headers):
    resp = request_api(api_session, base_url, "PUT", "/profile", headers=user_headers, json={})
    assert resp.status_code == 400


@pytest.mark.parametrize(
    "payload",
    [
        {"name": 12345, "phone": "9999999999"},
        {"name": "Valid Name", "phone": 9999999999},
    ],
)
def test_profile_update_wrong_types_return_400(api_session, base_url, user_headers, payload):
    resp = request_api(api_session, base_url, "PUT", "/profile", headers=user_headers, json=payload)
    assert resp.status_code == 400


def test_profile_update_valid_min_boundary_returns_200(api_session, base_url, user_headers):
    payload = {"name": "AB", "phone": "9876543210"}
    resp = request_api(api_session, base_url, "PUT", "/profile", headers=user_headers, json=payload)
    assert resp.status_code == 200
    assert isinstance(resp.json(), (dict, list))


def test_wallet_add_valid_min_boundary_returns_200(api_session, base_url, user_headers):
    resp = request_api(api_session, base_url, "POST", "/wallet/add", headers=user_headers, json={"amount": 1})
    assert resp.status_code == 200
    assert isinstance(resp.json(), (dict, list))


@pytest.mark.parametrize(
    "payload",
    [
        {"label": "HOME", "street": "12345 Main Street", "city": "Hyderabad", "pincode": "ABCDE1", "is_default": False},
        {"label": "HOME", "street": "12345 Main Street", "city": "Hyderabad", "pincode": "500001", "is_default": 1},
    ],
)
def test_create_address_additional_invalid_types_and_values(api_session, base_url, user_headers, payload):
    resp = request_api(api_session, base_url, "POST", "/addresses", headers=user_headers, json=payload)
    assert resp.status_code == 400


def test_cart_update_missing_quantity_returns_400(api_session, base_url, user_headers, clear_cart):
    payload = {"product_id": 1}
    resp = request_api(api_session, base_url, "POST", "/cart/update", headers=user_headers, json=payload)
    assert resp.status_code == 400


def test_cart_remove_missing_product_id_returns_400(api_session, base_url, user_headers, clear_cart):
    resp = request_api(api_session, base_url, "POST", "/cart/remove", headers=user_headers, json={})
    assert resp.status_code == 400


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"payment_method": 1},
    ],
)
def test_checkout_missing_or_wrong_payment_method_returns_400(api_session, base_url, user_headers, payload, clear_cart):
    resp = request_api(api_session, base_url, "POST", "/checkout", headers=user_headers, json=payload)
    assert resp.status_code == 400


@pytest.mark.parametrize(
    "endpoint, payload",
    [
        ("/wallet/add", {"amount": "100"}),
        ("/wallet/pay", {}),
        ("/wallet/pay", {"amount": "100"}),
    ],
)
def test_wallet_wrong_or_missing_amount_returns_400(api_session, base_url, user_headers, endpoint, payload):
    resp = request_api(api_session, base_url, "POST", endpoint, headers=user_headers, json=payload)
    assert resp.status_code == 400


def test_loyalty_redeem_wrong_type_returns_400(api_session, base_url, user_headers):
    resp = request_api(api_session, base_url, "POST", "/loyalty/redeem", headers=user_headers, json={"points": "10"})
    assert resp.status_code == 400


@pytest.mark.parametrize(
    "payload",
    [
        {"comment": "good"},
        {"rating": "5", "comment": "good"},
    ],
)
def test_review_missing_or_wrong_rating_returns_400(api_session, base_url, user_headers, product_id, payload):
    resp = request_api(api_session, base_url, "POST", f"/products/{product_id}/reviews", headers=user_headers, json=payload)
    assert resp.status_code == 400


def test_review_missing_comment_returns_400(api_session, base_url, user_headers, product_id):
    resp = request_api(api_session, base_url, "POST", f"/products/{product_id}/reviews", headers=user_headers, json={"rating": 5})
    assert resp.status_code == 400


@pytest.mark.parametrize(
    "payload",
    [
        {"message": "Need help with order"},
        {"subject": "Need help"},
    ],
)
def test_support_ticket_missing_fields_returns_400(api_session, base_url, user_headers, payload):
    resp = request_api(api_session, base_url, "POST", "/support/ticket", headers=user_headers, json=payload)
    assert resp.status_code == 400


# -----------------------------
# Further expansion: TC-121+
# -----------------------------


def _create_address_and_get_id(api_session, base_url, user_headers):
    """Create an address and resolve its ID using response or list diff."""
    before_resp = request_api(api_session, base_url, "GET", "/addresses", headers=user_headers)
    assert before_resp.status_code == 200
    before = unwrap_list(before_resp.json())
    before_ids = {
        pick_id(a)
        for a in before
        if isinstance(a, dict) and pick_id(a) is not None
    }

    payload = {
        "label": "OTHER",
        "street": "221B Baker Street",
        "city": "Hyderabad",
        "pincode": "500001",
        "is_default": False,
    }
    create_resp = request_api(api_session, base_url, "POST", "/addresses", headers=user_headers, json=payload)
    assert create_resp.status_code in (200, 201)

    created = unwrap_dict(create_resp.json())
    aid = pick_id(created)
    if aid is not None:
        return aid

    after_resp = request_api(api_session, base_url, "GET", "/addresses", headers=user_headers)
    assert after_resp.status_code == 200
    after = unwrap_list(after_resp.json())

    for addr in after:
        if not isinstance(addr, dict):
            continue
        candidate_id = pick_id(addr)
        if candidate_id in before_ids:
            continue
        if addr.get("street") == payload["street"] and addr.get("city") == payload["city"]:
            return candidate_id

    pytest.skip("Could not resolve newly created address id")


def _create_ticket_and_get_id(api_session, base_url, user_headers):
    """Create a support ticket and resolve its ticket ID robustly."""
    subject = f"Ticket-{uuid.uuid4().hex[:10]}"
    payload = {"subject": subject, "message": "Need help with checkout issue"}
    create_resp = request_api(api_session, base_url, "POST", "/support/ticket", headers=user_headers, json=payload)
    assert create_resp.status_code in (200, 201)

    created = unwrap_dict(create_resp.json())
    tid = pick_id(created)
    if tid is not None:
        return tid

    list_resp = request_api(api_session, base_url, "GET", "/support/tickets", headers=user_headers)
    assert list_resp.status_code == 200
    tickets = unwrap_list(list_resp.json())
    for t in reversed(tickets):
        if isinstance(t, dict) and t.get("subject") == subject:
            tid = pick_id(t)
            if tid is not None:
                return tid

    pytest.skip("Could not resolve newly created ticket id")


def test_profile_update_missing_name_returns_400(api_session, base_url, user_headers):
    payload = {"phone": "9999999999"}
    resp = request_api(api_session, base_url, "PUT", "/profile", headers=user_headers, json=payload)
    assert resp.status_code == 400


def test_profile_update_missing_phone_returns_400(api_session, base_url, user_headers):
    payload = {"name": "Valid Name"}
    resp = request_api(api_session, base_url, "PUT", "/profile", headers=user_headers, json=payload)
    assert resp.status_code == 400


def test_update_nonexistent_address_returns_404(api_session, base_url, user_headers):
    payload = {"street": "Updated Street Name", "is_default": False}
    resp = request_api(api_session, base_url, "PUT", "/addresses/99999999", headers=user_headers, json=payload)
    assert resp.status_code == 404


def test_update_address_valid_street_and_default(api_session, base_url, user_headers):
    aid = _create_address_and_get_id(api_session, base_url, user_headers)
    payload = {"street": "New Street 45", "is_default": True}

    update_resp = request_api(api_session, base_url, "PUT", f"/addresses/{aid}", headers=user_headers, json=payload)
    assert update_resp.status_code == 200
    assert isinstance(update_resp.json(), (dict, list))


@pytest.mark.parametrize(
    "payload",
    [
        {"label": "OFFICE", "street": "Updated Street", "is_default": False},
        {"city": "Mumbai", "street": "Updated Street", "is_default": False},
        {"pincode": "400001", "street": "Updated Street", "is_default": False},
    ],
)
def test_update_address_restricted_fields_rejected(api_session, base_url, user_headers, payload):
    aid = _create_address_and_get_id(api_session, base_url, user_headers)
    resp = request_api(api_session, base_url, "PUT", f"/addresses/{aid}", headers=user_headers, json=payload)
    assert resp.status_code == 400


def test_update_address_invalid_street_too_short(api_session, base_url, user_headers):
    aid = _create_address_and_get_id(api_session, base_url, user_headers)
    payload = {"street": "1234", "is_default": False}
    resp = request_api(api_session, base_url, "PUT", f"/addresses/{aid}", headers=user_headers, json=payload)
    assert resp.status_code == 400


def test_cart_totals_match_item_subtotals(api_session, base_url, user_headers, product_id, clear_cart):
    add_resp = request_api(
        api_session,
        base_url,
        "POST",
        "/cart/add",
        headers=user_headers,
        json={"product_id": product_id, "quantity": 2},
    )
    assert add_resp.status_code in (200, 201)

    cart_resp = request_api(api_session, base_url, "GET", "/cart", headers=user_headers)
    assert cart_resp.status_code == 200
    body = cart_resp.json()
    items = unwrap_list(body)

    if not items and isinstance(body, dict):
        items = body.get("items", []) if isinstance(body.get("items"), list) else []

    computed_total = 0
    for item in items:
        if not isinstance(item, dict):
            continue
        quantity = item.get("quantity")
        price = item.get("price") or item.get("unit_price")
        subtotal = item.get("subtotal")
        if isinstance(quantity, (int, float)) and isinstance(price, (int, float)) and isinstance(subtotal, (int, float)):
            assert subtotal == quantity * price
            computed_total += subtotal

    if isinstance(body, dict) and isinstance(body.get("total"), (int, float)) and computed_total:
        assert body["total"] == computed_total


def test_cart_update_nonexistent_product_returns_404(api_session, base_url, user_headers, clear_cart):
    payload = {"product_id": 99999999, "quantity": 2}
    resp = request_api(api_session, base_url, "POST", "/cart/update", headers=user_headers, json=payload)
    assert resp.status_code == 404


def test_wallet_add_upper_boundary_valid(api_session, base_url, user_headers):
    resp = request_api(api_session, base_url, "POST", "/wallet/add", headers=user_headers, json={"amount": 100000})
    assert resp.status_code == 200
    assert isinstance(resp.json(), (dict, list))


def test_wallet_pay_zero_amount_returns_400(api_session, base_url, user_headers):
    resp = request_api(api_session, base_url, "POST", "/wallet/pay", headers=user_headers, json={"amount": 0})
    assert resp.status_code == 400


def test_loyalty_redeem_more_than_available_points_returns_400(api_session, base_url, user_headers):
    loyalty_resp = request_api(api_session, base_url, "GET", "/loyalty", headers=user_headers)
    assert loyalty_resp.status_code == 200
    loyalty = unwrap_dict(loyalty_resp.json())

    points = loyalty.get("points", 0)
    if not isinstance(points, int):
        points = 0

    redeem_resp = request_api(
        api_session,
        base_url,
        "POST",
        "/loyalty/redeem",
        headers=user_headers,
        json={"points": points + 1},
    )
    assert redeem_resp.status_code == 400


def test_get_nonexistent_order_returns_404(api_session, base_url, user_headers):
    resp = request_api(api_session, base_url, "GET", "/orders/99999999", headers=user_headers)
    assert resp.status_code == 404


def test_get_nonexistent_order_invoice_returns_404(api_session, base_url, user_headers):
    resp = request_api(api_session, base_url, "GET", "/orders/99999999/invoice", headers=user_headers)
    assert resp.status_code == 404


def test_coupon_apply_empty_code_returns_400(api_session, base_url, user_headers, clear_cart):
    resp = request_api(api_session, base_url, "POST", "/coupon/apply", headers=user_headers, json={"code": ""})
    assert resp.status_code == 400


def test_get_product_reviews_endpoint_returns_200_and_json(api_session, base_url, user_headers, product_id):
    resp = request_api(api_session, base_url, "GET", f"/products/{product_id}/reviews", headers=user_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), (dict, list))


def test_support_ticket_create_valid_returns_success(api_session, base_url, user_headers):
    payload = {
        "subject": f"Need help {uuid.uuid4().hex[:6]}",
        "message": "Order stuck in processing",
    }
    resp = request_api(api_session, base_url, "POST", "/support/ticket", headers=user_headers, json=payload)
    assert resp.status_code in (200, 201)
    assert isinstance(resp.json(), (dict, list))


def test_support_ticket_update_nonexistent_returns_404(api_session, base_url, user_headers):
    payload = {"status": "IN_PROGRESS"}
    resp = request_api(api_session, base_url, "PUT", "/support/tickets/99999999", headers=user_headers, json=payload)
    assert resp.status_code == 404


def test_support_ticket_invalid_status_transition_open_to_closed_rejected(api_session, base_url, user_headers):
    tid = _create_ticket_and_get_id(api_session, base_url, user_headers)
    payload = {"status": "CLOSED"}
    resp = request_api(api_session, base_url, "PUT", f"/support/tickets/{tid}", headers=user_headers, json=payload)
    assert resp.status_code == 400


def test_support_ticket_valid_status_lifecycle(api_session, base_url, user_headers):
    tid = _create_ticket_and_get_id(api_session, base_url, user_headers)

    to_progress = request_api(
        api_session,
        base_url,
        "PUT",
        f"/support/tickets/{tid}",
        headers=user_headers,
        json={"status": "IN_PROGRESS"},
    )
    assert to_progress.status_code == 200

    to_closed = request_api(
        api_session,
        base_url,
        "PUT",
        f"/support/tickets/{tid}",
        headers=user_headers,
        json={"status": "CLOSED"},
    )
    assert to_closed.status_code == 200
