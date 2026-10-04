from app.combat.dice import FixedDiceProvider
from app.combat.exile import apply_on_hit_exile, removed_from_battlefield
from app.combat.melee_hit_retaliation import apply_melee_hit_retaliation
from app.combat.persistent_save_zone_cast import cast_save_zone
from app.combat.persistent_save_zone_resolution import resolve_save_zone_trigger
from app.combat.resource_conversion import resolve_resource_conversion
from app.combat.resource_conversion_automation import automatic_resource_conversion
from app.combat.spell_attack_resolution import resolve_spell_attack
from app.combat.state import build_combatant_state
from app.combat.timed_self_buffs import resolve_timed_self_buff
from app.content.arena_map import build_standard_iron_pit_map
from app.content.monsters import build_commoner
from app.content.warlock_fiend_2024_runtime import build_varek_ashenmark_2024
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import GridPosition


def _member(template, combatant_id: str, side: str, position_ft: int) -> EncounterCombatant:
    return EncounterCombatant(
        combatant_id=combatant_id,
        side=side,
        position_ft=position_ft,
        state=build_combatant_state(template),
    )


def _humanoid(combatant_id: str, position_ft: int, *, max_hp: int = 200) -> EncounterCombatant:
    template = build_commoner().model_copy(update={
        "id": f"humanoid-{combatant_id}",
        "creature_type": "humanoid",
        "max_hp": max_hp,
    })
    member = _member(template, combatant_id, "monsters", position_ft)
    member.state.current_hp = max_hp
    return member


def _setup(varek, *enemies):
    return EncounterSetup(
        heroes=[varek],
        monsters=list(enemies),
        hero_total_levels=varek.state.template.level,
        monster_total_cr="0",
        ruleset="2024",
        map_definition=build_standard_iron_pit_map(),
    )


def _place(member, x: int, y: int) -> None:
    member.state.position = GridPosition(x=x, y=y)


def _ids(actions) -> set[str]:
    return {item.id for item in actions}


def test_fiend_damage_spells_bind_at_printed_levels() -> None:
    level5 = build_varek_ashenmark_2024(5)
    level7 = build_varek_ashenmark_2024(7)
    level9 = build_varek_ashenmark_2024(9)
    assert "wall-of-fire" not in _ids(level5.persistent_save_zone_actions)
    assert {"fire-shield-warm", "fire-shield-chill"}.issubset(_ids(level7.timed_self_buff_actions))
    wall = next(item for item in level7.persistent_save_zone_actions if item.id == "wall-of-fire")
    assert (wall.damage_dice_count, wall.damage_dice_size, wall.damage_type, wall.save_triggers) == (
        5, 8, "fire", ["appear"],
    )
    plague = next(item for item in level9.persistent_save_zone_actions if item.id == "insect-plague")
    assert (plague.damage_dice_count, plague.damage_dice_size, plague.damage_type, plague.triggers) == (
        4, 10, "piercing", ["appear", "enter", "end_turn"],
    )


def test_fire_shield_retaliates_on_a_melee_hit() -> None:
    varek = _member(build_varek_ashenmark_2024(7), "varek", "heroes", 0)
    enemy = _humanoid("enemy", 5, max_hp=40)
    setup = _setup(varek, enemy)
    _place(varek, 2, 2)
    _place(enemy, 3, 2)
    warm = next(item for item in varek.state.template.timed_self_buff_actions if item.id == "fire-shield-warm")
    resolve_timed_self_buff(1, 1, varek, warm, setup=setup, turn_key="1:varek")
    applied = apply_melee_hit_retaliation(
        enemy, varek, melee=True, dice=FixedDiceProvider([8, 8]),
        affected_states=[varek.state, enemy.state],
    )
    assert applied == 16
    assert enemy.state.current_hp == 24


def test_wall_of_fire_saves_on_appear_and_deals_full_damage_later() -> None:
    varek = _member(build_varek_ashenmark_2024(7), "varek", "heroes", 0)
    enemy = _humanoid("enemy", 10)
    setup = _setup(varek, enemy)
    _place(varek, 0, 0)
    _place(enemy, 2, 0)
    wall = next(item for item in varek.state.template.persistent_save_zone_actions if item.id == "wall-of-fire")
    events, _ = cast_save_zone(
        1, 1, varek, setup, wall, GridPosition(x=2, y=0), "1:varek",
        FixedDiceProvider([20, 8, 8, 8, 8, 8]),
    )
    appear = next(event for event in events if event.event_type == "saving_throw")
    assert appear.save_succeeded is True
    hp_after_appear = enemy.state.current_hp
    later, _ = resolve_save_zone_trigger(
        3, 1, enemy, setup, setup.save_zones[0], FixedDiceProvider([8, 8, 8, 8, 8]),
        "1:enemy", "end_turn",
    )
    assert later[0].save_succeeded is False
    assert "no save" in later[0].description
    assert enemy.state.current_hp == hp_after_appear - 40


def test_insect_plague_uses_a_constitution_save_on_appear() -> None:
    varek = _member(build_varek_ashenmark_2024(9), "varek", "heroes", 0)
    enemy = _humanoid("enemy", 10)
    setup = _setup(varek, enemy)
    _place(varek, 0, 0)
    _place(enemy, 2, 0)
    plague = next(item for item in varek.state.template.persistent_save_zone_actions if item.id == "insect-plague")
    events, _ = cast_save_zone(
        1, 1, varek, setup, plague, GridPosition(x=2, y=0), "1:varek",
        FixedDiceProvider([1, 10, 10, 10, 10]),
    )
    appear = next(event for event in events if event.event_type == "saving_throw")
    assert appear.save_ability == "constitution"
    assert appear.save_succeeded is False
    assert enemy.state.current_hp == 160


def test_hurl_through_hell_triggers_from_eldritch_blast() -> None:
    varek = _member(build_varek_ashenmark_2024(14), "varek", "heroes", 0)
    varek.state.heroic_inspiration = False
    enemy = _humanoid("enemy", 30)
    setup = _setup(varek, enemy)
    blast = next(item for item in varek.state.template.spell_attack_actions if item.id == "eldritch-blast")
    blast = blast.model_copy(update={"attack_count": 1})

    event = resolve_spell_attack(
        1, 1, varek, enemy, blast, setup, "1:varek",
        FixedDiceProvider([20, 5, 5, 1, 5, 5, 5, 5, 5, 5, 5, 5]),
    )
    assert event.hit is True
    assert removed_from_battlefield(enemy.state) is True
    assert "incapacitated" in enemy.state.active_effect_ids
    hurl = next(item for item in varek.state.resources if item.id == "hurl-through-hell")
    assert hurl.current_uses == 0


def test_hurl_through_hell_restore_spends_a_pact_slot_automatically() -> None:
    varek = _member(build_varek_ashenmark_2024(14), "varek", "heroes", 0)
    hurl = next(item for item in varek.state.resources if item.id == "hurl-through-hell")
    pact = next(item for item in varek.state.resources if item.id.startswith("spell-slot-"))
    hurl.current_uses = 0
    before_pact = pact.current_uses

    action = automatic_resource_conversion(varek.state, "1:varek")
    assert action is not None
    assert action.id == "hurl-through-hell-restore"
    assert action.automation == "when-target-empty"

    event = resolve_resource_conversion(
        varek.state, action, sequence=1, round_number=1, actor_id="varek", turn_key="1:varek",
    )
    assert event is not None
    assert hurl.current_uses == 1
    assert pact.current_uses == before_pact - 1


def test_hurl_through_hell_accepts_a_spell_attack_hit() -> None:
    varek = _member(build_varek_ashenmark_2024(14), "varek", "heroes", 0)
    enemy = _humanoid("enemy", 5)
    applied = apply_on_hit_exile(
        varek.state,
        enemy.state,
        None,
        attacker_id="varek",
        round_number=1,
        affected_states=[varek.state, enemy.state],
        dice=FixedDiceProvider([1, 5, 5, 5, 5, 5, 5, 5, 5]),
        turn_key="1:varek",
    )
    assert applied == ("banished", 0)
    assert removed_from_battlefield(enemy.state) is True
