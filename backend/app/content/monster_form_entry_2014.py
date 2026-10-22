"""Validate source-declared precombat forms without monster-name dispatch."""
from __future__ import annotations
from collections.abc import Mapping, Sequence

def opening_form_id(forms: Mapping[str, object], *, opening_form: str, required_forms: Sequence[str] = ()) -> str:
    """Choose only a declared legal form, preserving all mandatory forms."""
    if not isinstance(opening_form, str) or not opening_form:
        raise ValueError("Opening form requires a source form ID.")
    if not forms or any(not isinstance(k, str) or not k or v is None for k, v in forms.items()):
        raise ValueError("Legal forms need valid IDs and compiled declarations.")
    if opening_form not in forms:
        raise ValueError("Opening form is not source-authorized.")
    if any(form not in forms for form in required_forms):
        raise ValueError("Required source form is missing.")
    return opening_form
