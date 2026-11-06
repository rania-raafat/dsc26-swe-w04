
import json
from pathlib import Path

from jsonschema import Draft202012Validator


SCHEMA_PATH = (
    Path(__file__).resolve().parents[2]
    / "contracts"
    / "transfer_card.schema.json"
)


def load_schema():
    with SCHEMA_PATH.open(encoding="utf-8") as file:
        return json.load(file)


def create_transfer(client):
    return client.post(
        "/v1/transfers",
        json={
            "itemCode": "MET500",
            "fromBranch": "heliopolis",
            "toBranch": "tanta",
            "quantity": 20,
        },
    )


# M07: API response must follow the camelCase contract.
def test_transfer_response_matches_json_schema(client):
    response = create_transfer(client)

    assert response.status_code == 201

    schema = load_schema()
    validator = Draft202012Validator(schema)

    errors = list(validator.iter_errors(response.json()))

    assert errors == [], [
        error.message for error in errors
    ]


# M07: Required public fields must use camelCase.
def test_transfer_card_contains_camel_case_fields(client):
    response = create_transfer(client)

    assert response.status_code == 201

    card = response.json()

    expected_fields = {
        "id",
        "itemCode",
        "fromBranch",
        "toBranch",
        "quantity",
        "priority",
        "status",
        "requestedAt",
    }

    assert set(card.keys()) == expected_fields


# M08: requestedAt must contain a UTC timezone marker.
def test_requested_at_is_iso_8601_utc(client):
    response = create_transfer(client)

    assert response.status_code == 201

    requested_at = response.json()["requestedAt"]

    assert requested_at.endswith("Z")

    schema = load_schema()
    validator = Draft202012Validator(schema)

    errors = list(
        validator.iter_errors(response.json())
    )

    assert errors == [], [
        error.message for error in errors
    ]
