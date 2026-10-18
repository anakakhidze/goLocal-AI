"""Validated extractor output. Empty strings mean unknown, never guessed."""
from pydantic import BaseModel, ConfigDict, Field


class ExtractedField(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    value: str = ""
    evidence: str = ""
    confidence: float = Field(default=0.0, ge=0, le=1, allow_inf_nan=False)


class Extraction(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    is_event: bool
    title: ExtractedField = Field(default_factory=ExtractedField)
    date: ExtractedField = Field(default_factory=ExtractedField)
    time: ExtractedField = Field(default_factory=ExtractedField)
    location: ExtractedField = Field(default_factory=ExtractedField)
