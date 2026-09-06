from __future__ import annotations

import re

from app.content.monster_combat_scope import feature_blocks
from app.content.monster_trait_source_audit import parse_trait_names

_ABILITY = r"Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma"
_DAMAGE = r"Acid|Bludgeoning|Cold|Fire|Force|Lightning|Necrotic|Piercing|Poison|Psychic|Radiant|Slashing|Thunder"
_CONDITION = r"Blinded|Charmed|Deafened|Exhaustion|Frightened|Incapacitated|Paralyzed|Petrified|Poisoned|Prone|Restrained|Stunned|Unconscious"
_SIZE = r"Tiny|Small|Medium|Large|Huge|Gargantuan"
_SIMPLE_SAVE = re.compile(
    rf"^(?P<name>.+?)\. (?P<ability>{_ABILITY}) Saving Throw: DC (?P<dc>\d+), "
    r"one creature .*?within (?P<range>\d+) feet\. Failure: \d+ "
    rf"\((?P<count>\d+)d(?P<size>\d+)(?P<bonus>\s*[+-]\s*\d+)?\) (?P<type>{_DAMAGE}) damage\."
    r"(?: Success: Half damage\.)?$",
    re.I,
)
_CONDITION_SAVE = re.compile(
    rf"^(?P<name>.+?)\. (?P<ability>{_ABILITY}) Saving Throw: DC (?P<dc>\d+), "
    rf"one creature .*?within (?P<range>\d+) feet\. Failure: The target has the (?P<condition>{_CONDITION}) condition "
    r"until the (?P<edge>start|end) of the .+? next turn\.$",
    re.I,
)
_GRAPPLE_SAVE = re.compile(
    rf"^(?P<name>.+?)\. (?P<ability>{_ABILITY}) Saving Throw: DC (?P<dc>\d+), "
    rf"one (?P<size>{_SIZE}) or smaller creature .*?within (?P<range>\d+) feet\. "
    r"Failure: The target has the Grappled condition \(escape DC (?P<escape>\d+)\)\.$",
    re.I,
)
_REPLACE_ONE = re.compile(r"\bcan replace one attack with a use of (?P<name>[A-Z][A-Za-z’'\- ]+)\.?")


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _condition_save_row(row: dict[str, object], match: re.Match[str]) -> dict[str, object]:
    monster_slug = _slug(str(row["name"])); edge = match.group("edge").lower()
    return {
        "id": f"srd-{monster_slug}-{_slug(match.group('name'))}", "name": match.group("name"),
        "save_ability": match.group("ability").lower(), "dc": int(match.group("dc")),
        "range_ft": int(match.group("range")),
        "failure_conditions": [{
            "kind": "condition", "condition": match.group("condition").lower(),
            "expiry_timing": f"source_turn_{edge}",
        }],
        "animation": "save-effect",
    }


def parse_simple_save_actions(row: dict[str, object]) -> list[dict[str, object]]:
    """Parse one-target damage or timed-condition saves; fail closed on other shapes."""
    source = str(row.get("actions", ""))
    headings = parse_trait_names(source, preserve_annotations=True) if source.strip() else []
    blocks = feature_blocks(source, headings) if headings else {}
    monster_slug = _slug(str(row["name"])); actions: list[dict[str, object]] = []
    for heading, block in blocks.items():
        if "Saving Throw:" not in block or "Attack Roll:" in block: continue
        match = _SIMPLE_SAVE.fullmatch(block)
        if match is None:
            condition_match = _CONDITION_SAVE.fullmatch(block)
            if condition_match is not None:
                actions.append(_condition_save_row(row, condition_match)); continue
            raise ValueError(f"Simple save parser cannot prove {row['name']} {heading!r}: {block!r}")
        bonus = int((match.group("bonus") or "0").replace(" ", ""))
        actions.append({
            "id": f"srd-{monster_slug}-{_slug(heading)}", "name": heading,
            "save_ability": match.group("ability").lower(), "dc": int(match.group("dc")),
            "range_ft": int(match.group("range")),
            "damage": {"count": int(match.group("count")), "size": int(match.group("size")), "bonus": bonus},
            "damage_type": match.group("type").lower(), "success_damage": "half" if "Success: Half damage." in block else "none",
            "animation": "save-effect",
        })
    return actions


def attach_save_replacement(
    row: dict[str, object], multiattack: dict[str, object] | None, save_actions: list[dict[str, object]],
) -> dict[str, object] | None:
    """Allow exactly one Multiattack slot to use a printed replacement save action."""
    if multiattack is None or not save_actions: return multiattack
    source = str(row.get("actions", "")); headings = parse_trait_names(source, preserve_annotations=True)
    blocks = feature_blocks(source, headings); match = _REPLACE_ONE.search(blocks.get("Multiattack", ""))
    if match is None: return multiattack
    by_name = {str(action["name"]): str(action["id"]) for action in save_actions}
    save_id = by_name.get(match.group("name").strip())
    if save_id is None: return multiattack
    result = dict(multiattack); slots = [dict(slot) for slot in multiattack["slots"]]
    if not slots: raise ValueError(f"{row['name']} replacement save requires a Multiattack slot.")
    slots[0]["save_action_ids"] = [save_id]; result["slots"] = slots
    return result


def parse_simple_bonus_save_actions(row: dict[str, object]) -> list[dict[str, object]]:
    """Parse mathematically simple Bonus Action saves into the same universal save capability."""
    source = str(row.get("bonusActions", ""))
    headings = parse_trait_names(source, preserve_annotations=True) if source.strip() else []
    blocks = feature_blocks(source, headings) if headings else {}
    monster_slug = _slug(str(row["name"])); actions: list[dict[str, object]] = []
    for heading, block in blocks.items():
        if "Saving Throw:" not in block: continue
        match = _GRAPPLE_SAVE.fullmatch(block)
        if match is None: raise ValueError(f"Simple bonus-save parser cannot prove {row['name']} {heading!r}: {block!r}")
        actions.append({
            "id": f"srd-{monster_slug}-{_slug(heading)}", "name": heading, "action_cost": "bonus_action",
            "save_ability": match.group("ability").lower(), "dc": int(match.group("dc")), "range_ft": int(match.group("range")),
            "target_max_size": match.group("size").lower(),
            "grapple": {"kind": "grapple", "escape_dc": int(match.group("escape")), "max_target_size": match.group("size").lower()},
            "animation": "grapple",
        })
    return actions
