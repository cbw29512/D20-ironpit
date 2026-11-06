"""2014 equipment-corrosion exclusion: preserve real attacks and card source."""
from __future__ import annotations

import logging

from app.combat.attacks import resolve_attack
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.capability_attack_compiler import compile_attack
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_definition_adapter_2014 import _attack
from app.content.monster_mixed_damage_2014 import source_completed_mixed_attack_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monsters import build_commoner
from app.domain.weapons_base import DamageType

logger = logging.getLogger(__name__)


def _source(monster_id: str):
    try:
        return next(m for m in load_monster_source_2014() if m.id == monster_id)
    except Exception:
        logger.exception("Missing 2014 equipment source %s", monster_id)
        raise


def test_roster_equipment_family_coverage_and_no_invented_attacks():
    try:
        roster = load_monster_source_2014()
        matching = []
        for monster in roster:
            text = (monster.source_traits or "") + (monster.source_actions or "")
            if "permanent and cumulative −1 penalty" in text and (
                "weapon" in text or "armor" in text
            ):
                matching.append(monster.id)
        assert len(roster) == 327
        assert set(matching) == {"black-pudding", "gray-ooze", "rust-monster"}
        for monster_id in matching:
            assert basic_blockers_2014(_source(monster_id)) == ()
        # A gear-only Action remains printed, but is never fabricated as
        # a damage Action, or rolled against a character.
        rust = _source("rust-monster")
        assert "Antennae" in rust.action_names
        assert [row.name for row in rust.attacks] == ["Bite"]
    except Exception:
        logger.exception("Equipment corrosion corpus classification failed")
        raise


def test_gray_ooze_still_deals_both_printed_damage_types_on_one_hit():
    try:
        ooze = _source("gray-ooze")
        original = ooze.model_dump_json()
        source_attack = ooze.attacks[0]
        corrected = source_completed_mixed_attack_2014(ooze, source_attack)
        assert corrected.source_complete
        assert corrected.damage == source_attack.damage
        assert corrected.on_hit_damage == source_attack.on_hit_damage
        weapon = compile_attack(_attack(ooze, source_attack))
        assert weapon.weapon.damage_type == DamageType.BLUDGEONING
        assert [(part.dice_count, part.dice_size, part.damage_type)
                for part in weapon.on_hit_damage] == [(2, 6, DamageType.ACID)]
        attacker = build_combatant_state(build_commoner())
        victim_template = build_commoner().model_copy(update={
            "max_hp": 100, "damage_immunities": [DamageType.ACID],
        })
        victim = build_combatant_state(victim_template)
        result = resolve_attack(
            1, 1, attacker, victim, weapon, 5,
            FixedDiceProvider([18, 4, 5, 5]), spend_action=False,
        )
        assert result.hit
        parts = {str(part.damage_type): part for part in result.damage_components}
        assert parts["acid"].applied_total == 0
        assert parts["bludgeoning"].applied_total > 0
        assert victim.current_hp == 100 - parts["bludgeoning"].applied_total
        assert not attacker.weapon_corrosion_penalties
        assert not victim.armor_corrosion_penalties
        assert not victim.destroyed_armor_ids
        assert ooze.model_dump_json() == original
    except Exception:
        logger.exception("Gray Ooze ordinary typed damage or equipment isolation failed")
        raise


def test_added_combat_effect_never_inherits_gear_only_exclusion():
    try:
        ooze = _source("gray-ooze")
        mutated_attack = ooze.model_copy(update={
            "source_actions": ooze.source_actions.replace(
                "reduces its AC to 10.</p>",
                "reduces its AC to 10. The victim is also paralyzed.</p>",
            ),
        })
        assert "attack:incomplete" in basic_blockers_2014(mutated_attack)
        mutated_trait = ooze.model_copy(update={
            "source_traits": ooze.source_traits.replace(
                "in 1 round. </p>",
                "in 1 round. Nearby enemies take 2d6 poison damage.</p>",
            ),
        })
        assert "source:trait" in basic_blockers_2014(mutated_trait)
    except Exception:
        logger.exception("Unverified combat rider bypassed source-completeness gate")
        raise
