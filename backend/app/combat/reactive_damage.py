from __future__ import annotations

from app.combat.damage_defenses import apply_damage_defenses
from app.combat.dice import DiceProvider
from app.combat.zero_hp import apply_damage
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent, DamageRollComponent, DiceRoll, WeaponAttack, WeaponAttackKind


def apply_melee_hit_reactive_damage(
    event: BattleEvent,
    attacker: EncounterCombatant,
    defender: EncounterCombatant,
    attack: WeaponAttack,
    distance_ft: int,
    dice: DiceProvider,
    setup: EncounterSetup | None,
) -> None:
    if not event.hit or attack.weapon.attack_kind is not WeaponAttackKind.MELEE:
        return
    rules = [*defender.state.template.melee_hit_reactive_damage, *defender.state.temporary_melee_hit_reactive_damage]
    profiles = [rule for rule in rules if distance_ft <= rule.range_ft]
    if not profiles or attacker.state.is_dead:
        return
    event.actor_hp_before = attacker.state.current_hp
    all_rolls: list[int] = []; total_modifier = 0; total_applied = 0; notation: list[str] = []
    affected = [member.state for member in [*setup.heroes, *setup.monsters]] if setup is not None else None
    for rule in profiles:
        rolls = [dice.roll(rule.dice_size) for _ in range(rule.dice_count)]
        raw = max(0, sum(rolls) + rule.damage_bonus)
        component = DamageRollComponent(
            source=rule.id, notation=f"{rule.dice_count}d{rule.dice_size}+{rule.damage_bonus}",
            rolls=rolls, modifier=rule.damage_bonus, damage_type=rule.damage_type, total=raw,
        )
        applied, adjusted = apply_damage_defenses(attacker.state, [component])
        event.reactive_damage_components.extend(adjusted)
        if applied:
            apply_damage(attacker.state, applied, damage_types={rule.damage_type}, dice=dice, affected_states=affected)
        all_rolls.extend(rolls); total_modifier += rule.damage_bonus; total_applied += applied
        notation.append(component.notation)
    event.actor_hp_after = attacker.state.current_hp
    event.reactive_damage_roll = DiceRoll(
        notation=" + ".join(notation), rolls=all_rolls, modifier=total_modifier, total=total_applied,
    )
    event.description += (
        f" {defender.state.template.name}'s reactive damage deals {total_applied} damage to "
        f"{attacker.state.template.name}."
    )
