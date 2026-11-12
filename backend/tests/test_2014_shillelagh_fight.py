"""Prove 2014 Shillelagh changes only the equipped staff for its active lifetime."""
from __future__ import annotations

import logging

from app.combat.damage import resolve_weapon_damage
from app.combat.dice import FixedDiceProvider
from app.combat.modifier_flat_bonuses import attack_roll_flat_bonus
from app.combat.modifier_stack import attack_damage_source_qualifiers
from app.combat.state import build_combatant_state
from app.combat.timed_condition_lifecycle import remove_effect_group
from app.combat.timed_self_buffs import resolve_timed_self_buff
from app.content.capability_compiler import compile_combatant
from app.content.monster_definition_adapter_2014 import adapt_monster_mechanics_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.damage_sources import DamageSourceQualifier
from app.domain.encounters import EncounterCombatant
from app.domain.models import RollMode

logger = logging.getLogger(__name__)


def test_printed_druid_staff_never_gains_shillelagh_damage_for_free() -> None:
    try:
        card = next(item for item in load_monster_source_2014() if item.id == "druid")
        immutable = card.model_dump_json()
        template = compile_combatant(adapt_monster_mechanics_2014(card))
        weapons = [template.weapon_attack, *template.alternate_weapon_attacks]
        staff = next(attack for attack in weapons
                     if attack is not None and attack.id == "2014-druid-quarterstaff")
        other = next(attack for attack in weapons
                     if attack is not None and attack.id.endswith("quarterstaff-two-handed"))
        buff = next(action for action in template.timed_self_buff_actions
                    if action.id == "shillelagh")
        state = build_combatant_state(template)
        caster = EncounterCombatant(
            combatant_id="caster", side="monsters", position_ft=5, state=state,
        )
        before, parts = resolve_weapon_damage(
            state, staff, FixedDiceProvider([4]), False, RollMode.NORMAL,
        )
        assert before.total == 4 and parts[0].notation == "1d6+0"
        assert attack_roll_flat_bonus(state, staff.weapon.id) == 0
        assert DamageSourceQualifier.MAGICAL not in attack_damage_source_qualifiers(state, staff)

        cast = resolve_timed_self_buff(
            1, 1, caster, buff, spend_action_cost=True,
        )
        assert cast.feature_id == "shillelagh"
        assert state.action_available and not state.bonus_action_available
        assert "shillelagh" in state.active_effect_ids
        assert attack_roll_flat_bonus(state, staff.weapon.id) == 2
        assert attack_roll_flat_bonus(state, other.weapon.id) == 2
        assert DamageSourceQualifier.MAGICAL in attack_damage_source_qualifiers(state, staff)
        empowered, parts = resolve_weapon_damage(
            state, staff, FixedDiceProvider([5]), False, RollMode.NORMAL,
        )
        assert empowered.total == 7 and parts[0].notation == "1d8+2"

        timed = next(effect for effect in state.timed_effects
                     if effect.source_effect_id == "shillelagh")
        assert remove_effect_group(state, timed) == ["shillelagh"]
        assert "shillelagh" not in state.active_effect_ids
        assert attack_roll_flat_bonus(state, staff.weapon.id) == 0
        assert DamageSourceQualifier.MAGICAL not in attack_damage_source_qualifiers(state, staff)
        restored, parts = resolve_weapon_damage(
            state, staff, FixedDiceProvider([4]), False, RollMode.NORMAL,
        )
        assert restored.total == before.total and parts[0].notation == "1d6+0"
        assert card.model_dump_json() == immutable
    except Exception:
        logger.exception("Source-backed 2014 Shillelagh did not use universal buff lifecycle.")
        raise
