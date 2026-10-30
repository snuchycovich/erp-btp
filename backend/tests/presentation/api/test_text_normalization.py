"""Tests for normalization of untrusted plain-text API fields."""

import pytest

from app.presentation.api.text_normalization import normalize_plain_text


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("<strong>Pose</strong> de carrelage", "Pose de carrelage"),
        ("AT&amp;T", "AT&T"),
        ("<script>alert(1)</script>Peinture", "Peinture"),
        ("<p>Pose</p><p>Peinture</p>", "Pose Peinture"),
        (" Isolation\n\tthermique   renforcée ", "Isolation thermique renforcée"),
        ("<!-- secret --><div onclick='alert(1)'>Plomberie</div>", "Plomberie"),
    ],
)
def test_normalize_plain_text(value: str, expected: str) -> None:
    """Convert HTML-like values into normalized visible text."""
    assert normalize_plain_text(value) == expected
