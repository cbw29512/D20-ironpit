from __future__ import annotations

import logging

from app.content.monster_basic_attack_support_2014 import (
    source_conditional_attack_advantage_2014,
    supports_basic_attack_effects_2014,
)
from app.content.monster_basic_save_effect_2014 import save_effect_2014
from app.content.monster_conditional_damage_2014 import conditional_damage_effect_2014
from app.content.monster_grapple_periodic_2014 import (
    grapple_periodic_damage_2014,
    supports_grapple_periodic_2014,
)
from app.content.monster_source_2014 import SourceAttack2014
from app.domain.capability_effects import (
    AbilityScoreReductionEffectDefinition,
    AttackEffectDefinition,
    ContestedMovementEffectDefinition,
    DamageEffectDefinition,
    DiceSpec,
    GrappleEffectDefinition,
)
from app.domain.size import CreatureSize
from app.domain.weapons import DamageType

logger = logging.getLogger(__name__)


def basic_attack_effects_2014(
    attack: SourceAttack2014,
    opening_source_name: str | None = None,
) -> list[AttackEffectDefinition]:
    try:
        if not supports_basic_attack_effects_2014(attack):
            raise ValueError(f"{attack.id} has unsupported 2014 attack effects")
        effects: list[AttackEffectDefinition] = [
            conditional_damage_effect_2014(
                row,
                (
                    opening_source_name
                    if row.get("trigger") == "round1_initiative_lead"
                    and opening_source_name
                    else attack.name
                ),
            )
            for row in attack.conditional_damage
        ]
        for row in attack.on_hit_damage:
            if not isinstance(row, dict):
                raise ValueError(f"{attack.id} has malformed on-hit damage data.")
            effects.append(DamageEffectDefinition(
                source=attack.name,
                dice=DiceSpec(
                    count=int(row["dice_count"]),
                    size=int(row["dice_size"]),
                    bonus=int(row.get("bonus", 0)),
                ),
                damage_type=DamageType(str(row["type"]).lower()),
            ))
        if attack.on_hit_save_effect is not None:
            effects.append(save_effect_2014(attack))
        if attack.on_hit_ability_score_reduction is not None:
            row = attack.on_hit_ability_score_reduction
            if not isinstance(row, dict):
                raise ValueError(f"{attack.id} has malformed ability-score reduction data.")
            effects.append(AbilityScoreReductionEffectDefinition(
                source=attack.name,
                ability=str(row["ability"]).lower(),
                dice=DiceSpec(
                    count=int(row["dice_count"]),
                    size=int(row["dice_size"]),
                ),
            ))
        if attack.on_hit_contested_movement is not None:
            row = attack.on_hit_contested_movement
            if not isinstance(row, dict):
                raise ValueError(f"{attack.id} has malformed contested-movement data.")
            max_size = row.get("max_target_size")
            effects.append(ContestedMovementEffectDefinition(
                source_ability=str(row["source_ability"]).lower(),
                target_ability=str(row["target_ability"]).lower(),
                max_target_size=(
                    CreatureSize(str(max_size).lower()) if max_size is not None else None
                ),
                distance_ft=int(row["distance_ft"]),
                direction=str(row["direction"]),
            ))
        if attack.control_effect is not None:
            row = attack.control_effect
            if not isinstance(row, dict):
                raise ValueError(f"{attack.id} has malformed control-effect data.")
            max_size = row.get("max_target_size")
            effects.append(GrappleEffectDefinition(
                escape_dc=int(row["grapple_escape_dc"]),
                max_target_size=(
                    CreatureSize(str(max_size).lower()) if max_size is not None else None
                ),
                restrains=bool(row.get("restrains_while_grappled", False)),
                requires_source_free=supports_grapple_periodic_2014(attack),
                max_active_grapples=row.get("max_active_grapples"),
                periodic_damage=(
                    grapple_periodic_damage_2014(attack)
                    if supports_grapple_periodic_2014(attack) else None
                ),
            ))
        return effects
    except Exception:
        logger.exception("Failed to compile basic 2014 attack effects for %s.", attack.id)
        raise
