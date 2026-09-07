from __future__ import annotations

import logging
import re

from app.content.monster_attack_source_audit import attack_issues, normalized, save_action_issues
from app.content.monster_bonus_action_source_audit import bonus_action_issues
from app.content.monster_charge_source_audit import charge_replacement_issues
from app.content.monster_combat_scope import battle_ready_size, strip_post_combat_outcomes
from app.content.monster_defense_source_audit import defense_issues
from app.content.monster_legendary_source_audit import legendary_action_issues
from app.content.monster_limited_use_source_audit import limited_use_issues
from app.content.monster_reaction_source_audit import reaction_issues
from app.content.monster_save_math_source_audit import save_math_issues
from app.content.monster_saving_throws import parse_saving_throw_bonuses
from app.content.monster_spellcasting_source_audit import spellcasting_issues
from app.content.monster_survival_source_audit import survival_action_issues
from app.content.monster_trait_source_audit import trait_issues
from app.domain.models import CombatantTemplate

logger = logging.getLogger(__name__)
_SIZE_NAMES = ("tiny", "small", "medium", "large", "huge", "gargantuan")
_MELEE_ATTACK_ROLL = re.compile(r"\bMelee\s+Attack Roll:", re.IGNORECASE)
_RANGED_ATTACK_ROLL = re.compile(r"\bRanged\s+Attack Roll:", re.IGNORECASE)
_COMBINED_ATTACK_ROLL = re.compile(r"\bMelee\s+or\s+Ranged\s+Attack Roll:", re.IGNORECASE)
_SAVING_THROW = re.compile(r"\b(?:Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma)\s+Saving Throw:", re.IGNORECASE)


def _first_int(value: object) -> int:
    match = re.search(r"-?\d+", str(value))
    if not match: raise ValueError(f"No integer found in SRD value: {value!r}")
    return int(match.group())


def _initiative(row: dict[str, object]) -> int:
    match = re.search(r"\bInitiative\s+([+-]?\d+)", str(row.get("rawText", "")), re.IGNORECASE)
    if not match: raise ValueError(f"SRD initiative could not be parsed for {row.get('name')!r}.")
    return int(match.group(1))


def _challenge(row: dict[str, object]) -> str:
    return str(row["challenge"]).split()[0]


def _size_matches(runtime_size: str, row: dict[str, object]) -> bool:
    text = str(row["size"]).lower()
    allowed = {size for size in _SIZE_NAMES if re.search(rf"\b{size}\b", text)}
    ready = battle_ready_size(row)
    if ready: allowed.add(ready)
    if not allowed: raise ValueError(f"SRD size could not be parsed: {row['size']!r}")
    return runtime_size.lower() in allowed


def _source_attack_mode_count(actions: str) -> int:
    combined = len(_COMBINED_ATTACK_ROLL.findall(actions)); standalone = _COMBINED_ATTACK_ROLL.sub("", actions)
    return len(_MELEE_ATTACK_ROLL.findall(standalone)) + len(_RANGED_ATTACK_ROLL.findall(standalone)) + 2 * combined


def _embedded_hit_save_count(attacks: list[object]) -> int:
    return sum(1 for attack in attacks if getattr(getattr(attack, "control_effect", None), "initial_save_ability", None) is not None)


def audit_monster_source(template: CombatantTemplate, row: dict[str, object]) -> list[str]:
    """Reconcile Iron Pit combat math against the vendored SRD 5.2.1 record."""
    try:
        checks = (
            (template.name == str(row["name"]), "name-mismatch"),
            (_size_matches(template.size.value, row), "size-mismatch"),
            (template.armor_class == _first_int(row["armorClass"]), "armor-class-mismatch"),
            (template.max_hp == _first_int(row["hitPoints"]), "hit-points-mismatch"),
            (template.challenge_rating == _challenge(row), "challenge-rating-mismatch"),
            (template.initiative_bonus == _initiative(row), "initiative-mismatch"),
            (template.saving_throw_bonuses == parse_saving_throw_bonuses(row), "saving-throws-mismatch"),
        )
        issues = [label for passed, label in checks if not passed]
        issues.extend(defense_issues(template, row)); issues.extend(trait_issues(template, row)); issues.extend(reaction_issues(template, row))
        issues.extend(bonus_action_issues(template, row)); issues.extend(limited_use_issues(template, row)); issues.extend(legendary_action_issues(template, row))
        issues.extend(spellcasting_issues(template, row))
        actions = normalized(strip_post_combat_outcomes(row.get("actions", ""))); bonus_actions = normalized(row.get("bonusActions", ""))
        runtime_attacks = [template.weapon_attack, *template.alternate_weapon_attacks]
        action_saves = [action for action in template.saving_throw_actions if action.action_cost == "action"]
        bonus_saves = [action for action in template.saving_throw_actions if action.action_cost == "bonus_action"]
        issues.extend(survival_action_issues(actions, runtime_attacks))
        if _source_attack_mode_count(actions) != len(runtime_attacks): issues.append("source-attack-count-mismatch")
        expected_action_saves = len(action_saves) + _embedded_hit_save_count(runtime_attacks)
        if len(_SAVING_THROW.findall(actions)) != expected_action_saves: issues.append("source-save-action-count-mismatch")
        if len(_SAVING_THROW.findall(bonus_actions)) != len(bonus_saves): issues.append("source-bonus-save-count-mismatch")
        for attack in runtime_attacks: issues.extend(attack_issues(attack, actions))
        issues.extend(charge_replacement_issues(template, actions))
        for action in action_saves:
            issues.extend(save_action_issues(action, actions)); issues.extend(save_math_issues(action, actions))
        for action in bonus_saves:
            issues.extend(save_action_issues(action, bonus_actions)); issues.extend(save_math_issues(action, bonus_actions))
        if template.attack_action is not None and "multiattack" not in actions: issues.append("multiattack-source-missing")
        return issues
    except (KeyError, ValueError): raise
    except Exception as exc:
        logger.exception("SRD monster reconciliation failed for %s.", template.id)
        raise RuntimeError(f"Monster source audit failed for {template.id}.") from exc
