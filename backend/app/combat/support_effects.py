from __future__ import annotations

from app.combat.dice import DiceProvider
from app.domain.models import BattleEvent, CombatantState, EncounterCombatant, EncounterSetup, TimedEffect

BLESS_EFFECT_ID = "bless"
SANCTUARY_EFFECT_ID = "sanctuary"


def has_support_effect(state: CombatantState, effect_id: str) -> bool:
    return any(effect.effect_id == effect_id for effect in state.timed_effects)


def bless_bonus(state: CombatantState, dice: DiceProvider) -> int:
    return dice.roll(4) if has_support_effect(state, BLESS_EFFECT_ID) else 0


def sanctuary_dc(state: CombatantState) -> int | None:
    effect = next((item for item in state.timed_effects if item.effect_id == SANCTUARY_EFFECT_ID), None)
    return effect.value if effect is not None else None


def end_sanctuary(state: CombatantState) -> bool:
    before = len(state.timed_effects)
    state.timed_effects = [item for item in state.timed_effects if item.effect_id != SANCTUARY_EFFECT_ID]
    return len(state.timed_effects) != before


def apply_support_effect(
    state: CombatantState,
    effect_id: str,
    source_id: str,
    expires_round: int,
    *,
    concentration: bool = False,
    value: int | None = None,
) -> None:
    state.timed_effects = [
        item for item in state.timed_effects
        if not (item.effect_id == effect_id and item.source_id == source_id)
    ]
    state.timed_effects.append(TimedEffect(
        effect_id=effect_id,
        source_id=source_id,
        expires_at_start_of_source_turn=False,
        expires_round=expires_round,
        concentration=concentration,
        value=value,
    ))


def break_concentration(source_id: str, setup: EncounterSetup) -> list[str]:
    removed: list[str] = []
    for member in [*setup.heroes, *setup.monsters]:
        ending = [item for item in member.state.timed_effects if item.source_id == source_id and item.concentration]
        removed.extend(item.effect_id for item in ending)
        member.state.timed_effects = [item for item in member.state.timed_effects if item not in ending]
    return removed


def concentrating(source_id: str, setup: EncounterSetup) -> bool:
    return any(
        item.source_id == source_id and item.concentration
        for member in [*setup.heroes, *setup.monsters]
        for item in member.state.timed_effects
    )


def expire_support_effects(
    sequence: int,
    round_number: int,
    source: EncounterCombatant,
    setup: EncounterSetup,
) -> tuple[list[BattleEvent], int]:
    events: list[BattleEvent] = []
    for target in [*setup.heroes, *setup.monsters]:
        ending = [
            item for item in target.state.timed_effects
            if item.source_id == source.combatant_id and item.expires_round is not None and item.expires_round <= round_number
        ]
        for effect in ending:
            target.state.timed_effects.remove(effect)
            events.append(BattleEvent(
                sequence=sequence, round_number=round_number, event_type="feature",
                actor_id=source.combatant_id, actor_name=source.state.template.name,
                target_id=target.combatant_id, target_name=target.state.template.name,
                feature_id="support-ended", animation="condition-ended",
                description=f"{effect.effect_id.title()} on {target.state.template.name} ends.",
            ))
            sequence += 1
    return events, sequence
