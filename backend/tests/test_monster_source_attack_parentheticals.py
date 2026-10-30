from __future__ import annotations

import logging

from app.content.monster_source_capability_candidates import source_candidate_definitions

logger = logging.getLogger(__name__)


def test_form_qualified_attack_is_parsed_without_fake_resource() -> None:
    try:
        candidates = source_candidate_definitions(set())
        werewolf = candidates["srd-werewolf"]
        bite = next(attack for attack in werewolf.attacks if attack.name == "Bite")

        assert bite.resource_id is None
        save = next(effect for effect in bite.effects if effect.kind == "saving-throw")
        assert save.dc == 12
        assert save.target_filter.required_creature_types == ["humanoid"]
        replacement = next(effect for effect in save.failure_effects if effect.kind == "zero-hp-replacement")
        assert replacement.effect_id == "cursed"
        assert replacement.replacement_hp == 10
    except Exception:
        logger.exception("Form-qualified source attack regression failed.")
        raise


def test_recharge_parenthetical_still_creates_a_resource() -> None:
    try:
        candidates = source_candidate_definitions(set())
        ape = candidates["srd-ape"]
        rock = next(attack for attack in ape.attacks if attack.name == "Rock")

        assert rock.resource_id == "srd-ape-rock-recharge"
        assert any(resource.id == rock.resource_id for resource in ape.resources)
    except Exception:
        logger.exception("Recharge source attack parenthetical regression failed.")
        raise
