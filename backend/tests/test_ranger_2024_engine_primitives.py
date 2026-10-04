from __future__ import annotations

from app.combat.damage_defenses import apply_damage_defenses
from app.combat.dice import FixedDiceProvider
from app.combat.healing_resolution_support import resolve_healing_amount
from app.combat.incoming_damage_resistance import expire_current_turn_type_resistances
from app.combat.precise_hunter import marked_target_advantage_sources
from app.combat.state import build_combatant_state
from app.content.monsters import build_commoner
from app.content.ranger_hunter_2024_runtime import build_rowan_ashtrail_2024
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import DamageRollComponent, DamageType
from app.domain.modifiers import CombatModifier, ModifierKind


def _member(template, combatant_id: str, side: str) -> EncounterCombatant:
    return EncounterCombatant(
        combatant_id=combatant_id,
        side=side,
        position_ft=0,
        state=build_combatant_state(template),
    )


def test_superior_defense_resists_triggering_damage_type() -> None:
    rowan = _member(build_rowan_ashtrail_2024(15), "rowan", "heroes")
    monster = _member(build_commoner(), "commoner", "monsters")
    components = [DamageRollComponent(
        source="claw", notation="8", rolls=[], modifier=0,
        damage_type=DamageType.SLASHING, total=8,
    )]
    applied, adjusted = apply_damage_defenses(rowan.state, components)
    assert rowan.state.reaction_available is False
    assert applied == 4
    assert adjusted[0].applied_total == 4
    expire_current_turn_type_resistances(EncounterSetup(
        heroes=[rowan],
        monsters=[monster],
        hero_total_levels=15,
        monster_total_cr="0",
        ruleset="2024",
    ))
    assert not any(
        effect.effect_id == "incoming-damage-type-resistance"
        for effect in rowan.state.timed_effects
    )


def test_precise_hunter_advantages_marked_target() -> None:
    rowan = build_combatant_state(build_rowan_ashtrail_2024(17))
    rowan.active_modifiers.append(CombatModifier(
        id="mark",
        source_id="rowan",
        source_effect_id="hunters-mark",
        source_name="Hunter's Mark",
        kind=ModifierKind.BONUS_DAMAGE,
        target_id="wolf",
        dice_count=1,
        dice_size=6,
        damage_type=DamageType.FORCE,
    ))
    assert marked_target_advantage_sources(rowan, "wolf") == 1
    assert marked_target_advantage_sources(rowan, "other") == 0


def test_tireless_grants_temporary_hp() -> None:
    rowan = _member(build_rowan_ashtrail_2024(10), "rowan", "heroes")
    action = next(item for item in rowan.state.template.healing_actions if item.id == "tireless")
    assert action.grants_temporary_hp is True
    _rolls, _total, healed, _notation, _bonus = resolve_healing_amount(
        rowan, rowan, action, FixedDiceProvider([8]),
    )
    assert healed == 8 + action.healing_bonus
    assert rowan.state.temporary_hp == healed
    assert rowan.state.current_hp == rowan.state.template.max_hp
