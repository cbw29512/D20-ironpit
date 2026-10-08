from __future__ import annotations

from app.combat.selectable_damage_resistance import score_enemy_damage_types
from app.combat.state import build_combatant_state
from app.content.monsters import build_commoner
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import DamageType, OnHitDamage, Weapon, WeaponAttack, WeaponAttackKind


def _member(name: str, side: str) -> EncounterCombatant:
    template = build_commoner().model_copy(update={"id": name, "name": name, "ruleset": "2014"})
    return EncounterCombatant(
        combatant_id=name, side=side, position_ft=0 if side == "heroes" else 40,
        state=build_combatant_state(template),
    )


def test_off_type_weapon_fire_rider_is_counted_as_incoming_fire_threat() -> None:
    caster, enemy = _member("caster", "heroes"), _member("enemy", "monsters")
    attack = WeaponAttack(
        id="mixed-slash",
        weapon=Weapon(
            id="slash", name="Slash", attack_kind=WeaponAttackKind.MELEE,
            dice_count=1, dice_size=8, damage_type=DamageType.SLASHING,
            reach_ft=5, animation="slash",
        ),
        attack_bonus=4,
        on_hit_damage=[OnHitDamage(
            source="Burning", dice_count=3, dice_size=6, damage_type=DamageType.FIRE,
        )],
    )
    enemy.state.template = enemy.state.template.model_copy(update={"weapon_attack": attack})
    setup = EncounterSetup(
        heroes=[caster], monsters=[enemy], hero_total_levels=1,
        monster_total_cr="0", ruleset="2014",
    )
    scores = score_enemy_damage_types(caster, setup, [DamageType.FIRE, DamageType.COLD])
    assert scores[DamageType.FIRE] == 10.5
    assert scores[DamageType.COLD] == 0
