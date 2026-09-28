from __future__ import annotations

from app.combat.forced_movement import push_straight_away
from app.combat.modifier_stack import add_modifier
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import CombatantState
from app.domain.modifiers import CombatModifier, ModifierKind

BRUTAL_STRIKE_HIT_KEY = "brutal-strike-hit"
BRUTAL_STRIKE_EFFECT_KEY = "brutal-strike-effect"
_EFFECT_PRIORITY = ("hamstring-blow", "staggering-blow", "forceful-blow", "sundering-blow")


def apply_hamstring_blow(defender: CombatantState, source_id: str, round_number: int) -> bool:
    """Reduce Speed by 15 feet; only the most recent Hamstring Blow remains."""
    defender.active_modifiers = [
        item for item in defender.active_modifiers if item.source_effect_id != "hamstring-blow"
    ]
    add_modifier(defender, CombatModifier(
        id=f"hamstring-blow:{source_id}",
        source_id=source_id,
        source_effect_id="hamstring-blow",
        source_name="Hamstring Blow",
        kind=ModifierKind.SPEED,
        flat_bonus=-15,
        expires_at_start_of_source_turn=True,
    ))
    return True


def apply_forceful_blow(
    attacker: EncounterCombatant, defender: EncounterCombatant, setup: EncounterSetup,
) -> int:
    """Push the target 15 feet straight away. Following the target remains optional."""
    return push_straight_away(defender, attacker, setup, 15)


def apply_staggering_blow(defender: CombatantState, source_id: str) -> bool:
    """Compose next-save Disadvantage and OA suppression from generic modifiers."""
    add_modifier(defender, CombatModifier(
        id=f"staggering-blow:{source_id}:save",
        source_id=source_id,
        source_effect_id="staggering-blow",
        source_name="Staggering Blow",
        kind=ModifierKind.SAVING_THROW_DISADVANTAGE,
        consume_on_saving_throw=True,
        expires_at_start_of_source_turn=True,
    ))
    add_modifier(defender, CombatModifier(
        id=f"staggering-blow:{source_id}:oa",
        source_id=source_id,
        source_effect_id="staggering-blow",
        source_name="Staggering Blow",
        kind=ModifierKind.OPPORTUNITY_ATTACK_SUPPRESSED,
        expires_at_start_of_source_turn=True,
    ))
    return True


def apply_sundering_blow(defender: CombatantState, source_id: str) -> bool:
    """Grant +5 to the next other-creature attack without stacking Sundering bonuses."""
    defender.active_modifiers = [
        item for item in defender.active_modifiers if item.source_effect_id != "sundering-blow"
    ]
    add_modifier(defender, CombatModifier(
        id=f"sundering-blow:{source_id}",
        source_id=source_id,
        source_effect_id="sundering-blow",
        source_name="Sundering Blow",
        kind=ModifierKind.NEXT_INCOMING_ATTACK_ROLL_FLAT,
        flat_bonus=5,
        expires_at_start_of_source_turn=True,
    ))
    return True


def select_brutal_strike_effects(
    state: CombatantState, requested: tuple[str, ...] | None = None,
) -> tuple[str, ...]:
    available = tuple(state.template.progression_features.brutal_strike_effect_ids)
    maximum = state.template.progression_features.brutal_strike_max_effects
    if maximum <= 0 or not available:
        return ()
    selected = requested or tuple(item for item in _EFFECT_PRIORITY if item in available)[:maximum]
    if len(selected) > maximum:
        raise ValueError(f"Brutal Strike allows at most {maximum} effect(s).")
    if len(set(selected)) != len(selected):
        raise ValueError("Brutal Strike effects must be different.")
    invalid = [item for item in selected if item not in available]
    if invalid:
        raise ValueError(f"Unavailable Brutal Strike effect(s): {', '.join(invalid)}")
    return tuple(selected)


def apply_brutal_strike_effects(
    attacker: EncounterCombatant,
    defender: EncounterCombatant,
    setup: EncounterSetup | None,
    turn_key: str | None,
    *,
    round_number: int,
    requested: tuple[str, ...] | None = None,
) -> tuple[str, ...]:
    state = attacker.state
    if (
        not turn_key
        or state.feature_last_turn_keys.get(BRUTAL_STRIKE_HIT_KEY) != turn_key
        or state.feature_last_turn_keys.get(BRUTAL_STRIKE_EFFECT_KEY) == turn_key
    ):
        return ()
    selected = select_brutal_strike_effects(state, requested)
    for effect_id in selected:
        if effect_id == "hamstring-blow":
            apply_hamstring_blow(defender.state, attacker.combatant_id, round_number)
        elif effect_id == "staggering-blow":
            apply_staggering_blow(defender.state, attacker.combatant_id)
        elif effect_id == "sundering-blow":
            apply_sundering_blow(defender.state, attacker.combatant_id)
        elif effect_id == "forceful-blow":
            if setup is None:
                raise ValueError("Forceful Blow requires encounter geometry.")
            apply_forceful_blow(attacker, defender, setup)
        else:
            raise ValueError(f"Unsupported Brutal Strike effect: {effect_id}")
    if selected:
        state.feature_last_turn_keys[BRUTAL_STRIKE_EFFECT_KEY] = turn_key
    return selected
