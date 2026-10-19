"""Small deterministic offline extractor; limited to one English announcement.

Not a language model. Supported: comma-separated title, full date, clock, room.
An injected extractor lets tests exercise outputs independently of these patterns.
"""
import re

from decision import decide


def offline_extract(text):
    output = {"is_event": bool(re.search(
        r"\b(night|workshop|meeting|concert|lecture|seminar|tournament|festival)\b", text, re.I))}
    parts = [part.strip() for part in text.split(",")]
    title = next((part for part in parts if re.search(
        r"\b(night|workshop|meeting|concert|lecture|seminar|tournament|festival)\b", part, re.I)), "")
    patterns = {
        "date": r"\b(?:\d{4}-\d{2}-\d{2}|\d{1,2} [A-Za-z]+ \d{4})\b",
        "time": r"\b(?:\d{1,2}:\d{2}(?:\s*[AP]M)?|\d{1,2}\s+[AP]M)\b",
        "location": r"\b(?:Lab|Room)\s+[A-Za-z]\d{3}\b|\b[A-Za-z]\d{3}\b",
    }
    for name in ("title", "date", "time", "location"):
        match = re.search(patterns[name], text, re.I) if name != "title" else None
        value = title if name == "title" else match.group() if match else ""
        output[name] = {"value": value, "evidence": value, "confidence": 0.8 if value else 0.0}
    return output


def process(text, today, rooms, extractor=offline_extract):
    return decide(extractor(text), text, today, rooms)
