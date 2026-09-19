from app.combat.attacks import resolve_attack
from app.combat.death_saves import resolve_death_save
from app.combat.dice import FixedDiceProvider
from app.combat.state import begin_turn, build_combatant_state
from app.content.json_hero_runtime import compile_json_hero_template
from app.content.monsters import build_commoner


def _karnok(level: int):
    return build_combatant_state(compile_json_hero_template("2024", "karnok-stoneward", level))


def test_2024_heroic_rally_heals_only_while_alive_and_at_or_below_half_hp() -> None:
    state = _karnok(18)
    half = state.template.max_hp // 2
    state.current_hp = half
    begin_turn(state)
    assert state.current_hp == min(state.template.max_hp, half + 10)

    state.current_hp = half + 1
    begin_turn(state)
    assert state.current_hp == half + 1

    state.current_hp = 0
    begin_turn(state)
    assert state.current_hp == 0


def test_2024_defy_death_treats_eighteen_as_natural_twenty() -> None:
    state = _karnok(18)
    state.current_hp = 0
    state.is_unconscious = True
    event = resolve_death_save(1, 1, state.template.id, state, FixedDiceProvider([18, 3]))
    assert event.event_type == "death_save"
    assert event.death_save_roll is not None
    assert event.death_save_roll.mode.value == "advantage"
    assert state.current_hp == 1
    assert "regains 1 HP" in event.description


def _dummy():
    return build_combatant_state(build_commoner().model_copy(update={"armor_class": 30, "max_hp": 100}))


def test_peerless_aim_converts_one_miss_per_turn_and_logs_it() -> None:
    attacker = _karnok(19)
    defender = _dummy()
    miss = resolve_attack(
        1, 1, attacker, defender, attacker.template.weapon_attack,
        5, FixedDiceProvider([2, 4, 5, 4, 5]), turn_key="1:karnok",
    )
    assert miss.hit is True
    assert "Boon of Combat Prowess turns the miss into a hit" in miss.description

    second = resolve_attack(
        2, 1, attacker, defender, attacker.template.weapon_attack,
        5, FixedDiceProvider([2, 4, 5]), turn_key="1:karnok", spend_action=False,
    )
    assert second.hit is False


def test_peerless_aim_does_not_override_iron_pit_natural_1() -> None:
    attacker = _karnok(19)
    defender = _dummy()
    event = resolve_attack(
        1, 1, attacker, defender, attacker.template.weapon_attack,
        5, FixedDiceProvider([1]), turn_key="1:karnok",
    )
    assert event.hit is False
    assert event.turn_terminated is True
    assert "Boon of Combat Prowess" not in event.description
