import pytest
from pydantic import ValidationError
from typing import get_args

from src.catalog import load_catalog
from src.contracts import EventKind, FindEventsByKind, GetEventDetails, ListEvents


@pytest.mark.parametrize("value", ["../.env", "../../.env", "a/b", "a\\b", "A-title", "", "x" * 65,
                                   "a\n", "a--b", "-a", "a-", "a;DROP TABLE", 1, None, True])
def test_event_id_is_a_bounded_slug(value):
    with pytest.raises(ValidationError):
        GetEventDetails(event_id=value)


@pytest.mark.parametrize("field", ["user", "user_id", "student", "account", "path", "url"])
def test_extra_fields_never_become_identity_or_resources(field):
    with pytest.raises(ValidationError):
        GetEventDetails.model_validate({"event_id": "hardhell", field: "other"})


@pytest.mark.parametrize("limit", [0, 21, -1, True, "5", 1.5])
def test_every_numeric_input_is_bounded_and_strict(limit):
    with pytest.raises(ValidationError):
        ListEvents(limit=limit)


def test_schema_is_closed_and_contains_the_actual_constraints():
    schema = GetEventDetails.model_json_schema()
    assert schema["additionalProperties"] is False
    assert schema["required"] == ["event_id"]
    field = schema["properties"]["event_id"]
    assert field["pattern"] and field["maxLength"] == 64
    assert ListEvents.model_json_schema()["properties"]["limit"]["maximum"] == 20


def test_find_kind_enum_matches_kinds_produced_for_all_catalog_files():
    records = load_catalog()
    assert len(records) == 13
    catalog_kinds = {record.kind for record in records.values()}
    assert catalog_kinds == {"event", "venue"}
    assert set(get_args(EventKind)) == catalog_kinds
    schema = FindEventsByKind.model_json_schema()
    assert set(schema["properties"]["kind"]["enum"]) == catalog_kinds
    assert schema["properties"]["limit"]["minimum"] == 1
    assert schema["properties"]["limit"]["maximum"] == 10


@pytest.mark.parametrize("payload", [
    {"kind": "concert tickets"}, {"kind": "event", "limit": 0},
    {"kind": "event", "limit": 11}, {"kind": "event", "limit": True},
    {"kind": "event", "limit": "3"}, {"kind": "event", "limit": 1.0},
    {"kind": "event", "user_id": "another-user"},
])
def test_find_events_by_kind_contract_rejects_unknown_or_out_of_range_inputs(payload):
    with pytest.raises(ValidationError):
        FindEventsByKind.model_validate(payload)
