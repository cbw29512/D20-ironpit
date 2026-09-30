from __future__ import annotations

import logging
from dataclasses import dataclass

from app.combat.barrier_line_of_effect import clear_line_between_members
from app.combat.action_economy import is_available
from app.combat.encounter_targeting import combatant_distance
from app.combat.offense_value import auto_hit_spell_expected_damage
from app.combat.spellcasting import legal_slot_levels
from app.combat.spell_damage_maximizers import safe_maximizer_for_spell
from app.domain.auto_hit_spells import AutoHitSpellAction
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.spell_damage_maximizers import SpellDamageMaximizerGrant

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AutoHitSpellChoice:
    action: AutoHitSpellAction
    target: EncounterCombatant
    slot_level: int
    projectile_count: int
    expected_damage: float
    damage_maximizer: SpellDamageMaximizerGrant | None = None


def choose_auto_hit_spell(
    caster: EncounterCombatant,
    setup: EncounterSetup,
    turn_key: str,
) -> AutoHitSpellChoice | None:
    try:
        enemies = setup.monsters if caster.side == "heroes" else setup.heroes
        candidates: list[tuple[float, int, int, str, AutoHitSpellChoice]] = []
        for index, action in enumerate(caster.state.template.auto_hit_spell_actions):
            if action.action_cost == "reaction" or not is_available(caster.state, action.action_cost):
                continue
            for slot_level in legal_slot_levels(
                caster.state,
                turn_key,
                action.level,
                higher_slot_scaling=action.projectiles_per_slot_above > 0,
            ):
                projectile_count = action.projectile_count + (
                    slot_level - action.level
                ) * action.projectiles_per_slot_above
                for target in enemies:
                    if (
                        not target.state.is_alive
                        or target.state.is_dead
                        or target.state.current_hp <= 0
                        or combatant_distance(caster, target) > action.range_ft
                        or not clear_line_between_members(caster, target, setup)
                    ):
                        continue
                    score = auto_hit_spell_expected_damage(
                        target, action, projectile_count,
                    )
                    choice = AutoHitSpellChoice(
                        action=action, target=target, slot_level=slot_level,
                        projectile_count=projectile_count, expected_damage=score,
                        damage_maximizer=safe_maximizer_for_spell(
                            caster, action.id, slot_level,
                        ),
                    )
                    candidates.append((
                        score, -action.level, -index, target.combatant_id, choice,
                    ))
        return max(candidates, key=lambda item: item[:4])[4] if candidates else None
    except Exception:
        logger.exception("Failed to choose auto-hit spell for %s.", caster.combatant_id)
        raise
