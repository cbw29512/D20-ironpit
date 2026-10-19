"""Complete source proof, mutation rejection and independent edition bindings."""
import logging

import pytest
from pydantic import ValidationError

from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_healing_block_source_2014 import source_completed_healing_block_2014
from app.content.monster_passive_grants_2014 import conditional_immunity_grants_2014
from app.domain.passive_modifiers import PassiveModifierGrant
from bearded_devil_test_support import source, template

logger = logging.getLogger(__name__)


def test_actual_card_completes_every_printed_attack_and_trait_without_mutation():
    try:
        monster = source()
        before = monster.model_dump()
        assert basic_blockers_2014(monster) == ()
        card = template()
        assert card.attack_action.slots[0].attack_ids == ["2014-bearded-devil-beard"]
        assert card.attack_action.slots[1].attack_ids == ["2014-bearded-devil-glaive"]
        assert len([card.weapon_attack, *card.alternate_weapon_attacks]) == 2
        assert card.passive_modifier_grants[0].required_visible_active_ally_within_ft == 30
        assert card.passive_modifier_grants[0].source_name == "Steadfast"
        assert "frightened" not in card.condition_immunities
        assert monster.model_dump() == before
        assert not monster.attacks[0].source_complete
    except Exception:
        logger.exception("Actual Bearded Devil source binding failed.")
        raise


@pytest.mark.parametrize("before,after", [
    ("+5 to hit, reach 5", "+6 to hit, reach 5"),
    ("reach 5 ft.", "reach 10 ft."),
    ("6 (1d8 + 2)", "7 (1d8 + 3)"),
    ("DC 12 Constitution", "DC 13 Constitution"),
    ("poisoned for 1 minute", "poisoned for 2 minutes"),
    ("can't regain hit points", "can regain hit points"),
    ("each of its turns", "each of the devil's turns"),
    ("on a success. </p>", "on a success. It also falls prone. </p>"),
])
def test_changed_attack_source_cannot_silently_complete(before, after):
    try:
        monster = source().model_copy(deep=True)
        assert before in monster.source_actions
        monster.source_actions = monster.source_actions.replace(before, after, 1)
        assert not source_completed_healing_block_2014(monster, monster.attacks[0]).source_complete
        assert "attack:incomplete" in basic_blockers_2014(monster)
    except Exception:
        logger.exception("Changed Beard clause was not rejected: %s.", before)
        raise


@pytest.mark.parametrize("field,value", [
    ("cannot_regain_hit_points", False), ("duration_rounds", 9),
    ("repeat_save_timing", "target_turn_start"), ("dc", 13),
    ("additional_condition", "prone"),
])
def test_rider_drift_remains_incomplete(field, value):
    try:
        monster = source().model_copy(deep=True)
        monster.attacks[0].on_hit_save_effect[field] = value
        assert "attack:incomplete" in basic_blockers_2014(monster)
    except Exception:
        logger.exception("Changed Beard rider was not rejected: %s.", field)
        raise


def test_trait_binding_derives_renamed_label_and_range_but_rejects_extra_semantics():
    try:
        monster = source().model_copy(deep=True)
        monster.trait_names = ["Crystal Resolve"]
        monster.source_traits = monster.source_traits.replace("Steadfast", "Crystal Resolve").replace("30 feet", "15 feet")
        grant, = conditional_immunity_grants_2014(monster)
        assert grant.source_name == "Crystal Resolve" and grant.required_visible_active_ally_within_ft == 15
        monster.source_traits = monster.source_traits.replace("feet of it.", "feet of it. It also cannot be stunned.")
        assert conditional_immunity_grants_2014(monster) == []
    except Exception:
        logger.exception("Renamed conditional immunity source proof failed.")
        raise


def test_unknown_or_obsolete_passive_qualifier_fails_closed():
    try:
        payload = conditional_immunity_grants_2014(source())[0].model_dump()
        payload["unknown_ally_gate"] = 5
        with pytest.raises(ValidationError):
            PassiveModifierGrant.model_validate(payload)
    except Exception:
        logger.exception("Unsupported passive immunity qualifier was accepted.")
        raise
