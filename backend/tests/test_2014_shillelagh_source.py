"""2014 Shillelagh is an active weapon enchantment, not a permanent alternate attack."""
from __future__ import annotations

import logging

import pytest

from app.combat.spell_modifiers import build_spell_modifier
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_source_shillelagh_2014 import (
    source_shillelagh_buff_2014, source_shillelagh_attacks_2014,
)

logger = logging.getLogger(__name__)

def test_shillelagh_attack_is_conditioned_on_generic_buff_not_always_active() -> None:
    try:
        druid = next(item for item in load_monster_source_2014() if item.id == "druid")
        before = druid.model_dump_json()
        transformed = source_shillelagh_attacks_2014(druid)
        assert [attack.id for attack in transformed] == [
            "quarterstaff", "quarterstaff-two-handed",
        ]
        for attack in transformed:
            conditional, = attack.conditional_damage
            assert conditional == {
                "trigger": "attacker_active_effect", "required_effect_id": "shillelagh",
                "mode": "replace_weapon",
                "dice_count": 1, "dice_size": 8, "damage_bonus": 2,
                "damage_type": "bludgeoning",
            }
        buff = source_shillelagh_buff_2014(druid)
        assert (buff.action_cost, buff.duration_rounds, buff.concentration) == (
            "bonus_action", 10, False,
        )
        assert {effect.weapon_id for effect in buff.modifier_effects} == {
            "2014-druid-quarterstaff", "2014-druid-quarterstaff-two-handed",
        }
        assert len(buff.modifier_effects) == 4
        for index, effect in enumerate(buff.modifier_effects):
            scoped = build_spell_modifier("caster", "caster", "shillelagh", effect, index)
            assert scoped.weapon_id == effect.weapon_id
            if index < 2:
                assert scoped.kind.value == "attack-roll-flat"
                assert scoped.flat_bonus == 2
            else:
                assert scoped.kind.value == "damage-source-qualifier"
                assert scoped.source_qualifier.value == "magical"
        assert druid.model_dump_json() == before
    except Exception:
        logger.exception("Shillelagh source weapon bonus was not source-scoped.")
        raise


def test_shillelagh_printed_attack_mutation_fails_closed() -> None:
    try:
        druid = next(item for item in load_monster_source_2014() if item.id == "druid")
        changed = druid.model_copy(deep=True)
        changed.source_actions = changed.source_actions.replace(
            "with shillelagh", "without shillelagh",
        )
        with pytest.raises(ValueError, match="Quarterstaff source changed"):
            source_shillelagh_buff_2014(changed)
        assert basic_blockers_2014(druid) == ()
    except Exception:
        logger.exception("Mutated enhanced-staff source was accepted.")
        raise

