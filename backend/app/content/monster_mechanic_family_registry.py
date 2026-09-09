from __future__ import annotations

from typing import Literal, TypedDict

LayerStatus = Literal["supported", "partial", "missing", "source_defect"]


class MechanicFamilyStatus(TypedDict):
    status: LayerStatus
    parser: LayerStatus
    python: LayerStatus
    browser: LayerStatus
    audit: LayerStatus
    next_primitive: str


MONSTER_MECHANIC_FAMILIES: dict[str, MechanicFamilyStatus] = {
    "trait": {
        "status": "partial", "parser": "partial", "python": "partial", "browser": "partial", "audit": "partial",
        "next_primitive": "compile unsupported trait headings into reusable trigger/effect primitives",
    },
    "trait-parse": {
        "status": "source_defect", "parser": "source_defect", "python": "supported", "browser": "supported", "audit": "source_defect",
        "next_primitive": "tighten trait source parsing without name-based behavior",
    },
    "reaction": {
        "status": "partial", "parser": "partial", "python": "partial", "browser": "partial", "audit": "partial",
        "next_primitive": "generic reaction trigger and response composition",
    },
    "reaction-parse": {
        "status": "source_defect", "parser": "source_defect", "python": "supported", "browser": "supported", "audit": "source_defect",
        "next_primitive": "tighten reaction source parsing",
    },
    "bonus-action": {
        "status": "partial", "parser": "partial", "python": "partial", "browser": "partial", "audit": "partial",
        "next_primitive": "generic bonus-action compilation through the normal action/effect path",
    },
    "bonus-action-parse": {
        "status": "source_defect", "parser": "source_defect", "python": "supported", "browser": "supported", "audit": "source_defect",
        "next_primitive": "tighten bonus-action source parsing",
    },
    "limited-use": {
        "status": "partial", "parser": "partial", "python": "partial", "browser": "partial", "audit": "partial",
        "next_primitive": "generic limited-use resource declaration and refresh policy",
    },
    "limited-use-parse": {
        "status": "source_defect", "parser": "source_defect", "python": "supported", "browser": "supported", "audit": "source_defect",
        "next_primitive": "tighten limited-use source parsing",
    },
    "legendary": {
        "status": "missing", "parser": "missing", "python": "missing", "browser": "missing", "audit": "missing",
        "next_primitive": "legendary action point pool plus after-turn timing",
    },
    "spellcasting": {
        "status": "partial", "parser": "partial", "python": "partial", "browser": "partial", "audit": "partial",
        "next_primitive": "compile remaining combat spells into the canonical action/effect vocabulary",
    },
    "defense-clause": {
        "status": "partial", "parser": "partial", "python": "partial", "browser": "partial", "audit": "partial",
        "next_primitive": "normalize unsupported defense clauses into typed defenses/modifiers",
    },
    "no-attack-roll": {
        "status": "partial", "parser": "partial", "python": "partial", "browser": "partial", "audit": "partial",
        "next_primitive": "automatic/check/save action resolution that does not require an attack roll",
    },
    "conditional-attack-modifier": {
        "status": "partial", "parser": "partial", "python": "partial", "browser": "partial", "audit": "partial",
        "next_primitive": "data-driven conditional attack modifier predicates",
    },
    "save-or-complex-action": {
        "status": "partial", "parser": "partial", "python": "partial", "browser": "partial", "audit": "partial",
        "next_primitive": "ordered save/check/action effects including success/failure branches",
    },
    "condition-or-control": {
        "status": "partial", "parser": "partial", "python": "partial", "browser": "partial", "audit": "partial",
        "next_primitive": "complete condition/control semantics and lifecycle variants",
    },
    "unsupported-action-rider": {
        "status": "partial", "parser": "partial", "python": "partial", "browser": "partial", "audit": "partial",
        "next_primitive": "represent remaining hit/miss/attachment/speed riders as ordered effects",
    },
    "source-neighbor-bleed": {
        "status": "source_defect", "parser": "source_defect", "python": "supported", "browser": "supported", "audit": "source_defect",
        "next_primitive": "repair canonical source row boundaries",
    },
    "unclassified-source-audit-gap": {
        "status": "source_defect", "parser": "source_defect", "python": "partial", "browser": "partial", "audit": "source_defect",
        "next_primitive": "trace source-to-IR round trip until the missing family is classified",
    },
}
