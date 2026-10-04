from app.combat.dice import FixedDiceProvider
from app.combat.melee_hit_save_retaliation import apply_melee_hit_save_retaliation
from app.combat.state import build_combatant_state
from app.combat.timed_self_buffs import resolve_timed_self_buff
from app.content.arena_map import build_standard_iron_pit_map
from app.combat.concentration import end_concentration
from app.content.audited_cleric import build_seraphine_dawnshield_level
from app.content.shared_holy_aura_2024 import holy_aura_2014
from app.content.audited_fighter import build_karnok_stoneward
from app.content.monsters import build_commoner
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import GridPosition


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


def _aura_setup(*, attacker_type: str, ax: int = 5, ay: int = 7):
    cleric = _member(build_seraphine_dawnshield_level(15), "cleric", "heroes", 4, 7)
    ally = _member(build_karnok_stoneward(), "ally", "heroes", 5, 7)
    enemy = _member(
        build_commoner().model_copy(update={"creature_type": attacker_type, "max_hp": 40}),
        "enemy",
        "monsters",
        ax,
        ay,
    )
    setup = _setup([cleric, ally], [enemy])
    aura = next(item for item in cleric.state.template.timed_self_buff_actions if item.id == "holy-aura")
    resolve_timed_self_buff(1, 1, cleric, aura, setup=setup, turn_key="1:cleric")
    return cleric, ally, enemy, setup, aura


def test_holy_aura_binds_the_printed_fiend_undead_blind_rider() -> None:
    cleric = build_seraphine_dawnshield_level(15)
    aura = next(item for item in cleric.timed_self_buff_actions if item.id == "holy-aura")
    rider = aura.friendly_save_advantage_aura.melee_hit_save_retaliation
    assert rider is not None
    assert rider.attacker_creature_types == ["fiend", "undead"]
    assert rider.save_ability == "constitution"
    assert rider.condition_id == "blinded"
    assert rider.expiry_timing == "target_turn_end"


def test_holy_aura_blinds_a_fiend_that_fails_the_melee_save() -> None:
    _cleric, ally, enemy, setup, _aura = _aura_setup(attacker_type="fiend")
    applied = apply_melee_hit_save_retaliation(
        enemy, ally, melee=True, dice=FixedDiceProvider([1]), setup=setup, round_number=1,
        affected_states=[item.state for item in [*setup.heroes, *setup.monsters]],
    )
    assert applied == "blinded"
    assert "blinded" in enemy.state.active_effect_ids
    effect = next(item for item in enemy.state.timed_effects if item.effect_id == "blinded")
    assert effect.expiry_timing == "target_turn_end"
    assert effect.expires_round == 2


def test_holy_aura_does_not_blind_on_a_successful_save() -> None:
    _cleric, ally, enemy, setup, _aura = _aura_setup(attacker_type="undead")
    applied = apply_melee_hit_save_retaliation(
        enemy, ally, melee=True, dice=FixedDiceProvider([20]), setup=setup, round_number=1,
    )
    assert applied is None
    assert "blinded" not in enemy.state.active_effect_ids


def test_holy_aura_ignores_non_fiend_and_ranged_hits() -> None:
    _cleric, ally, humanoid, setup, _aura = _aura_setup(attacker_type="humanoid")
    assert apply_melee_hit_save_retaliation(
        humanoid, ally, melee=True, dice=FixedDiceProvider([1]), setup=setup, round_number=1,
    ) is None
    _cleric, ally, fiend, setup, _aura = _aura_setup(attacker_type="fiend")
    assert apply_melee_hit_save_retaliation(
        fiend, ally, melee=False, dice=FixedDiceProvider([1]), setup=setup, round_number=1,
    ) is None


def test_holy_aura_requires_the_defender_to_be_inside_the_emanation() -> None:
    cleric, _ally, enemy, setup, _aura = _aura_setup(attacker_type="fiend")
    far = _member(build_karnok_stoneward(), "far", "heroes", 20, 7)
    setup.heroes.append(far)
    assert apply_melee_hit_save_retaliation(
        enemy, far, melee=True, dice=FixedDiceProvider([1]), setup=setup, round_number=1,
    ) is None
    assert "blinded" not in enemy.state.active_effect_ids
    assert cleric.state.timed_effects


def test_holy_aura_2014_blind_ends_when_the_spell_ends() -> None:
    cleric = _member(build_seraphine_dawnshield_level(15), "cleric", "heroes", 4, 7)
    cleric.state.template.timed_self_buff_actions = [holy_aura_2014(18)]
    ally = _member(build_karnok_stoneward(), "ally", "heroes", 5, 7)
    enemy = _member(
        build_commoner().model_copy(update={"creature_type": "fiend", "max_hp": 40}),
        "enemy",
        "monsters",
        5,
        7,
    )
    setup = _setup([cleric, ally], [enemy])
    aura = cleric.state.template.timed_self_buff_actions[0]
    assert aura.friendly_save_advantage_aura.melee_hit_save_retaliation.bind_to_source_effect is True
    resolve_timed_self_buff(1, 1, cleric, aura, setup=setup, turn_key="1:cleric")
    applied = apply_melee_hit_save_retaliation(
        enemy, ally, melee=True, dice=FixedDiceProvider([1]), setup=setup, round_number=1,
        affected_states=[item.state for item in [*setup.heroes, *setup.monsters]],
    )
    assert applied == "blinded"
    end_concentration(cleric.state, [cleric.state, ally.state, enemy.state])
    assert "blinded" not in enemy.state.active_effect_ids
