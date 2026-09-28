from __future__ import annotations

from app.combat.attacks import resolve_attack
from app.combat.dice import FixedDiceProvider
from app.combat.incoming_attack_bonus import next_incoming_attack_roll_flat_bonus
from app.combat.modifier_stack import add_modifier
from app.combat.state import build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.domain.modifiers import CombatModifier, ModifierKind


def _state():
    return build_combatant_state(build_karnok_stoneward().model_copy(deep=True))


def test_next_incoming_attack_bonus_excludes_source_then_consumes_for_other_attacker() -> None:
    source = _state()
    ally = _state()
    target = _state()
    add_modifier(target, CombatModifier(
        id="source:sundering:target",
        source_id="source",
        source_effect_id="sundering-blow",
        source_name="Sundering Blow",
        kind=ModifierKind.NEXT_INCOMING_ATTACK_ROLL_FLAT,
        flat_bonus=5,
        expires_at_start_of_source_turn=True,
    ))

    assert next_incoming_attack_roll_flat_bonus(target, "source") == 0
    assert next_incoming_attack_roll_flat_bonus(target, "ally") == 5

    source_event = resolve_attack(
        1, 1, source, target, source.template.weapon_attack, 5,
        FixedDiceProvider([8]),
        actor_event_id="source", target_event_id="target", spend_action=False,
    )
    assert source_event.hit is False
    assert next_incoming_attack_roll_flat_bonus(target, "ally") == 5

    ally_event = resolve_attack(
        2, 1, ally, target, ally.template.weapon_attack, 5,
        FixedDiceProvider([8, 4]),
        actor_event_id="ally", target_event_id="target", spend_action=False,
    )
    assert ally_event.attack_roll is not None
    assert ally_event.attack_roll.modifier == ally.template.weapon_attack.attack_bonus + 5
    assert ally_event.hit is True
    assert next_incoming_attack_roll_flat_bonus(target, "ally") == 0


def test_next_incoming_attack_bonus_requires_nonzero_flat_bonus() -> None:
    try:
        CombatModifier(
            id="bad",
            source_id="source",
            source_effect_id="effect",
            kind=ModifierKind.NEXT_INCOMING_ATTACK_ROLL_FLAT,
        )
    except ValueError:
        return
    raise AssertionError("next incoming attack-roll modifiers must reject a zero bonus")
