from __future__ import annotations

from app.content.capability_compiler import compile_combatant
from app.content.monster_source_audit import audit_monster_source
from app.content.monster_source_metadata import complete_monster_source_metadata
from app.content.simple_monster_source_definitions import _definition


def auto_discovery_failure(row: dict[str, object]) -> tuple[str, str]:
    """Explain why a blocked SRD row cannot yet use the generic source compiler."""
    try:
        definition = _definition(row)
    except Exception as exc:
        return "parse", f"{type(exc).__name__}: {exc}"
    try:
        template = complete_monster_source_metadata([compile_combatant(definition)])[0]
        issues = audit_monster_source(template, row)
    except Exception as exc:
        return "runtime", f"{type(exc).__name__}: {exc}"
    if issues:
        return "audit", " | ".join(issues)
    return "ready", "generic source compiler and full audit both pass"
