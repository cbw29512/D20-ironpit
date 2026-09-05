from __future__ import annotations

import json
import re

from app.content.arena_eligibility import deferred_environment_reason
from app.content.iron_pit_mvp_scope import affects_mvp_combat_math, feature_block, source_feature_blocks
from app.content.monster_action_boundary_audit import unmodeled_combat_math_riders
from app.content.monster_bonus_action_source_audit import _ARENA_NEUTRAL_BONUS_ACTIONS, _base_name, parse_bonus_action_names
from app.content.monster_catalog import build_monster_catalog, load_monster_rows
from app.content.monster_defense_source_audit import parse_defense_profile
from app.content.monster_limited_use_source_audit import parse_limited_use_names
from app.content.monster_reaction_source_audit import parse_parry_ac_bonus, parse_reaction_names, parse_redirect_attack_range
from app.content.monster_spellcasting_source_audit import arena_neutral_spellcasting, spellcasting_fingerprint
from app.content.monster_trait_source_audit import (
    _ARENA_NEUTRAL_TRAITS, _MODELED_AURA_TRAITS, _MODELED_ROLL_ADVANTAGE_TRAITS, _MODELED_TRAITS, parse_trait_names,
)
from app.domain.catalog import CoverageStatus

_DIRECT_CONDITION = re.compile(r"\b(blinded|charmed|frightened|incapacitated|paralyzed|petrified|poisoned|prone|restrained|stunned|unconscious|swallow(?:s|ed)?)\b", re.I)
_SAVING_THROW = re.compile(r"\b(?:Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma)\s+Saving Throw:", re.I)
_ONGOING_RIDER = re.compile(r"\btakes?\s+\d+\s*\([^)]*\)\s+\w+\s+damage\s+at\s+the\s+(?:start|end)\s+of\b|\bhalves?\s+the\s+damage\s+it\s+takes\b|\btakes?\s+the\s+same\s+amount\s+of\s+damage\b", re.I)
_ALLOWED_TRAITS = set(_ARENA_NEUTRAL_TRAITS) | set(_MODELED_TRAITS) | set(_MODELED_ROLL_ADVANTAGE_TRAITS) | set(_MODELED_AURA_TRAITS)
_DETAIL_FIELDS = ("name", "size", "armorClass", "hitPoints", "speed", "challenge", "traits", "actions")
_DETAIL_BLOCKER_LIMIT = 30


def _has_neighbor_bleed(row: dict[str, object], monster_names: set[str]) -> bool:
    actions = str(row.get("actions", "")).rstrip(); own_name = str(row.get("name", ""))
    return any(name != own_name and actions.endswith(name) for name in monster_names)


def _reaction_is_modeled(row: dict[str, object], reactions: list[str]) -> bool:
    source = row.get("reactions", "")
    if reactions == ["Parry"]: return parse_parry_ac_bonus(source) is not None
    if reactions == ["Redirect Attack"]: return parse_redirect_attack_range(source) == 5
    return not reactions


def _feature_is_direct(source: object, heading: str) -> bool:
    block = feature_block(source, heading)
    return not block or affects_mvp_combat_math(block) or bool(re.search(r"\bcasts?\b", block, re.I))


def _has_in_scope_save(actions: object) -> bool:
    for _, block in source_feature_blocks(actions):
        for match in _SAVING_THROW.finditer(block):
            if affects_mvp_combat_math(block[match.start():]): return True
    return False


def _unmodeled_action_rider(actions: str) -> bool:
    return bool(_ONGOING_RIDER.search(actions) or unmodeled_combat_math_riders(actions))


def _source_blockers(row: dict[str, object], monster_names: set[str]) -> list[str]:
    blockers: list[str] = []
    try:
        source = row.get("traits", ""); traits = parse_trait_names(source)
        if any(name not in _ALLOWED_TRAITS and _feature_is_direct(source, name) for name in traits): blockers.append("trait")
    except ValueError: blockers.append("trait-parse")
    try:
        source = row.get("reactions", ""); reactions = parse_reaction_names(source)
        if not _reaction_is_modeled(row, reactions) and any(_feature_is_direct(source, name) for name in reactions): blockers.append("reaction")
    except ValueError: blockers.append("reaction-parse")
    try:
        source = row.get("bonusActions", ""); bonus = parse_bonus_action_names(source)
        if any(_base_name(name) not in _ARENA_NEUTRAL_BONUS_ACTIONS and _feature_is_direct(source, name) for name in bonus): blockers.append("bonus-action")
    except ValueError: blockers.append("bonus-action-parse")
    try:
        # Recharge/N-per-Day is a shared resource wrapper, not a separate effect family.
        # Runtime source audit still validates the exact resource wiring fail-closed.
        parse_limited_use_names(row)
    except ValueError: blockers.append("limited-use-parse")
    if str(row.get("legendaryActions", "")).strip(): blockers.append("legendary")
    if spellcasting_fingerprint(row) is not None and not arena_neutral_spellcasting(row): blockers.append("spellcasting")
    try: parse_defense_profile(row)
    except ValueError: blockers.append("defense-clause")
    actions = str(row.get("actions", ""))
    if _has_in_scope_save(actions): blockers.append("save-or-complex-action")
    if _DIRECT_CONDITION.search(actions): blockers.append("condition-or-control")
    if _unmodeled_action_rider(actions): blockers.append("unsupported-action-rider")
    if _has_neighbor_bleed(row, monster_names): blockers.append("source-neighbor-bleed")
    return blockers


def main() -> None:
    rows = load_monster_rows(); monster_names = {str(row["name"]) for row in rows}
    ready_names = {card.name for card in build_monster_catalog() if card.coverage_status is CoverageStatus.RAW_READY}
    safe: list[dict[str, object]] = []; already_ready: list[str] = []; deferred: list[str] = []
    blocker_counts: dict[str, int] = {}; blocker_names: dict[str, list[str]] = {}; reaction_details = []; rider_details = []
    for row in rows:
        name = str(row["name"])
        if name in ready_names:
            already_ready.append(name)
            continue
        if deferred_environment_reason(name) is not None: deferred.append(name); continue
        blockers = _source_blockers(row, monster_names)
        for blocker in set(blockers):
            blocker_counts[blocker] = blocker_counts.get(blocker, 0) + 1; blocker_names.setdefault(blocker, []).append(name)
        if "reaction" in blockers: reaction_details.append({"name": name, "blockers": blockers, "reactions": str(row.get("reactions", ""))})
        if "unsupported-action-rider" in blockers: rider_details.append({"name": name, "blockers": blockers, "actions": str(row.get("actions", ""))})
        if not blockers: safe.append(row)
    print(f"ZERO_ENGINE_BASELINE existing={len(already_ready)} missing={len(safe)} deferred={len(deferred)}")
    if deferred: print("ZERO_ENGINE_DEFERRED_ENVIRONMENT\t" + " | ".join(sorted(deferred)))
    for row in safe:
        detail = {field: row.get(field, "") for field in _DETAIL_FIELDS}; raw = str(row.get("rawText", "")); initiative = re.search(r"\bInitiative\s+([+-]?\d+)", raw, re.I)
        detail["initiative"] = int(initiative.group(1)) if initiative else None; print("ZERO_ENGINE_DETAIL\t" + json.dumps(detail, ensure_ascii=False, separators=(",", ":")))
    for detail in reaction_details: print("ZERO_ENGINE_REACTION_DETAIL\t" + json.dumps(detail, ensure_ascii=False, separators=(",", ":")))
    for detail in rider_details: print("ZERO_ENGINE_RIDER_DETAIL\t" + json.dumps(detail, ensure_ascii=False, separators=(",", ":")))
    for blocker, count in sorted(blocker_counts.items(), key=lambda item: (-item[1], item[0])):
        print(f"ZERO_ENGINE_BLOCKER\t{blocker}\t{count}")
        if count <= _DETAIL_BLOCKER_LIMIT: print(f"ZERO_ENGINE_BLOCKER_NAMES\t{blocker}\t" + " | ".join(sorted(blocker_names[blocker])))


if __name__ == "__main__": main()
