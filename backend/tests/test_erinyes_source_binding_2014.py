"""Source proof composes magical weapon damage with an existing condition save."""
import logging

import pytest

from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_included_weapon_traits_2014 import included_weapon_trait_names_2014
from app.content.monster_mixed_damage_2014 import source_completed_mixed_attack_2014
from app.domain.weapons import DamageSourceQualifier
from erinyes_test_support import card, source

logger = logging.getLogger(__name__)


def test_source_complete_card_preserves_all_printed_parameters_without_mutation():
    try:
        monster = source()
        before = monster.model_dump()
        assert basic_blockers_2014(monster) == ()
        assert included_weapon_trait_names_2014(monster) == {"Hellish Weapons"}
        template = card()
        attacks = [template.weapon_attack, *template.alternate_weapon_attacks]
        assert len(attacks) == 3
        for attack in attacks:
            assert attack.damage_source_qualifiers == [DamageSourceQualifier.MAGICAL]
            assert [(r.dice_count, r.dice_size, r.damage_type.value) for r in attack.on_hit_damage] == [(3, 8, "poison")]
        bow = next(attack for attack in attacks if attack.weapon.name == "Longbow")
        assert (bow.attack_bonus, bow.weapon.normal_range_ft, bow.weapon.long_range_ft) == (7, 150, 600)
        assert (bow.weapon.dice_count, bow.weapon.dice_size, bow.damage_bonus) == (1, 8, 3)
        effect = bow.on_hit_condition_save
        assert (effect.condition_id, effect.save_ability, effect.dc) == ("poisoned", "constitution", 14)
        assert effect.duration_rounds is None and effect.repeat_save_timing is None
        assert monster.model_dump() == before
    except Exception:
        logger.exception("Failed exact immutable source/compiled Erinyes parameter proof.")
        raise


@pytest.mark.parametrize("mutation", ["bonus", "range", "base", "rider", "extra_clause", "removal", "trait", "target_policy", "existing_effect"])
def test_source_or_payload_mismatches_remain_blocked(mutation):
    try:
        monster = source().model_copy(deep=True)
        bow = next(attack for attack in monster.attacks if attack.id == "longbow")
        if mutation == "bonus":
            bow.attack_bonus += 1
        elif mutation == "range":
            bow.long_range_ft -= 5
        elif mutation == "base":
            bow.damage.bonus += 1
        elif mutation == "rider":
            bow.on_hit_damage.clear()
        elif mutation == "extra_clause":
            monster.source_actions = monster.source_actions.replace("or similar magic.", "or similar magic. The target is also stunned.")
        elif mutation == "removal":
            monster.source_actions = monster.source_actions.replace("lesser restoration", "ordinary rest")
        elif mutation == "trait":
            monster.source_traits = monster.source_traits.replace("3d8", "4d8")
        elif mutation == "target_policy":
            bow.grapple_target_policy = "own_grapple_only"
        else:
            bow.on_hit_save_effect = {}
        assert basic_blockers_2014(monster)
    except Exception:
        logger.exception("Erinyes source mutation did not fail closed: %s.", mutation)
        raise


def test_renamed_source_supplies_its_own_dc_without_new_engine_logic():
    try:
        monster = source().model_copy(deep=True)
        monster.id, monster.name = "prism-guardian", "Prism Guardian"
        monster.source_actions = monster.source_actions.replace("Longbow", "Prism Bolt").replace("DC 14", "DC 17")
        bow = next(attack for attack in monster.attacks if attack.id == "longbow")
        bow.id, bow.name = "prism-bolt", "Prism Bolt"
        corrected = source_completed_mixed_attack_2014(monster, bow)
        assert corrected.source_complete
        assert corrected.on_hit_save_effect == {"condition_id": "poisoned", "save_ability": "constitution", "dc": 17}
        assert bow.on_hit_save_effect is None
    except Exception:
        logger.exception("Renamed persistent hit-condition source failed parameter-driven binding.")
        raise
