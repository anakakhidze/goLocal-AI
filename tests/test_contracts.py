import pytest
from pydantic import ValidationError

from src.contracts import GetEventDetails, ListEvents


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
