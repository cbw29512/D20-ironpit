"""Stage inherited and gained weapon attacks for a voluntary monster form.

Source-authored ability provenance is required to rebase the old creature's
Strength/Dexterity attack and damage bonuses.  A form's printed attack profile
already uses its own adopted physical scores; do not add the ability modifier a
second time. All existing damage riders and magical qualifiers are retained.
This pure function neither authorizes nor activates Change Shape.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Mapping

from app.domain.models import CombatantTemplate, WeaponAttack


@dataclass(frozen=True)
class SourceAttackAbility:
    """Explicit 2014 source proof for the *retained* attack's bonuses."""
    ability: Literal["strength", "dexterity", "fixed"]
    adds_ability_to_damage: bool = False


def compose_monster_form_weapon_profiles(
    owner: CombatantTemplate,
    form: CombatantTemplate,
    *,
    owner_attack_abilities: Mapping[str, SourceAttackAbility],
) -> tuple[WeaponAttack, ...]:
    """Return validated owner attacks then newly gained printed form attacks.

    The form legality/CR/type and eligibility of other gained capabilities must
    be validated separately. Do not register the resulting profiles in a live
    template until Multiattack references and all source riders are certified.
    """
    if owner.kind != "monster" or form.kind != "monster" or owner.ruleset != form.ruleset:
        raise ValueError("Form attacks require two same-edition monster sources.")
    if owner.ability_scores is None or form.ability_scores is None:
        raise ValueError("Attack rebasing requires source ability scores.")
    original_attacks = [owner.weapon_attack, *owner.alternate_weapon_attacks]
    gained_attacks = [form.weapon_attack, *form.alternate_weapon_attacks]
    ids = [row.id for row in original_attacks]
    if len(set(ids)) != len(ids):
        raise ValueError("Owner attack IDs must be unique.")
    if set(owner_attack_abilities) != set(ids):
        raise ValueError("Source provenance required for every retained attack ID.")

    result: list[WeaponAttack] = []
    for attack in original_attacks:
        rule = owner_attack_abilities[attack.id]
        if not isinstance(rule, SourceAttackAbility):
            raise ValueError("Retained attack provenance must be explicit.")
        if rule.ability == "fixed":
            if rule.adds_ability_to_damage or attack.attack_ability in ("strength", "dexterity"):
                raise ValueError("Fixed attacks cannot claim a physical ability modifier.")
            delta = 0
            ability = attack.attack_ability
        else:
            if attack.attack_ability not in (None, rule.ability):
                raise ValueError("Attack ability conflicts with source provenance.")
            before = owner.ability_scores.modifier(rule.ability)
            after = form.ability_scores.modifier(rule.ability)
            delta = after - before
            ability = rule.ability
            if delta and rule.adds_ability_to_damage and attack.fixed_damage is not None:
                raise ValueError("Fixed-damage attack needs source-specific damage conversion.")
        result.append(attack.model_copy(update={
            "attack_bonus": attack.attack_bonus + delta,
            "damage_bonus": attack.damage_bonus + (delta if rule.adds_ability_to_damage else 0),
            "attack_ability": ability,
            "attack_ability_modifier": (
                (attack.attack_ability_modifier + delta)
                if delta and attack.attack_ability_modifier is not None
                else attack.attack_ability_modifier
            ),
        }, deep=True))

    by_id = {attack.id: attack for attack in result}
    for attack in gained_attacks:
        if attack.id in by_id:
            if attack != by_id[attack.id]:
                raise ValueError("Form and owner use the same attack ID with different semantics.")
            continue
        copied = attack.model_copy(deep=True)
        result.append(copied)
        by_id[attack.id] = copied
    if len(result) > 64:
        raise ValueError("Combined source attack inventory exceeds the bounded profile limit.")
    return tuple(result)
