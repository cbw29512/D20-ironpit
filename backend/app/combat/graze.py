from __future__ import annotations

import logging

from app.combat.damage_defenses import adjusted_damage_amount
from app.combat.dice import DiceProvider
from app.combat.zero_hp import ZeroHpOutcome, apply_damage
from app.domain.models import CombatantState, DamageRollComponent, DiceRoll, WeaponAttack

logger = logging.getLogger(__name__)
GrazeResolution = tuple[DiceRoll, list[DamageRollComponent], ZeroHpOutcome]


def graze_mastery_active(attacker: CombatantState, attack: WeaponAttack) -> bool:
    return (
        attack.weapon.mastery_property == "Graze"
        and attack.weapon.id in attacker.template.weapon_masteries
    )


def resolve_graze_miss(
    attacker: CombatantState,
    defender: CombatantState,
    attack: WeaponAttack,
    dice: DiceProvider,
    affected_states: list[CombatantState] | None = None,
) -> GrazeResolution | None:
    """Resolve strict RAW Graze fixed damage after a mastered weapon misses."""
    try:
        if not graze_mastery_active(attacker, attack):
            return None
        modifier = attack.attack_ability_modifier
        if modifier is None:
            raise ValueError(
                f"Graze attack {attack.id!r} requires an explicit attack ability modifier."
            )
        raw_damage = max(0, modifier)
        component = DamageRollComponent(
            source=f"{attack.weapon.name} (Graze)",
            notation=str(raw_damage),
            rolls=[],
            modifier=0,
            damage_type=attack.weapon.damage_type,
            total=raw_damage,
        )
        applied = adjusted_damage_amount(
            raw_damage,
            attack.weapon.damage_type,
            defender,
            allow_vulnerability=False,
        )
        applied_component = component.model_copy(update={"applied_total": applied})
        roll = DiceRoll(notation=str(raw_damage), rolls=[], modifier=0, total=applied)
        damage_types = {attack.weapon.damage_type} if applied > 0 else set()
        outcome = apply_damage(
            defender,
            applied,
            critical=False,
            damage_types=damage_types,
            dice=dice,
            affected_states=affected_states,
        )
        return roll, [applied_component], outcome
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Graze resolution failed for %s.", attacker.template.name)
        raise RuntimeError("Graze mastery could not be resolved.") from exc
