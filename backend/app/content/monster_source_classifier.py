from __future__ import annotations

import re

from app.content.monster_attack_roll_modifier_source_audit import unsupported_conditional_attack_modifier
from app.content.monster_bonus_action_source_audit import _ARENA_NEUTRAL_BONUS_ACTIONS, _base_name, parse_bonus_action_names
from app.content.monster_defense_source_audit import parse_defense_profile
from app.content.monster_limited_use_source_audit import parse_action_recharges, parse_limited_use_names
from app.content.monster_reaction_source_audit import parse_parry_ac_bonus, parse_reaction_names, parse_redirect_attack_range
from app.content.monster_simple_control_rider import has_unmodeled_control_text
from app.content.monster_simple_hit_modifier_rider import strip_modeled_hit_modifier_riders
from app.content.monster_simple_save_control_parser import strip_simple_save_control_actions
from app.content.monster_simple_save_parser import strip_simple_save_actions
from app.content.monster_spellcasting_source_audit import arena_neutral_spellcasting, spellcasting_fingerprint
from app.content.monster_trait_source_audit import _ARENA_NEUTRAL_TRAITS, _MODELED_TRAITS, parse_trait_names

_COMPLEX_ACTION = re.compile(
    r"\b(Saving Throw|Failure:|Success:|Temporary Hit Points?|regains?\s+\d+|teleport|Concentration)\b",
    re.I,
)
_DAMAGE_TYPES = r"Acid|Bludgeoning|Cold|Fire|Force|Lightning|Necrotic|Piercing|Poison|Psychic|Radiant|Slashing|Thunder"
_SUPPORTED_BLOODIED_REPLACEMENT = re.compile(
    rf"\bdamage,?\s+or\s+\d+\s*\(\s*\d+\s*d\s*\d+(?:\s*[+-]\s*\d+)?\s*\)\s+"
    rf"(?:{_DAMAGE_TYPES})\s+damage\s+if\s+the\s+[a-z][a-z -]*\s+is\s+Bloodied\b",
    re.I,
)
_SUPPORTED_FIXED_RIDER = re.compile(rf"\bplus\s+\d+\s+(?:{_DAMAGE_TYPES})\s+damage\b", re.I)
_SUPPORTED_RETURNING_WEAPON = re.compile(
    r"Hit or Miss:\s+The\s+[A-Za-z’' -]+\s+magically returns to\s+the\s+[A-Za-z’' -]+(?:’s|'s)\s+hand\s+"
    r"immediately after a ranged attack\.?",
    re.I,
)
_HIDDEN_RIDER = re.compile(
    r"\b(?:Speed decreases|attaches?|detaches?|next attack roll|Hit or Miss:)\b"
    r"|\bdamage,?\s+or\s+\d+\s*\([^)]*\)\s+\w+\s+damage\s+if\b",
    re.I,
)
_ATTACK_ROLL = re.compile(r"\b(?:Melee|Ranged|Melee or Ranged)\s+Attack Roll:", re.I)
_ALLOWED_TRAITS = set(_ARENA_NEUTRAL_TRAITS) | set(_MODELED_TRAITS)


def _has_neighbor_bleed(row: dict[str, object], monster_names: set[str]) -> bool:
    actions = str(row.get("actions", "")).rstrip()
    own_name = str(row.get("name", ""))
    return any(name != own_name and actions.endswith(name) for name in monster_names)


def _reaction_is_modeled(row: dict[str, object], reactions: list[str]) -> bool:
    source = row.get("reactions", "")
    if reactions == ["Parry"]:
        return parse_parry_ac_bonus(source) is not None
    if reactions == ["Redirect Attack"]:
        return parse_redirect_attack_range(source) == 5
    return not reactions


def _limited_uses_are_simple_action_recharges(row: dict[str, object]) -> bool:
    names = parse_limited_use_names(row)
    if not names:
        return True
    recharges = parse_action_recharges(row)
    return bool(recharges) and len(names) == len(recharges) and all(name.startswith("actions:") for name in names)


def _unmodeled_action_rider(actions: str) -> bool:
    clean = _SUPPORTED_BLOODIED_REPLACEMENT.sub("damage", actions)
    clean = _SUPPORTED_FIXED_RIDER.sub("", clean)
    clean = _SUPPORTED_RETURNING_WEAPON.sub("", clean)
    clean = strip_modeled_hit_modifier_riders(clean)
    return bool(_HIDDEN_RIDER.search(clean))


def source_blockers(row: dict[str, object], monster_names: set[str]) -> list[str]:
    """Return generic mechanic families preventing source-driven auto-compilation."""
    blockers: list[str] = []
    try:
        if any(name not in _ALLOWED_TRAITS for name in parse_trait_names(row.get("traits", ""))):
            blockers.append("trait")
    except ValueError:
        blockers.append("trait-parse")
    try:
        reactions = parse_reaction_names(row.get("reactions", ""))
        if not _reaction_is_modeled(row, reactions):
            blockers.append("reaction")
    except ValueError:
        blockers.append("reaction-parse")
    try:
        bonus = parse_bonus_action_names(row.get("bonusActions", ""))
        if any(_base_name(name) not in _ARENA_NEUTRAL_BONUS_ACTIONS for name in bonus):
            blockers.append("bonus-action")
    except ValueError:
        blockers.append("bonus-action-parse")
    try:
        if not _limited_uses_are_simple_action_recharges(row):
            blockers.append("limited-use")
    except ValueError:
        blockers.append("limited-use-parse")
    if str(row.get("legendaryActions", "")).strip():
        blockers.append("legendary")
    if spellcasting_fingerprint(row) is not None and not arena_neutral_spellcasting(row):
        blockers.append("spellcasting")
    try:
        parse_defense_profile(row)
    except ValueError:
        blockers.append("defense-clause")
    actions = str(row.get("actions", ""))
    simple_clean = strip_simple_save_control_actions(strip_simple_save_actions(actions))
    if not _ATTACK_ROLL.search(actions):
        blockers.append("no-attack-roll")
    try:
        if unsupported_conditional_attack_modifier(actions):
            blockers.append("conditional-attack-modifier")
    except ValueError:
        blockers.append("conditional-attack-modifier")
    if _COMPLEX_ACTION.search(simple_clean):
        blockers.append("save-or-complex-action")
    if has_unmodeled_control_text(simple_clean):
        blockers.append("condition-or-control")
    if _unmodeled_action_rider(simple_clean):
        blockers.append("unsupported-action-rider")
    if _has_neighbor_bleed(row, monster_names):
        blockers.append("source-neighbor-bleed")
    return blockers
