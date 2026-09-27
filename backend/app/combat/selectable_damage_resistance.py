from __future__ import annotations

import logging

from app.combat.modifier_stack import attack_damage_source_qualifiers
from app.domain.damage_sources import ConditionalDamageDefense, DamageDefenseKind
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.events import BattleEvent
from app.domain.weapons_base import DamageType

logger = logging.getLogger(__name__)


def _average_damage(dice_count: int, dice_size: int, bonus: int = 0) -> float:
    if dice_count <= 0:
        return float(max(0, bonus))
    return dice_count * (dice_size + 1) / 2 + bonus


def _score_enemy_damage(member: EncounterCombatant, setup: EncounterSetup) -> dict[DamageType, float]:
    rule = member.state.template.progression_features.selectable_damage_resistance
    if rule is None:
        return {}
    scores = {damage_type: 0.0 for damage_type in rule.allowed_damage_types}
    enemies = setup.monsters if member.side == "heroes" else setup.heroes
    forbidden = set(rule.forbidden_source_qualifiers)

    for enemy in enemies:
        template = enemy.state.template
        for attack in [template.weapon_attack, *template.alternate_weapon_attacks]:
            if attack.weapon.damage_type not in scores:
                continue
            qualifiers = attack_damage_source_qualifiers(enemy.state, attack)
            if forbidden.intersection(qualifiers):
                continue
            scores[attack.weapon.damage_type] += _average_damage(
                attack.weapon.dice_count, attack.weapon.dice_size, attack.damage_bonus,
            )
            for rider in attack.on_hit_damage:
                if rider.damage_type in scores:
                    scores[rider.damage_type] += _average_damage(
                        rider.dice_count, rider.dice_size, rider.damage_bonus,
                    )

        for action in [*template.saving_throw_actions, *template.spell_save_actions]:
            for component in action.damage_components:
                typed = DamageType(component.damage_type)
                if typed in scores:
                    scores[typed] += _average_damage(
                        component.dice_count, component.dice_size, component.damage_bonus,
                    )
            if action.damage_type is not None:
                typed = DamageType(action.damage_type)
                if typed in scores:
                    scores[typed] += _average_damage(
                        action.damage_dice_count, action.damage_dice_size, action.damage_bonus,
                    )

        for action in template.spell_attack_actions:
            if action.damage_type is None:
                continue
            typed = DamageType(action.damage_type)
            if typed in scores:
                scores[typed] += action.attack_count * _average_damage(
                    action.damage_dice_count, action.damage_dice_size, action.damage_bonus,
                )

    return scores


def choose_damage_resistance(member: EncounterCombatant, setup: EncounterSetup) -> DamageType | None:
    """Choose the legal damage type with the highest visible opposing damage value."""
    rule = member.state.template.progression_features.selectable_damage_resistance
    if rule is None:
        return None
    scores = _score_enemy_damage(member, setup)
    order = {item: index for index, item in enumerate(rule.allowed_damage_types)}
    return max(
        rule.allowed_damage_types,
        key=lambda item: (scores.get(item, 0.0), -order[item]),
        default=None,
    )


def resolve_selectable_damage_resistance(
    sequence: int,
    member: EncounterCombatant,
    setup: EncounterSetup,
) -> BattleEvent | None:
    """Apply one fight-scoped source-qualified resistance selected at preparation."""
    try:
        rule = member.state.template.progression_features.selectable_damage_resistance
        if rule is None or member.state.opening_buff_id is not None:
            return None
        selected = choose_damage_resistance(member, setup)
        if selected is None:
            return None

        member.state.active_conditional_damage_defenses = [
            item for item in member.state.active_conditional_damage_defenses
            if item.id != rule.source_id
        ]
        member.state.active_conditional_damage_defenses.append(ConditionalDamageDefense(
            id=rule.source_id,
            kind=DamageDefenseKind.RESISTANCE,
            damage_types=[selected],
            forbidden_source_qualifiers=rule.forbidden_source_qualifiers,
        ))
        member.state.opening_buff_id = rule.source_id
        return BattleEvent(
            sequence=sequence,
            round_number=0,
            event_type="feature",
            actor_id=member.combatant_id,
            actor_name=member.state.template.name,
            target_id=member.combatant_id,
            target_name=member.state.template.name,
            feature_id=rule.source_id,
            animation="damage-resistance",
            description=(
                f"Precombat preparation: {member.state.template.name} uses {rule.source_name} "
                f"and chooses {selected.value} resistance."
            ),
        )
    except Exception as exc:
        logger.exception("Selectable damage resistance failed for %s.", member.combatant_id)
        raise RuntimeError("Selectable damage resistance could not be resolved.") from exc
