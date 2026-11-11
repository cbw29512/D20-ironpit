"""Two 2014 vampire-family cards reuse one damage-free Grapple hit resolver."""
from __future__ import annotations

import logging

from app.content.capability_compiler import compile_combatant
from app.content.monster_definition_adapter_2014 import adapt_monster_mechanics_2014
from app.content.monster_multiattack_variants_2014 import source_variants_2014
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_damage_or_grapple_2014 import (
    source_proven_damage_or_grapple_2014,
)
from scripts.browser_template_serializer import template_row

logger = logging.getLogger(__name__)


def _cards():
    try:
        cards = load_monster_source_2014()
        assert len(cards) == 327
        return {card.id: card for card in cards}
    except Exception:
        logger.exception("Failed to load 327 source monsters for Grapple family.")
        raise


def test_only_printed_damage_or_grapple_family_reuses_shared_engine():
    try:
        cards = _cards()
        admitted = {
            key: proof for key, card in cards.items()
            if (proof := source_proven_damage_or_grapple_2014(card))
        }
        assert set(admitted) == {"vampire", "vampire-spawn"}
        for identity, dc, bonus, regen, bite_necrotic_dice in (
            ("vampire", 18, 9, 20, 3),
            ("vampire-spawn", 13, 6, 10, 2),
        ):
            source = cards[identity]
            before = source.model_dump_json()
            (alternative,) = admitted[identity]
            assert alternative.fixed_damage == 0
            assert alternative.attack_bonus == bonus
            assert alternative.reach_ft == 5
            assert len(alternative.effects) == 1
            assert alternative.effects[0].kind == "grapple"
            assert alternative.effects[0].escape_dc == dc
            # Reuse the normal ordered Multiattack variant executor; a
            # non-damaging Grapple replaces its original melee hit in a slot.
            variants = source_variants_2014(source)
            assert any(alternative.id in slot.attack_ids
                       for variant in variants for slot in variant.slots)
            definition = adapt_monster_mechanics_2014(source)
            runtime = compile_combatant(definition)
            binding = next(item for item in runtime.alternate_weapon_attacks
                           if item.id == alternative.id)
            assert binding.fixed_damage == 0
            assert binding.control_effect.grapple_escape_dc == dc
            browser = next(item for item in template_row(runtime)["attacks"]
                           if item["id"] == alternative.id)
            assert browser["fixedDamage"] == 0
            assert browser["controlEffect"]["grappleEscapeDc"] == dc
            # The same mixed-damage attack compiler owns both Bites; the
            # source declares only the different Necrotic dice and hit bonus.
            bite = next(item for item in template_row(runtime)["attacks"]
                        if item["name"].casefold().startswith("bite"))
            assert bite["bonus"] == bonus
            necrotic = next(item for item in bite["onHitDamage"]
                            if item["damageType"] == "necrotic")
            assert (necrotic["diceCount"], necrotic["diceSize"]) == (
                bite_necrotic_dice, 6,
            )
            assert runtime.regeneration.amount == regen
            assert runtime.regeneration.requires_positive_hp
            assert "radiant" in [x.value for x in runtime.regeneration.suppressed_by_damage_types]
            assert "attack:incomplete" in basic_blockers_2014(source)
            assert source.model_dump_json() == before
    except Exception:
        logger.exception("Vampire family shared Grapple parameter parity failed.")
        raise


def test_alternate_hit_does_not_inherit_damage_or_permit_source_drift():
    try:
        cards = _cards()
        for identity in ("vampire", "vampire-spawn"):
            card = cards[identity]
            for before, after in (
                ("Instead of dealing damage", "After dealing damage"),
                ("can grapple the target", "can stun the target"),
            ):
                assert before in card.source_actions
                mutated = card.model_copy(update={
                    "source_actions": card.source_actions.replace(before, after)
                })
                assert source_proven_damage_or_grapple_2014(mutated) == []
            renamed = card.model_copy(update={
                "id": f"synthetic-{identity}", "name": "Synthetic Controller",
            })
            (alternative,) = source_proven_damage_or_grapple_2014(renamed)
            assert alternative.id.startswith(f"2014-synthetic-{identity}-")
    except Exception:
        logger.exception("Vampire source mutation or reusable identity proof failed.")
        raise
