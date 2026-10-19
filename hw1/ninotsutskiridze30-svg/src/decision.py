"""Pure decision policy. No I/O or model calls."""
from datetime import date, datetime
import re

from pydantic import ValidationError
from schema import Extraction


FIELDS = ("title", "date", "time", "location")
WEEKDAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")


def normalize(field, value):
    value = value.strip()
    if field == "date":
        for pattern in ("%Y-%m-%d", "%d %B %Y", "%d %b %Y"):
            try:
                return datetime.strptime(value, pattern).date().isoformat()
            except ValueError:
                pass
        raise ValueError("Use a valid ISO date or day, English month, year.")
    if field == "time":
        for pattern in ("%H:%M", "%I:%M %p", "%I %p"):
            try:
                return datetime.strptime(value.upper(), pattern).strftime("%H:%M")
            except ValueError:
                pass
        raise ValueError("Use a valid 24-hour time or AM/PM time.")
    if field == "location":
        return re.sub(r"^(?:lab|room)\s+", "", value, flags=re.I).strip().upper()
    return value


def decide(extraction, source_text, today, rooms):
    """Return {route, fields, flags}; today is a date, rooms contains canonical codes.

    Validation > non-event > unsafe/required fields > soft flags > accepted.
    Evidence must both occur literally and support the normalized value.
    """
    fields = {name: {"value": "", "evidence": "", "confidence": 0.0} for name in FIELDS}
    flags = []

    def flag(code, field, reason):
        flags.append({"code": code, "field": field, "reason": reason})

    def result(route):
        return {"route": route, "fields": fields, "flags": flags}

    try:
        raw = extraction.model_dump() if isinstance(extraction, Extraction) else extraction
        parsed = Extraction.model_validate(raw)
    except ValidationError:
        flag("invalid_extraction", None, "Extractor output failed schema validation; check the draft manually.")
        return result("review")
    if not parsed.is_event:
        flag("not_event", None, "The announcement is classified as a notice, not an event.")
        return result("rejected")
    unsafe = False
    for name in FIELDS:
        item = getattr(parsed, name)
        if not item.value.strip():
            if name != "time":
                flag("missing_required", name, f"{name.title()} is required and was not provided.")
                unsafe = True
            continue
        if not item.evidence.strip() or item.evidence not in source_text:
            flag("no_evidence", name, f"{name.title()} has no exact supporting text in the announcement.")
            unsafe = True
            continue
        try:
            value = normalize(name, item.value)
            supported = value == normalize(name, item.evidence)
        except ValueError:
            flag("invalid_value", name, f"{name.title()} cannot be normalized; enter it manually.")
            unsafe = True
            continue
        if not supported or not value:
            flag("unsupported_value", name, f"{name.title()} differs from its evidence; leave it empty for review.")
            unsafe = True
            continue
        fields[name] = {"value": value, "evidence": item.evidence, "confidence": item.confidence}
        if item.confidence < 0.6:
            flag("low_confidence", name, f"{name.title()} confidence is below 0.6; confirm the supported value.")
    if fields["date"]["value"]:
        event_date = date.fromisoformat(fields["date"]["value"])
        if event_date < today:
            flag("past_date", "date", "The event date is before today.")
        stated = re.findall(r"\b(" + "|".join(WEEKDAYS) + r")\b", source_text, flags=re.I)
        if any(day.lower() != WEEKDAYS[event_date.weekday()].lower() for day in stated):
            flag("weekday_mismatch", "date", "A stated weekday does not match the event date.")
    if fields["location"]["value"] and fields["location"]["value"] not in rooms:
        flag("unknown_room", "location", "The room code is absent from the supplied room list.")
    return result("review" if unsafe else "confirm" if flags else "accepted")
