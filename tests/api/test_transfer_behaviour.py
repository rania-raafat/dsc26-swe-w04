
from datetime import UTC, datetime

from nour_transfers.app import create_app
from fastapi.testclient import TestClient


def make_transfer(client, item="MET500", source="heliopolis",
                  destination="tanta", quantity=10):
    return client.post(
        "/v1/transfers",
        json={
            "itemCode": item,
            "fromBranch": source,
            "toBranch": destination,
            "quantity": quantity,
        },
    )


# M06: An approved transfer cannot be approved again.
def test_approving_transfer_twice_is_rejected(client):
    response = make_transfer(client, quantity=20)
    assert response.status_code == 201

    transfer_id = response.json()["id"]

    first = client.post(f"/v1/transfers/{transfer_id}/approve")
    assert first.status_code == 200
    assert first.json()["status"] == "approved"

    second = client.post(f"/v1/transfers/{transfer_id}/approve")
    assert second.status_code == 409
    assert second.json()["type"] == "/problems/not-pending"


# Approval must recheck the reserve using current stock.
def test_approval_rechecks_current_source_stock(client):
    first = make_transfer(client, quantity=20)
    second = make_transfer(client, quantity=20)

    assert first.status_code == 201
    assert second.status_code == 201

    first_id = first.json()["id"]
    second_id = second.json()["id"]

    approved = client.post(f"/v1/transfers/{first_id}/approve")
    assert approved.status_code == 200

    rejected = client.post(f"/v1/transfers/{second_id}/approve")
    assert rejected.status_code == 409
    assert rejected.json()["type"] == "/problems/below-reserve"

    source = client.get(
        "/v1/branches/heliopolis/stock/MET500"
    )
    destination = client.get(
        "/v1/branches/tanta/stock/MET500"
    )

    assert source.json()["units"] == 20
    assert destination.json()["units"] == 22


# M09: Only the two specified origins are allowed.
def test_cors_rejects_unapproved_origin(client):
    response = client.options(
        "/v1/transfers",
        headers={
            "Origin": "https://evil.example",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )

    assert response.status_code == 400
    assert "access-control-allow-origin" not in response.headers


def test_cors_allows_branch_web_origin(client):
    origin = "https://branch.nour.example"

    response = client.options(
        "/v1/transfers",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == origin
    assert response.headers["access-control-allow-credentials"] == "true"


# M10: Destination inbox is sorted by priority.
def test_inbox_sorts_urgent_high_then_normal():
    now = lambda: datetime(2026, 11, 5, 9, 30, tzinfo=UTC)

    app = create_app(
        stock={
            ("source_normal", "NORMAL"): 100,
            ("source_high", "HIGH"): 100,
            ("source_urgent", "URGENT"): 100,
            ("destination", "NORMAL"): 100,
            ("destination", "HIGH"): 5,
            ("destination", "URGENT"): 2,
        },
        items={
            "NORMAL": {"chronic": False, "reserve": 0},
            "HIGH": {"chronic": False, "reserve": 0},
            "URGENT": {"chronic": True, "reserve": 0},
        },
        sales={
            ("destination", "NORMAL"): 10,
            ("destination", "HIGH"): 1,
            ("destination", "URGENT"): 1,
        },
        now=now,
    )

    test_client = TestClient(app)

    # Deliberately create them in the opposite order.
    normal = test_client.post(
        "/v1/transfers",
        json={
            "itemCode": "NORMAL",
            "fromBranch": "source_normal",
            "toBranch": "destination",
            "quantity": 1,
        },
    )

    high = test_client.post(
        "/v1/transfers",
        json={
            "itemCode": "HIGH",
            "fromBranch": "source_high",
            "toBranch": "destination",
            "quantity": 1,
        },
    )

    urgent = test_client.post(
        "/v1/transfers",
        json={
            "itemCode": "URGENT",
            "fromBranch": "source_urgent",
            "toBranch": "destination",
            "quantity": 1,
        },
    )

    assert normal.status_code == 201
    assert high.status_code == 201
    assert urgent.status_code == 201

    response = test_client.get(
        "/v1/branches/destination/transfers"
    )

    assert response.status_code == 200

    cards = response.json()["items"]

    assert [card["priority"] for card in cards] == [
        "urgent",
        "high",
        "normal",
    ]


# M11: Errors must use application/problem+json.
def test_error_response_uses_problem_json_media_type(client):
    response = client.post(
        "/v1/transfers",
        json={
            "itemCode": "UNKNOWN",
            "fromBranch": "heliopolis",
            "toBranch": "tanta",
            "quantity": 1,
        },
    )

    assert response.status_code == 404
    assert response.headers["content-type"].startswith(
        "application/problem+json"
    )
    assert response.json()["type"] == "/problems/unknown-item"
    assert response.json()["status"] == 404


# M12: A branch cannot transfer stock to itself.
def test_same_branch_transfer_is_rejected(client):
    response = make_transfer(
        client,
        source="heliopolis",
        destination="heliopolis",
        quantity=1,
    )

    assert response.status_code == 422
    assert response.json()["type"] == "/problems/same-branch"


# M13: Successful approval must debit and credit stock.
def test_approval_moves_stock_to_destination(client):
    response = make_transfer(client, quantity=20)

    assert response.status_code == 201

    transfer_id = response.json()["id"]

    approved = client.post(
        f"/v1/transfers/{transfer_id}/approve"
    )

    assert approved.status_code == 200
    assert approved.json()["status"] == "approved"

    source = client.get(
        "/v1/branches/heliopolis/stock/MET500"
    )
    destination = client.get(
        "/v1/branches/tanta/stock/MET500"
    )

    assert source.status_code == 200
    assert destination.status_code == 200

    assert source.json()["units"] == 20
    assert destination.json()["units"] == 22
