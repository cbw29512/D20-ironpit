"""Pure source-neutral expansion of weapon-hit traits to gained form weapons.

This is a capability compiler, NOT another damage resolver. The existing
OnHitDamage and MAGICAL qualifier primitives remain authoritative in combat.
"""
from __future__ import annotations

from collections.abc import Sequence

from app.domain.models import CombatantTemplate, WeaponAttack
from app.domain.weapons import OnHitDamage
from app.domain.damage_sources import DamageSourceQualifier


def inherit_weapon_hit_trait_for_form(
    original: CombatantTemplate,
    form: CombatantTemplate,
    compiled_attacks: Sequence[WeaponAttack],
    *,
    inherited_rider: OnHitDamage,
    magical_weapons: bool,
) -> tuple[WeaponAttack, ...]:
    """Apply one source-validated owner trait to *gained* form weapon hits.

    Source attacks already include their printed effects, so existing owner
    attacks are retained untouched. Do not claim a live Change Shape action.
    """
    if original.kind != "monster" or form.kind != "monster" or original.ruleset != form.ruleset:
        raise ValueError("Inherited weapon trait requires same-edition monster sources.")
    if not inherited_rider.source or inherited_rider.dice_count <= 0:
        raise ValueError("Weapon-hit rider needs explicit nonempty source and rolled damage.")
    owner_ids = {attack.id for attack in [original.weapon_attack, *original.alternate_weapon_attacks]}
    gained_ids = {attack.id for attack in [form.weapon_attack, *form.alternate_weapon_attacks]}
    if owner_ids & gained_ids:
        raise ValueError("Owner and acquired form weapon IDs must not collide.")
    by_id = {attack.id: attack for attack in compiled_attacks}
    if len(by_id) != len(compiled_attacks) or set(by_id) != owner_ids | gained_ids:
        raise ValueError("Source-validated owner and form attack inventory required.")

    result = []
    for attack in compiled_attacks:
        if attack.id in owner_ids:
            result.append(attack.model_copy(deep=True))
            continue
        source_matched = [row for row in attack.on_hit_damage if row.source == inherited_rider.source]
        if source_matched and source_matched != [inherited_rider]:
            raise ValueError("Existing weapon-hit source conflicts with inherited trait.")
        riders = list(attack.on_hit_damage)
        if not source_matched:
            riders.append(inherited_rider.model_copy(deep=True))
        qualifiers = list(attack.damage_source_qualifiers)
        if magical_weapons and DamageSourceQualifier.MAGICAL not in qualifiers:
            qualifiers.append(DamageSourceQualifier.MAGICAL)
        result.append(attack.model_copy(update={
            "on_hit_damage": riders,
            "damage_source_qualifiers": qualifiers,
        }, deep=True))
    return tuple(result)
