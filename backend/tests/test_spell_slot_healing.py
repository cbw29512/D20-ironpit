from app.combat.dice import FixedDiceProvider
from app.combat.healing import choose_healing_action, resolve_healing
from app.combat.spell_attack_policy import choose_spell_attack
from app.combat.spell_policy import choose_spell
from app.combat.state import build_combatant_state
from app.content.audited_cleric import build_seraphine_dawnshield
from app.content.audited_fighter import build_karnok_stoneward
from app.content.healing_spell_effects import build_healing_word
from app.domain.encounters import EncounterCombatant, EncounterSetup


def _member(template, combatant_id: str, side: str, position_ft: int) -> EncounterCombatant:
    return EncounterCombatant(
        combatant_id=combatant_id, side=side, position_ft=position_ft,
        state=build_combatant_state(template.model_copy(deep=True)),
    )


def _setup() -> tuple[EncounterSetup, EncounterCombatant, EncounterCombatant]:
    cleric_template = build_seraphine_dawnshield()
    cleric_template.healing_actions.append(build_healing_word(3))
    caster = _member(cleric_template, "cleric", "heroes", 0)
    ally = _member(build_karnok_stoneward(), "ally", "heroes", 5)
    enemy = _member(build_karnok_stoneward(), "enemy", "monsters", 10)
    ally.state.current_hp = 1
    setup = EncounterSetup(
        heroes=[caster, ally], monsters=[enemy], hero_total_levels=2, monster_total_cr="1",
    )
    return setup, caster, ally


def test_healing_word_marks_slot_turn_and_allows_only_cantrip_afterward() -> None:
    setup, caster, ally = _setup()
    turn_key = "1:cleric"
    choice = choose_healing_action(caster, setup, turn_key)
    assert choice is not None
    action, target = choice
    assert action.id == "healing-word" and target is ally
    assert action.action_cost == "bonus_action" and action.range_ft == 60
    assert (action.dice_count, action.dice_size, action.healing_bonus) == (2, 4, 3)

    event = resolve_healing(1, 1, caster, ally, action, FixedDiceProvider([4, 3]), turn_key)
    assert event.healing_roll is not None and event.healing_roll.total == 10
    assert caster.state.bonus_action_available is False
    assert caster.state.action_available is True
    assert caster.state.spell_slot_expended_turn_key == turn_key
    assert choose_spell_attack(caster, setup, turn_key) is None
    cantrip = choose_spell(caster, setup, turn_key)
    assert cantrip is not None and cantrip.action.id == "sacred-flame" and cantrip.slot_level == 0


def test_prior_leveled_spell_blocks_healing_word_same_turn() -> None:
    setup, caster, _ = _setup()
    turn_key = "1:cleric"
    caster.state.spell_slot_expended_turn_key = turn_key
    assert choose_healing_action(caster, setup, turn_key) is None


def test_healing_word_fails_closed_without_active_turn_key() -> None:
    setup, caster, _ = _setup()
    assert choose_healing_action(caster, setup) is None
