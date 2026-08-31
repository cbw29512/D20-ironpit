from __future__ import annotations

import re

from app.content.monster_bonus_action_source_audit import (
    _ARENA_NEUTRAL_BONUS_ACTIONS,
    _base_name,
    parse_bonus_action_names,
)
from app.content.monster_catalog import _READY_BY_NAME, load_monster_rows
from app.content.monster_defense_source_audit import parse_defense_profile
from app.content.monster_legendary_source_audit import parse_legendary_action_names
from app.content.monster_limited_use_source_audit import parse_limited_use_names
from app.content.monster_reaction_source_audit import parse_reaction_names
from app.content.monster_spellcasting_source_audit import arena_neutral_spellcasting, spellcasting_fingerprint
from app.content.monster_trait_source_audit import _ARENA_NEUTRAL_TRAITS, _MODELED_TRAITS, parse_trait_names

_CONDITION_OR_CONTROL = re.compile(
    r"\b(blinded|charmed|deafened|frightened|grappled|incapacitated|paralyzed|petrified|poisoned|prone|restrained|stunned|unconscious|push(?:ed)?|pull(?:ed)?|swallow(?:ed)?)\b",
    re.I,
)
_COMPLEX_ACTION = re.compile(
    r"\b(Saving Throw|Failure:|Success:|Temporary Hit Points?|regains?\s+\d+|teleport|Concentration)\b",
    re.I,
)
_ATTACK_ROLL = re.compile(r"\b(?:Melee|Ranged|Melee or Ranged)\s+Attack Roll:", re.I)
_ALLOWED_TRAITS = set(_ARENA_NEUTRAL_TRAITS) | set(_MODELED_TRAITS)


def _source_blockers(row: dict[str, object]) -> list[str]:
    blockers: list[str] = []
    traits = parse_trait_names(row.get("traits", ""))
    unknown_traits = [name for name in traits if name not in _ALLOWED_TRAITS]
    if unknown_traits:
        blockers.append("trait")
    reactions = parse_reaction_names(row.get("reactions", ""))
    if reactions:
        blockers.append("reaction")
    bonus = parse_bonus_action_names(row.get("bonusActions", ""))
    if any(_base_name(name) not in _ARENA_NEUTRAL_BONUS_ACTIONS for name in bonus):
        blockers.append("bonus-action")
    if parse_limited_use_names(row):
        blockers.append("limited-use")
    if parse_legendary_action_names(row.get("legendaryActions", "")):
        blockers.append("legendary")
    if spellcasting_fingerprint(row) is not None and not arena_neutral_spellcasting(row):
        blockers.append("spellcasting")
    try:
        parse_defense_profile(row)
    except ValueError:
        blockers.append("defense-clause")
    actions = str(row.get("actions", ""))
    if not _ATTACK_ROLL.search(actions):
        blockers.append("no-attack-roll")
    if _COMPLEX_ACTION.search(actions):
        blockers.append("save-or-complex-action")
    if _CONDITION_OR_CONTROL.search(actions):
        blockers.append("condition-or-control")
    return blockers


def main() -> None:
    rows = load_monster_rows()
    safe = []
    already_ready = []
    for row in rows:
        blockers = _source_blockers(row)
        if blockers:
            continue
        name = str(row["name"])
        if name in _READY_BY_NAME:
            already_ready.append(name)
        else:
            safe.append(name)
    print(f"ZERO_ENGINE_BASELINE existing={len(already_ready)} missing={len(safe)}")
    for name in safe:
        print(f"ZERO_ENGINE_MISSING\t{name}")


if __name__ == "__main__":
    main()
