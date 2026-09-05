from app.combat.attacks import resolve_attack
from app.combat.dice import FixedDiceProvider
from app.combat.hit_modifiers import apply_hit_modifier_effects
from app.combat.modifier_stack import expire_target_turn_modifiers
from app.combat.state import build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.content.monster_worg import build_worg
from app.domain.hit_modifiers import HitModifierEffect
from app.domain.modifiers import ModifierKind


def _disadvantage_bite():
    bite = build_worg().weapon_attack
    return bite.model_copy(update={
        "on_hit_modifier_effects": [
            HitModifierEffect(kind="next-attack-disadvantage", expires_at_end_of_target_turn=True)
        ]
    })


def test_generic_next_attack_disadvantage_is_consumed_by_next_attack_roll() -> None:
    source = build_combatant_state(build_worg())
    target = build_combatant_state(build_karnok_stoneward().model_copy(deep=True))
    attack = _disadvantage_bite()
    hit = resolve_attack(
        1, 1, source, target, attack, 5, FixedDiceProvider([15, 1]),
        actor_event_id="source", target_event_id="target", spend_action=False,
    )
    assert hit.hit is True
    assert len(target.active_modifiers) == 1
    assert target.active_modifiers[0].kind is ModifierKind.NEXT_ATTACK_DISADVANTAGE

    follow_up = resolve_attack(
        2, 1, target, source, target.template.weapon_attack, 5, FixedDiceProvider([5, 15]),
        actor_event_id="target", target_event_id="source", spend_action=False,
    )
    assert follow_up.attack_roll is not None and follow_up.attack_roll.mode.value == "disadvantage"
    assert target.active_modifiers == []


def test_unused_next_attack_disadvantage_expires_at_target_turn_end() -> None:
    target = build_combatant_state(build_karnok_stoneward().model_copy(deep=True))
    apply_hit_modifier_effects(target, "source", _disadvantage_bite())
    assert len(target.active_modifiers) == 1
    assert expire_target_turn_modifiers(target) == 1
    assert target.active_modifiers == []
