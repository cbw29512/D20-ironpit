from __future__ import annotations

from app.combat.attack_effect_resolution import resolve_attack_effects
from app.combat.dice import FixedDiceProvider
from app.combat.friendly_save_auras import sync_friendly_save_auras
from app.combat.restoration_riders import apply_hit_point_maximum_reduction
from app.combat.start_of_turn_save_condition_events import (
    resolve_start_of_turn_save_condition_damage_events,
)
from app.combat.state import begin_turn, build_combatant_state
from app.combat.timed_self_buffs import resolve_timed_self_buff
from app.content.arena_map import build_standard_iron_pit_map
from app.content.audited_cleric import build_seraphine_dawnshield_level
from app.content.monsters import build_commoner
from app.content.paladin_devotion_2024_runtime import build_aurelia_brightshield_2024
from app.content.shared_recovery_auras_2024 import (
    aura_of_life_2024,
    aura_of_vitality_2024,
    crusaders_mantle_2024,
)
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import GridPosition
from app.domain.models import RollMode


def _member(template, combatant_id: str, side: str, x: int, y: int) -> EncounterCombatant:
    member = EncounterCombatant(
        combatant_id=combatant_id,
        side=side,
        position_ft=abs(x) * 5,
        state=build_combatant_state(template),
    )
    member.state.position = GridPosition(x=x, y=y)
    return member


def _setup(heroes, monsters) -> EncounterSetup:
    return EncounterSetup(
        heroes=heroes,
        monsters=monsters,
        hero_total_levels=sum((item.state.template.level or 1) for item in heroes),
        monster_total_cr="0",
        ruleset="2024",
        map_definition=build_standard_iron_pit_map(),
    )


def test_printed_recovery_auras_are_not_pit_bans_and_bind() -> None:
    mantle = crusaders_mantle_2024()
    vitality = aura_of_vitality_2024()
    life = aura_of_life_2024()
    assert mantle.friendly_weapon_damage_aura is not None
    assert (mantle.friendly_weapon_damage_aura.dice_count, mantle.friendly_weapon_damage_aura.dice_size) == (1, 4)
    assert vitality.friendly_recovery_aura is not None
    assert vitality.friendly_recovery_aura.heal_on_create is True
    assert life.friendly_recovery_aura is not None
    assert life.friendly_recovery_aura.zero_hp_ally_start_heal == 1
    aurelia = build_aurelia_brightshield_2024(15)
    ids = {item.id for item in aurelia.timed_self_buff_actions}
    assert {"aura-of-vitality", "crusaders-mantle", "aura-of-life"} <= ids
    cleric = build_seraphine_dawnshield_level(7)
    assert any(item.id == "aura-of-life" for item in cleric.timed_self_buff_actions)


def test_crusaders_mantle_adds_printed_radiant_on_weapon_hits() -> None:
    template = build_aurelia_brightshield_2024(11)
    template = template.model_copy(update={
        "progression_features": template.progression_features.model_copy(update={
            "resource_backed_post_hit_damage": None,
            "post_hit_spell_options": [],
        }),
    })
    hero = _member(template, "aurelia", "heroes", 4, 7)
    enemy = _member(build_commoner().model_copy(update={"max_hp": 40}, deep=True), "enemy", "monsters", 5, 7)
    setup = _setup([hero], [enemy])
    begin_turn(hero.state)
    resolve_timed_self_buff(
        1, 1, hero, crusaders_mantle_2024(), setup=setup, turn_key="1:aurelia",
    )
    sync_friendly_save_auras(setup)
    hero.state.feature_last_turn_keys["savage-attacker"] = "1:aurelia"
    before = enemy.state.current_hp
    resolve_attack_effects(
        hero.state, enemy.state, hero.state.template.weapon_attack,
        FixedDiceProvider([8, 8, 4]),
        hit=True, critical=False, mode=RollMode.NORMAL, round_number=1,
        attacker_event_id=hero.combatant_id, defender_event_id=enemy.combatant_id,
        actual_event_id=enemy.combatant_id, turn_key="1:aurelia", bonus_damage=None,
        affected_states=[hero.state, enemy.state], sneak_attack_ally_available=False,
        brutal_strike_disadvantage=0, setup=setup,
    )
    expected = 8 + hero.state.template.weapon_attack.damage_bonus + 8 + 4
    assert enemy.state.current_hp == before - expected


def test_aura_of_vitality_heals_on_create_and_source_turn_start() -> None:
    hero = _member(build_aurelia_brightshield_2024(9), "aurelia", "heroes", 4, 7)
    ally_template = build_commoner().model_copy(update={"max_hp": 20, "kind": "character"}, deep=True)
    ally = _member(ally_template, "ally", "heroes", 5, 7)
    enemy = _member(build_commoner(), "enemy", "monsters", 8, 7)
    setup = _setup([hero, ally], [enemy])
    ally.state.current_hp = 4
    begin_turn(hero.state)
    resolve_timed_self_buff(
        1, 1, hero, aura_of_vitality_2024(), setup=setup, turn_key="1:aurelia",
        dice=FixedDiceProvider([6, 5]),
    )
    assert ally.state.current_hp == 15
    ally.state.current_hp = 2
    resolve_start_of_turn_save_condition_damage_events(
        2, 2, hero, setup, FixedDiceProvider([4, 3]),
    )
    assert ally.state.current_hp == 9


def test_aura_of_life_locks_hp_max_resists_necrotic_and_revives_zero_hp_ally() -> None:
    hero = _member(build_aurelia_brightshield_2024(15), "aurelia", "heroes", 4, 7)
    ally_template = build_commoner().model_copy(update={"max_hp": 16, "kind": "character"}, deep=True)
    ally = _member(ally_template, "ally", "heroes", 5, 7)
    enemy = _member(build_commoner(), "enemy", "monsters", 8, 7)
    setup = _setup([hero, ally], [enemy])
    begin_turn(hero.state)
    resolve_timed_self_buff(
        1, 1, hero, aura_of_life_2024(), setup=setup, turn_key="1:aurelia",
    )
    sync_friendly_save_auras(setup)
    assert apply_hit_point_maximum_reduction(ally, 8) == 0
    assert ally.state.hit_point_maximum_reduction == 0
    from app.combat.damage_defenses import apply_damage_defenses
    from app.domain.models import DamageRollComponent, DamageType
    component = DamageRollComponent(
        source="test", notation="10", rolls=[], modifier=0,
        damage_type=DamageType.NECROTIC, total=10,
    )
    applied, _adjusted = apply_damage_defenses(hero.state, [component])
    assert applied == 5
    ally.state.current_hp = 0
    ally.state.is_unconscious = True
    resolve_start_of_turn_save_condition_damage_events(2, 2, ally, setup, FixedDiceProvider([1]))
    assert ally.state.current_hp == 1
    assert ally.state.is_unconscious is False
