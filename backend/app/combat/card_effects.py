from __future__ import annotations

import logging

from app.domain.models import (
    AttackRollEffect,
    AttackRollEffectKind,
    CombatCardEffectChange,
    CombatantState,
    ConditionKind,
)

logger = logging.getLogger(__name__)


def _attack_effect_id(effect: AttackRollEffect) -> str:
    target = effect.target_actor_id or "any"
    return f"{effect.id}:{effect.source_actor_id}:{target}"


def attack_effect_change(
    holder: CombatantState,
    effect: AttackRollEffect,
    operation: str,
) -> CombatCardEffectChange:
    try:
        buff = effect.kind is AttackRollEffectKind.ADVANTAGE
        labels = {"sap": "Sap", "vex": "Vex"}
        details = {
            "sap": "Next applicable attack roll has Disadvantage.",
            "vex": "Next attack against the marked target has Advantage.",
        }
        return CombatCardEffectChange(
            actor_id=holder.template.id,
            effect_id=_attack_effect_id(effect),
            operation=operation,
            kind="buff" if buff else "debuff",
            label=labels.get(effect.id, effect.id.replace("-", " ").title()),
            detail=details.get(effect.id),
        )
    except Exception as exc:
        logger.exception("Failed to build attack-effect card change.")
        raise RuntimeError("Combat-card effect could not be built.") from exc


def dodge_effect_change(
    actor: CombatantState,
    operation: str,
) -> CombatCardEffectChange:
    return CombatCardEffectChange(
        actor_id=actor.template.id,
        effect_id="dodge",
        operation=operation,
        kind="buff",
        label="Dodge",
        detail="Seen attackers have Disadvantage; Dexterity saves have Advantage.",
    )


def hidden_effect_change(
    actor: CombatantState,
    operation: str,
) -> CombatCardEffectChange:
    return CombatCardEffectChange(
        actor_id=actor.template.id,
        effect_id="hidden",
        operation=operation,
        kind="buff",
        label="Hidden",
        detail="Currently hidden from the opponent in the supported visibility model.",
    )


def condition_effect_change(
    actor: CombatantState,
    condition: ConditionKind,
    operation: str,
) -> CombatCardEffectChange:
    try:
        kind = "buff" if condition is ConditionKind.INVISIBLE else "debuff"
        return CombatCardEffectChange(
            actor_id=actor.template.id,
            effect_id=f"condition:{condition.value}",
            operation=operation,
            kind=kind,
            label=condition.value.replace("-", " ").title(),
            detail="Active combat condition.",
        )
    except Exception as exc:
        logger.exception("Failed to build condition card effect for %s.", actor.template.name)
        raise RuntimeError("Condition card effect could not be built.") from exc


def mastery_effect_change(
    feature_id: str | None,
    attacker: CombatantState,
    defender: CombatantState,
) -> CombatCardEffectChange | None:
    try:
        if feature_id == "sap":
            effect = next(
                (item for item in defender.attack_roll_effects if item.id == "sap"),
                None,
            )
            return attack_effect_change(defender, effect, "apply") if effect else None
        if feature_id == "vex":
            effect = next(
                (
                    item for item in attacker.attack_roll_effects
                    if item.id == "vex"
                    and item.target_actor_id == defender.template.id
                ),
                None,
            )
            return attack_effect_change(attacker, effect, "apply") if effect else None
        return None
    except Exception as exc:
        logger.exception("Failed to build mastery card effect.")
        raise RuntimeError("Mastery card effect could not be built.") from exc
