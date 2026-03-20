# Black-Box Testing Report: QuickCart REST API

## Scope
- Technique: Black-box testing only.
- Test file: `blackbox/tests/test_quickcart_api.py`
- Environment:
  - Base URL: `http://localhost:8080`
  - Headers: `X-Roll-Number`, `X-User-ID` (for user endpoints)

## Execution
- Command used:

```bash
QC_BASE_URL=http://localhost:8080 QC_ROLL_NUMBER=1 python -m pytest blackbox/tests/test_quickcart_api.py -vv
```

- Latest verification command:

```bash
QC_BASE_URL=http://localhost:8080 QC_ROLL_NUMBER=1 /home/arnav-agnihotri/miniconda3/envs/autograder/bin/python -m pytest blackbox/tests/test_quickcart_api.py -q
```

- Total test cases: `141`
- Passed: `120`
- Failed: `21`
- Skipped: `0`

## Category-Wise Distribution (Total = 141)

| Category | Test Count |
|---|---:|
| Header Validation | 8 |
| Admin Endpoints | 16 |
| Profile | 15 |
| Addresses | 27 |
| Products | 9 |
| Cart | 17 |
| Coupons | 5 |
| Checkout | 4 |
| Wallet | 10 |
| Loyalty | 5 |
| Orders | 4 |
| Reviews | 8 |
| Support Tickets | 13 |
| **Total** | **141** |

## Complete Test Case Status (All 141, Category-Wise)

### Header Validation (8)
| TC | Pytest Test Case | Status |
|---|---|---|
| TC-001 | `test_missing_roll_number_header_returns_401` | PASS |
| TC-002 | `test_invalid_roll_number_header_returns_400` | PASS |
| TC-003 | `test_missing_user_header_on_user_endpoint_returns_400` | PASS |
| TC-004 | `test_invalid_user_header_returns_400` | PASS |
| TC-060 | `test_profile_header_edge_cases[headers0-expected_statuses0]` | PASS |
| TC-061 | `test_profile_header_edge_cases[headers1-expected_statuses1]` | PASS |
| TC-062 | `test_profile_header_edge_cases[headers2-expected_statuses2]` | PASS |
| TC-063 | `test_profile_header_edge_cases[headers3-expected_statuses3]` | PASS |

### Admin Endpoints (16)
| TC | Pytest Test Case | Status |
|---|---|---|
| TC-005 | `test_admin_endpoint_does_not_require_user_header` | PASS |
| TC-006 | `test_admin_list_endpoints_return_200[/admin/users]` | PASS |
| TC-007 | `test_admin_list_endpoints_return_200[/admin/carts]` | PASS |
| TC-008 | `test_admin_list_endpoints_return_200[/admin/orders]` | PASS |
| TC-009 | `test_admin_list_endpoints_return_200[/admin/products]` | PASS |
| TC-010 | `test_admin_list_endpoints_return_200[/admin/coupons]` | PASS |
| TC-011 | `test_admin_list_endpoints_return_200[/admin/tickets]` | PASS |
| TC-012 | `test_admin_list_endpoints_return_200[/admin/addresses]` | PASS |
| TC-013 | `test_admin_get_single_user_returns_200` | PASS |
| TC-064 | `test_admin_list_endpoints_json_structure[/admin/users]` | PASS |
| TC-065 | `test_admin_list_endpoints_json_structure[/admin/carts]` | PASS |
| TC-066 | `test_admin_list_endpoints_json_structure[/admin/orders]` | PASS |
| TC-067 | `test_admin_list_endpoints_json_structure[/admin/products]` | PASS |
| TC-068 | `test_admin_list_endpoints_json_structure[/admin/coupons]` | PASS |
| TC-069 | `test_admin_list_endpoints_json_structure[/admin/tickets]` | PASS |
| TC-070 | `test_admin_list_endpoints_json_structure[/admin/addresses]` | PASS |

### Profile (15)
| TC | Pytest Test Case | Status |
|---|---|---|
| TC-014 | `test_get_profile_returns_200_and_json` | PASS |
| TC-015 | `test_update_profile_name_boundary_invalid[A]` | PASS |
| TC-016 | `test_update_profile_name_boundary_invalid[XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX]` | PASS |
| TC-017 | `test_update_profile_phone_invalid[123456789]` | PASS |
| TC-018 | `test_update_profile_phone_invalid[12345678901]` | PASS |
| TC-019 | `test_update_profile_phone_invalid[abcde12345]` | FAIL |
| TC-071 | `test_profile_response_structure_contains_profile_data` | PASS |
| TC-072 | `test_profile_update_valid_inputs[payload0]` | PASS |
| TC-073 | `test_profile_update_valid_inputs[payload1]` | PASS |

Merged additional Profile cases:
- `test_profile_update_missing_body_returns_400`
- `test_profile_update_wrong_types_return_400[payload0]`
- `test_profile_update_wrong_types_return_400[payload1]`
- `test_profile_update_valid_min_boundary_returns_200`
- `test_profile_update_missing_name_returns_400`
- `test_profile_update_missing_phone_returns_400`

### Addresses (27)
| TC | Pytest Test Case | Status |
|---|---|---|
| TC-020 | `test_get_addresses_returns_200` | PASS |
| TC-021 | `test_create_address_invalid_payload_returns_400[payload0]` | PASS |
| TC-022 | `test_create_address_invalid_payload_returns_400[payload1]` | PASS |
| TC-023 | `test_create_address_invalid_payload_returns_400[payload2]` | PASS |
| TC-024 | `test_create_address_invalid_payload_returns_400[payload3]` | PASS |
| TC-025 | `test_address_create_and_delete_flow` | FAIL |
| TC-026 | `test_delete_nonexistent_address_returns_404` | PASS |
| TC-074 | `test_create_address_valid_boundaries[payload0]` | PASS |
| TC-075 | `test_create_address_valid_boundaries[payload1]` | PASS |
| TC-076 | `test_create_address_missing_fields_returns_400[payload0]` | PASS |
| TC-077 | `test_create_address_missing_fields_returns_400[payload1]` | PASS |
| TC-078 | `test_create_address_missing_fields_returns_400[payload2]` | PASS |
| TC-079 | `test_create_address_missing_fields_returns_400[payload3]` | PASS |
| TC-080 | `test_create_address_missing_fields_returns_400[payload4]` | FAIL |
| TC-081 | `test_create_address_wrong_types_returns_400[payload0]` | PASS |
| TC-082 | `test_create_address_wrong_types_returns_400[payload1]` | PASS |
| TC-083 | `test_create_address_wrong_types_returns_400[payload2]` | PASS |
| TC-084 | `test_create_address_wrong_types_returns_400[payload3]` | PASS |
| TC-085 | `test_create_address_wrong_types_returns_400[payload4]` | PASS |

Merged additional Address cases:
- `test_create_address_additional_invalid_types_and_values[payload0]` | FAIL
- `test_create_address_additional_invalid_types_and_values[payload1]`
- `test_update_nonexistent_address_returns_404`
- `test_update_address_valid_street_and_default`
- `test_update_address_restricted_fields_rejected[payload0]` | FAIL
- `test_update_address_restricted_fields_rejected[payload1]` | FAIL
- `test_update_address_restricted_fields_rejected[payload2]` | FAIL
- `test_update_address_invalid_street_too_short` | FAIL

### Products (9)
| TC | Pytest Test Case | Status |
|---|---|---|
| TC-027 | `test_products_list_returns_only_active_products` | PASS |
| TC-028 | `test_get_product_by_valid_id` | PASS |
| TC-029 | `test_get_product_nonexistent_returns_404` | PASS |
| TC-030 | `test_products_sort_query_supported[asc]` | PASS |
| TC-031 | `test_products_sort_query_supported[desc]` | PASS |
| TC-086 | `test_products_query_boundaries_return_json[?search=]` | PASS |
| TC-087 | `test_products_query_boundaries_return_json[?category=]` | PASS |
| TC-088 | `test_products_query_boundaries_return_json[?sort=asc&search=phone]` | PASS |
| TC-089 | `test_products_query_boundaries_return_json[?sort=desc&category=electronics]` | PASS |

Merged additional Product/Review-list case:
- `test_get_product_reviews_endpoint_returns_200_and_json`

### Cart (17)
| TC | Pytest Test Case | Status |
|---|---|---|
| TC-032 | `test_cart_add_invalid_quantity_returns_400[0]` | FAIL |
| TC-033 | `test_cart_add_invalid_quantity_returns_400[-1]` | FAIL |
| TC-034 | `test_cart_add_nonexistent_product_returns_404` | PASS |
| TC-035 | `test_cart_update_invalid_quantity_returns_400` | PASS |
| TC-036 | `test_cart_remove_missing_item_returns_404` | PASS |
| TC-037 | `test_cart_clear_endpoint_returns_success` | PASS |
| TC-090 | `test_cart_add_missing_or_wrong_types_return_400[payload0]` | FAIL |
| TC-091 | `test_cart_add_missing_or_wrong_types_return_400[payload1]` | PASS |
| TC-092 | `test_cart_add_missing_or_wrong_types_return_400[payload2]` | PASS |
| TC-093 | `test_cart_add_missing_or_wrong_types_return_400[payload3]` | FAIL |
| TC-094 | `test_cart_add_missing_or_wrong_types_return_400[payload4]` | FAIL |
| TC-095 | `test_cart_update_missing_or_wrong_types_return_400[payload0]` | PASS |
| TC-096 | `test_cart_update_missing_or_wrong_types_return_400[payload1]` | PASS |

Merged additional Cart cases:
- `test_cart_update_missing_quantity_returns_400`
- `test_cart_remove_missing_product_id_returns_400` | FAIL
- `test_cart_totals_match_item_subtotals` | FAIL
- `test_cart_update_nonexistent_product_returns_404` | FAIL

### Coupons (5)
| TC | Pytest Test Case | Status |
|---|---|---|
| TC-038 | `test_apply_coupon_missing_code_returns_400` | PASS |
| TC-039 | `test_remove_coupon_without_coupon_returns_valid_status` | PASS |
| TC-097 | `test_coupon_apply_missing_or_wrong_type_returns_400[payload0]` | PASS |
| TC-098 | `test_coupon_apply_missing_or_wrong_type_returns_400[payload1]` | PASS |

Merged additional Coupon case:
- `test_coupon_apply_empty_code_returns_400`

### Checkout (4)
| TC | Pytest Test Case | Status |
|---|---|---|
| TC-040 | `test_checkout_empty_cart_returns_400` | FAIL |
| TC-041 | `test_checkout_invalid_payment_method_returns_400` | PASS |

Merged additional Checkout cases:
- `test_checkout_missing_or_wrong_payment_method_returns_400[payload0]`
- `test_checkout_missing_or_wrong_payment_method_returns_400[payload1]`

### Wallet (10)
| TC | Pytest Test Case | Status |
|---|---|---|
| TC-042 | `test_wallet_add_invalid_amount_boundaries[0]` | PASS |
| TC-043 | `test_wallet_add_invalid_amount_boundaries[-1]` | PASS |
| TC-044 | `test_wallet_add_invalid_amount_boundaries[100001]` | PASS |
| TC-045 | `test_wallet_pay_insufficient_balance_returns_400` | PASS |

Merged additional Wallet cases:
- `test_wallet_add_valid_min_boundary_returns_200`
- `test_wallet_wrong_or_missing_amount_returns_400[/wallet/add-payload0]`
- `test_wallet_wrong_or_missing_amount_returns_400[/wallet/pay-payload1]`
- `test_wallet_wrong_or_missing_amount_returns_400[/wallet/pay-payload2]`
- `test_wallet_add_upper_boundary_valid`
- `test_wallet_pay_zero_amount_returns_400`

### Loyalty (5)
| TC | Pytest Test Case | Status |
|---|---|---|
| TC-046 | `test_loyalty_get_returns_200` | PASS |
| TC-047 | `test_loyalty_redeem_invalid_points_returns_400[0]` | PASS |
| TC-048 | `test_loyalty_redeem_invalid_points_returns_400[-1]` | PASS |

Merged additional Loyalty cases:
- `test_loyalty_redeem_wrong_type_returns_400`
- `test_loyalty_redeem_more_than_available_points_returns_400` | FAIL

### Orders (4)
| TC | Pytest Test Case | Status |
|---|---|---|
| TC-049 | `test_orders_list_returns_200` | PASS |
| TC-050 | `test_cancel_nonexistent_order_returns_404` | PASS |

Merged additional Order cases:
- `test_get_nonexistent_order_returns_404`
- `test_get_nonexistent_order_invoice_returns_404`

### Reviews (8)
| TC | Pytest Test Case | Status |
|---|---|---|
| TC-051 | `test_review_rating_outside_range_returns_400[0]` | FAIL |
| TC-052 | `test_review_rating_outside_range_returns_400[6]` | FAIL |
| TC-053 | `test_review_comment_length_boundaries[]` | PASS |
| TC-054 | `test_review_comment_length_boundaries[xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx]` | PASS |

Merged additional Review cases:
- `test_review_missing_or_wrong_rating_returns_400[payload0]` | FAIL
- `test_review_missing_or_wrong_rating_returns_400[payload1]`
- `test_review_missing_comment_returns_400`

### Support Tickets (13)
| TC | Pytest Test Case | Status |
|---|---|---|
| TC-055 | `test_support_ticket_subject_boundary_invalid[1234]` | PASS |
| TC-056 | `test_support_ticket_subject_boundary_invalid[xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx]` | PASS |
| TC-057 | `test_support_ticket_message_boundary_invalid[]` | PASS |
| TC-058 | `test_support_ticket_message_boundary_invalid[xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx]` | PASS |
| TC-059 | `test_support_tickets_list_returns_200` | PASS |
| TC-099 | `test_support_ticket_wrong_types_return_400[payload0]` | PASS |
| TC-100 | `test_support_ticket_wrong_types_return_400[payload1]` | PASS |

Merged additional Support Ticket cases:
- `test_support_ticket_missing_fields_returns_400[payload0]`
- `test_support_ticket_missing_fields_returns_400[payload1]`
- `test_support_ticket_create_valid_returns_success`
- `test_support_ticket_update_nonexistent_returns_404`
- `test_support_ticket_invalid_status_transition_open_to_closed_rejected`
- `test_support_ticket_valid_status_lifecycle`

## Bug Detection (Failed Test Cases)

### Bug ID: BB-01
- Endpoint tested: `/api/v1/profile`
- Request payload:
  - Method: `PUT`
  - URL: `http://localhost:8080/api/v1/profile`
  - Headers: `X-Roll-Number: 1`, `X-User-ID: 1`
  - Body:

```json
{
  "name": "Valid Name",
  "phone": "abcde12345"
}
```

- Expected result (API doc): `400` (phone must be exactly 10 digits).
- Actual result observed: `200 OK`.

### Bug ID: BB-02
- Endpoint tested: `/api/v1/addresses`
- Request payload:
  - Method: `POST`
  - URL: `http://localhost:8080/api/v1/addresses`
  - Headers: `X-Roll-Number: 1`, `X-User-ID: 1`
  - Body:

```json
{
  "label": "HOME",
  "street": "12345 Main Street, Block A",
  "city": "Hyderabad",
  "pincode": "500001",
  "is_default": false
}
```

- Expected result (API doc): `200/201` with created address object containing an identifier (`address_id`/`id`) for follow-up delete/update operations.
- Actual result observed: response succeeded but identifier was not discoverable (`aid is None`).

### Bug ID: BB-03
- Endpoint tested: `/api/v1/cart/add`
- Request payload:
  - Method: `POST`
  - URL: `http://localhost:8080/api/v1/cart/add`
  - Headers: `X-Roll-Number: 1`, `X-User-ID: 1`
  - Body:

```json
{
  "product_id": 1,
  "quantity": 0
}
```

- Expected result (API doc): `400` (quantity must be >= 1).
- Actual result observed: `200 OK`.

### Bug ID: BB-04
- Endpoint tested: `/api/v1/cart/add`
- Request payload:
  - Method: `POST`
  - URL: `http://localhost:8080/api/v1/cart/add`
  - Headers: `X-Roll-Number: 1`, `X-User-ID: 1`
  - Body:

```json
{
  "product_id": 1,
  "quantity": -1
}
```

- Expected result (API doc): `400` (negative quantity invalid).
- Actual result observed: `200 OK`.

### Bug ID: BB-05
- Endpoint tested: `/api/v1/checkout`
- Request payload:
  - Method: `POST`
  - URL: `http://localhost:8080/api/v1/checkout`
  - Headers: `X-Roll-Number: 1`, `X-User-ID: 1`
  - Body:

```json
{
  "payment_method": "COD"
}
```

- Expected result (API doc): `400` for empty cart checkout.
- Actual result observed: `200 OK`.

### Bug ID: BB-06
- Endpoint tested: `/api/v1/products/1/reviews`
- Request payload:
  - Method: `POST`
  - URL: `http://localhost:8080/api/v1/products/1/reviews`
  - Headers: `X-Roll-Number: 1`, `X-User-ID: 1`
  - Body:

```json
{
  "rating": 0,
  "comment": "boundary-check"
}
```

- Expected result (API doc): `400` (rating must be between 1 and 5).
- Actual result observed: `200 OK`.

### Bug ID: BB-07
- Endpoint tested: `/api/v1/products/1/reviews`
- Request payload:
  - Method: `POST`
  - URL: `http://localhost:8080/api/v1/products/1/reviews`
  - Headers: `X-Roll-Number: 1`, `X-User-ID: 1`
  - Body:

```json
{
  "rating": 6,
  "comment": "boundary-check"
}
```

- Expected result (API doc): `400` (rating must be between 1 and 5).
- Actual result observed: `200 OK`.

### Bug ID: BB-08
- Endpoint tested: `/api/v1/addresses`
- Request payload:
  - Method: `POST`
  - URL: `http://localhost:8080/api/v1/addresses`
  - Headers: `X-Roll-Number: 1`, `X-User-ID: 1`
  - Body:

```json
{
  "label": "HOME",
  "street": "12345 Main Street",
  "city": "Hyderabad",
  "pincode": "500001"
}
```

- Expected result (API doc): `400` because required field `is_default` is missing.
- Actual result observed: `200 OK`.

### Bug ID: BB-09
- Endpoint tested: `/api/v1/cart/add`
- Request payload:
  - Method: `POST`
  - URL: `http://localhost:8080/api/v1/cart/add`
  - Headers: `X-Roll-Number: 1`, `X-User-ID: 1`
  - Body:

```json
{}
```

- Expected result (API doc): `400` for missing required fields.
- Actual result observed: `404 Not Found`.

### Bug ID: BB-10
- Endpoint tested: `/api/v1/cart/add`
- Request payload:
  - Method: `POST`
  - URL: `http://localhost:8080/api/v1/cart/add`
  - Headers: `X-Roll-Number: 1`, `X-User-ID: 1`
  - Body:

```json
{
  "product_id": 1
}
```

- Expected result (API doc): `400` because `quantity` is missing.
- Actual result observed: `200 OK`.

### Bug ID: BB-11
- Endpoint tested: `/api/v1/cart/add`
- Request payload:
  - Method: `POST`
  - URL: `http://localhost:8080/api/v1/cart/add`
  - Headers: `X-Roll-Number: 1`, `X-User-ID: 1`
  - Body:

```json
{
  "quantity": 1
}
```

- Expected result (API doc): `400` because `product_id` is missing.
- Actual result observed: `404 Not Found`.

### Bug ID: BB-12
- Endpoint tested: `/api/v1/addresses`
- Request payload:
  - Method: `POST`
  - URL: `http://localhost:8080/api/v1/addresses`
  - Headers: `X-Roll-Number: 1`, `X-User-ID: 1`
  - Body: `{"label":"HOME","street":"12345 Main Street","city":"Hyderabad","pincode":"ABCDE1","is_default":false}`
- Expected result: `400` for invalid pincode format.
- Actual result observed: `200 OK`.

### Bug ID: BB-13
- Endpoint tested: `/api/v1/cart/remove`
- Request payload:
  - Method: `POST`
  - URL: `http://localhost:8080/api/v1/cart/remove`
  - Headers: `X-Roll-Number: 1`, `X-User-ID: 1`
  - Body: `{}`
- Expected result: `400` for missing `product_id`.
- Actual result observed: `404 Not Found`.

### Bug ID: BB-14
- Endpoint tested: `/api/v1/products/{product_id}/reviews`
- Request payload:
  - Method: `POST`
  - URL: `http://localhost:8080/api/v1/products/1/reviews`
  - Headers: `X-Roll-Number: 1`, `X-User-ID: 1`
  - Body: `{"comment":"good"}`
- Expected result: `400` for missing `rating`.
- Actual result observed: `200 OK`.

### Bug ID: BB-15
- Endpoint tested: `/api/v1/addresses/{address_id}`
- Request payload:
  - Method: `PUT`
  - URL: `http://localhost:8080/api/v1/addresses/{address_id}`
  - Headers: `X-Roll-Number: 1`, `X-User-ID: 1`
  - Body examples: `{"label":"OFFICE","street":"Updated Street","is_default":false}`, `{"city":"Mumbai","street":"Updated Street","is_default":false}`, `{"pincode":"400001","street":"Updated Street","is_default":false}`
- Expected result: `400` because `label`/`city`/`pincode` are restricted in update.
- Actual result observed: `200 OK`.

### Bug ID: BB-16
- Endpoint tested: `/api/v1/addresses/{address_id}`
- Request payload:
  - Method: `PUT`
  - URL: `http://localhost:8080/api/v1/addresses/{address_id}`
  - Headers: `X-Roll-Number: 1`, `X-User-ID: 1`
  - Body: `{"street":"1234","is_default":false}`
- Expected result: `400` for street length below minimum.
- Actual result observed: `200 OK`.

### Bug ID: BB-17
- Endpoint tested: `/api/v1/cart`
- Validation: cart arithmetic consistency.
- Expected result: `subtotal == quantity * price` for each item; total equals sum of subtotals.
- Actual result observed: mismatched arithmetic (example observed: subtotal `-16` for quantity `2`, price `120`).

### Bug ID: BB-18
- Endpoint tested: `/api/v1/cart/update`
- Request payload:
  - Method: `POST`
  - URL: `http://localhost:8080/api/v1/cart/update`
  - Headers: `X-Roll-Number: 1`, `X-User-ID: 1`
  - Body: `{"product_id":99999999,"quantity":2}`
- Expected result: `404` for nonexistent cart product.
- Actual result observed: `200 OK`.

### Bug ID: BB-19
- Endpoint tested: `/api/v1/loyalty/redeem`
- Request payload:
  - Method: `POST`
  - URL: `http://localhost:8080/api/v1/loyalty/redeem`
  - Headers: `X-Roll-Number: 1`, `X-User-ID: 1`
  - Body: `{"points": current_points + 1}`
- Expected result: `400` when redeeming more points than available.
- Actual result observed: `200 OK`.
