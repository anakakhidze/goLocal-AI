"""Read only the fixed, versioned GoLocal corpus; never construct a path from input."""
from datetime import date
from pathlib import Path
import re
from urllib.parse import urlsplit

from pydantic import BaseModel, ConfigDict, Field


CORPUS = Path(__file__).resolve().parents[1] / "data" / "corpus" / "events"
SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
NOTICE = (
    "Historical listing snapshot, not live availability. Dates, prices, entry rules, "
    "and status may have changed. Check the original source before making plans."
)


class CatalogError(Exception):
    """A corpus problem; callers receive a sanitized, actionable message."""


class EventDetails(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    event_id: str
    title: str
    source_url: str
    snapshot_date: date
    event_time: str | None
    location: str | None
    details: str = Field(max_length=12000)
    kind: str
    live_verified: bool = False
    notice: str = NOTICE


def load_catalog(root: Path | None = None) -> dict[str, EventDetails]:
    """Reload curated files for every request; return no guessed facts or cached inventory."""
    root = CORPUS if root is None else root
    try:
        files = sorted(root.glob("*.md"))
        if not files or len(files) > 100:
            raise ValueError("Invalid corpus size")
        records = {}
        for path in files:
            if path.is_symlink() or not SLUG.fullmatch(path.stem) or path.stat().st_size > 32768:
                raise ValueError("Invalid corpus file")
            text = path.read_text(encoding="utf-8")
            lines = text.splitlines()
            if not lines or not lines[0].startswith("# "):
                raise ValueError("Missing title")
            metadata = {}
            for line in lines[1:]:
                if line.startswith("- ") and ": " in line:
                    key, value = line[2:].split(": ", 1)
                    if key in metadata:
                        raise ValueError("Duplicate metadata")
                    metadata[key] = value.strip()
            source = metadata["Source"]
            url = urlsplit(source)
            if (url.scheme != "https" or not url.hostname or url.username or url.password
                    or any(c.isspace() or ord(c) < 32 for c in source)):
                raise ValueError("Invalid source")
            compiled_values = [metadata[k] for k in ("Compiled from the public listing", "Compiled from the public listings")
                               if k in metadata]
            if len(compiled_values) != 1:
                raise ValueError("Missing or ambiguous snapshot date")
            compiled = date.fromisoformat(compiled_values[0])
            if compiled.isoformat() != compiled_values[0]:
                raise ValueError("Noncanonical snapshot date")
            body = text.split("\n## ", 1)
            details = "## " + body[1].strip() if len(body) == 2 else ""
            if not details:
                raise ValueError("Missing details")
            records[path.stem] = EventDetails(
                event_id=path.stem, title=lines[0][2:].strip(), source_url=source,
                snapshot_date=compiled, event_time=(metadata.get("Event time") or metadata.get("Event dates")
                                                   or metadata.get("Listed performance")),
                location=metadata.get("Venue") or metadata.get("Location") or metadata.get("Venue and organizer"),
                # This is the reviewed venue-only document in the existing corpus.
                # An absent date alone does not turn the other event listings into venues.
                details=details, kind="venue" if path.stem == "digomi-olympic-pool" else "event",
            )
        return records
    except (OSError, UnicodeError, ValueError, KeyError) as exc:
        raise CatalogError("Event data is unavailable. Ask the maintainer to check the curated corpus; retry later.") from exc
