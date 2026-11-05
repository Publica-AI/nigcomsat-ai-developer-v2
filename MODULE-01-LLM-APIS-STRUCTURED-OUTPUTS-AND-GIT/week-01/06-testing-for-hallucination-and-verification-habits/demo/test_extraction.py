"""
Pytest suite for Module 1, Topic 6.

Run from the terminal in this folder:
    pytest test_extraction.py -v

test_duration_not_copied_from_summary needs a working .env (OPENAI_API_KEY,
MODEL_NAME, OPENAI_BASE_URL) -- it makes one plain, schema-free API call.
test_negative_customers_rejected does not call the model at all.
"""
import os
import re
from typing import Literal, Optional

import pytest
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, ValidationError, field_validator

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL"),
)
MODEL_NAME = os.getenv("MODEL_NAME")

SHIFT_NOTE = """*** SYNTHETIC DOCUMENT - FOR TRAINING USE ONLY - NOT A REAL NIGCOMSAT RECORD ***

NOC Shift Note - Incident NOC-INC-2026-0417

02:14 - Loss-of-carrier alarm raised on link KU-HUB1-GW3.
03:52 - Full service restored after the faulty amplifier (HPA-2) was bypassed.

Summary: The outage lasted approximately two hours.
"""

KNOWN_DURATION_MINUTES = 9  # 03:52 minus 02:14, computed by hand


def extract_minutes(text: str) -> int:
    """Pull the first integer out of the model's plain-text reply."""
    match = re.search(r"\d+", text)
    if not match:
        raise ValueError(f"No number found in model reply: {text!r}")
    return int(match.group())


class IncidentExtract(BaseModel):
    incident_id: str
    severity: Literal["P1", "P2", "P3", "P4"]
    affected_link: str
    customers_affected: int
    root_cause: Optional[str] = None

    @field_validator("customers_affected")
    @classmethod
    def must_be_non_negative(cls, v):
        if v < 0:
            raise ValueError("customers_affected cannot be negative")
        return v


def test_duration_not_copied_from_summary():
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": (
                    "Based on the shift note below, how long did the outage last, "
                    "in minutes? Reply with just the number.\n\n" + SHIFT_NOTE
                ),
            },
        ],
    )
    reported_minutes = extract_minutes(response.choices[0].message.content)
    assert reported_minutes == KNOWN_DURATION_MINUTES


def test_negative_customers_rejected():
    with pytest.raises(ValidationError):
        IncidentExtract(
            incident_id="NOC-INC-2026-0417",
            severity="P2",
            affected_link="KU-HUB1-GW3",
            customers_affected=-3,
            root_cause="unknown",
        )
