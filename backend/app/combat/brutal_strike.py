from __future__ import annotations

from app.combat.reckless_attack import reckless_attack_active
from app.combat.forced_movement import push_straight_away
from app.combat.modifier_stack import add_modifier, effective_speed
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import CombatantState, DamageType, WeaponAttack
from app.domain.modifiers import CombatModifier, ModifierKind

BRUTAL_STRIKE_FEATURE_ID = "brutal-strike"
BonusDamageSpec = tuple[str, int, int, DamageType]


def brutal_strike_bonus_damage(
    state: CombatantState,
    attack: WeaponAttack,
    turn_key: str | None,
    *,
    has_disadvantage: bool,
) -> BonusDamageSpec | None:
    """Consume 2024 Brutal Strike on one eligible Strength attack during the active turn."""
    dice_count = state.template.progression_features.brutal_strike_damage_dice
    if (
        state.template.ruleset == "2014"
        or dice_count <= 0
        or turn_key is None
        or has_disadvantage
        or attack.attack_ability != "strength"
        or not reckless_attack_active(state)
        or state.feature_last_turn_keys.get(BRUTAL_STRIKE_FEATURE_ID) == turn_key
    ):
        return None
    state.feature_last_turn_keys[BRUTAL_STRIKE_FEATURE_ID] = turn_key
    return ("Brutal Strike", dice_count, 10, attack.weapon.damage_type)


def brutal_strike_advantage_suppression(
    state: CombatantState,
    attack: WeaponAttack,
    turn_key: str | None,
    *,
    has_disadvantage: bool,
) -> int:
    """Cancel only the Advantage granted by Reckless Attack for the chosen Brutal Strike roll."""
    if (
        state.template.ruleset == "2014"
        or state.template.progression_features.brutal_strike_damage_dice <= 0
        or turn_key is None
        or has_disadvantage
        or attack.attack_ability != "strength"
        or not reckless_attack_active(state)
        or state.feature_last_turn_keys.get(BRUTAL_STRIKE_FEATURE_ID) == turn_key
    ):
        return 0
    return 1


def apply_hamstring_blow(
    defender: CombatantState,
    source_id: str,
    round_number: int,
) -> bool:
    """Apply the 2024 Brutal Strike Hamstring Blow speed penalty until source turn start."""
    modifier = CombatModifier(
        id=f"hamstring-blow:{source_id}",
        source_id=source_id,
        source_effect_id="hamstring-blow",
        kind=ModifierKind.SPEED,
        flat_bonus=-15,
        expires_at_start_of_source_turn=True,
    )
    add_modifier(defender, modifier)
    return True


def apply_staggering_blow(
    defender: CombatantState,
    source_id: str,
) -> bool:
    """Apply Staggering Blow through shared next-save and OA-suppression modifiers."""
    defender.active_modifiers = [
        item for item in defender.active_modifiers
        if not (item.source_id == source_id and item.source_effect_id == "staggering-blow")
    ]
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


def apply_sundering_blow(
    defender: CombatantState,
    source_id: str,
) -> bool:
    """Prime the target for one +5 attack by a different creature before source turn start."""
    defender.active_modifiers = [
        item for item in defender.active_modifiers
        if item.source_effect_id != "sundering-blow"
    ]
    add_modifier(defender, CombatModifier(
        id=f"sundering-blow:{source_id}",
        source_id=source_id,
        source_effect_id="sundering-blow",
        source_name="Sundering Blow",
        kind=ModifierKind.NEXT_ATTACK_AGAINST_FLAT,
        flat_bonus=5,
        consume_on_attack_against=True,
        expires_at_start_of_source_turn=True,
    ))
    return True


def apply_forceful_blow(
    attacker: EncounterCombatant,
    defender: EncounterCombatant,
    setup: EncounterSetup,
) -> int:
    """Apply the 2024 Brutal Strike Forceful Blow 15-foot straight-away push."""
    return push_straight_away(defender, attacker, setup, 15)


def follow_forceful_blow(
    sequence: int,
    round_number: int,
    attacker: EncounterCombatant,
    defender: EncounterCombatant,
    setup: EncounterSetup,
    dice,
    *,
    turn_key: str | None = None,
):
    """Move up to half Speed straight toward the pushed target without provoking OAs."""
    from app.combat.grid_reaction_movement import move_toward_on_grid

    allowance = effective_speed(attacker.state) // 2
    normal_remaining = attacker.state.movement_remaining_ft
    attacker.state.movement_remaining_ft = allowance
    try:
        return move_toward_on_grid(
            sequence, round_number, attacker, defender, setup, 5, dice,
            movement_source="forced", disengaged=True, turn_key=turn_key,
        )
    finally:
        attacker.state.movement_remaining_ft = normal_remaining

def brutal_strike_attack_sources(
    state: CombatantState,
    attack: WeaponAttack,
    turn_key: str | None,
    *,
    reckless_advantage: int,
    disadvantage_sources: int,
) -> tuple[int, bool]:
    """Return adjusted Reckless Advantage and whether the chosen roll has Disadvantage."""
    has_disadvantage = disadvantage_sources > 0
    suppression = brutal_strike_advantage_suppression(
        state, attack, turn_key, has_disadvantage=has_disadvantage,
    )
    return max(0, reckless_advantage - suppression), has_disadvantage
