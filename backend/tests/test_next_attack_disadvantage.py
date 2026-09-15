from app.combat.attacks import resolve_attack
from app.combat.attack_roll_modifiers import next_attack_disadvantage_sources
from app.combat.dice import FixedDiceProvider
from app.combat.hit_modifiers import apply_modifier_effect
from app.combat.state import build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.domain.hit_modifiers import CombatModifierEffect


def test_next_attack_disadvantage_is_source_neutral_and_consumed() -> None:
    attacker = build_combatant_state(build_karnok_stoneward().model_copy(deep=True))
    defender = build_combatant_state(build_karnok_stoneward().model_copy(deep=True))
    apply_modifier_effect(
        attacker,
        "generic-source",
        "generic-effect",
        CombatModifierEffect(kind="next-attack-disadvantage", expires_at_end_of_target_turn=True),
        0,
        trigger="hit",
    )
    assert next_attack_disadvantage_sources(attacker) == 1

    event = resolve_attack(
        1,
        1,
        attacker,
        defender,
        attacker.template.weapon_attack,
        5,
        FixedDiceProvider([18, 5, 1]),
        actor_event_id="attacker",
        target_event_id="defender",
        spend_action=False,
    )

    assert event.attack_roll is not None
    assert event.attack_roll.mode.value == "disadvantage"
    assert next_attack_disadvantage_sources(attacker) == 0
