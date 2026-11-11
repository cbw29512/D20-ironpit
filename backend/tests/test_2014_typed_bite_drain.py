"""Source-neutral Bite eligibility and on-hit typed damage transfer regressions."""
from __future__ import annotations

import logging

from app.combat.attack_legality import attack_allowed_against
from app.combat.on_hit_typed_drain import apply_on_hit_typed_drain
from app.combat.state import build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.demo import build_goblin_warrior
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_definition_adapter_2014 import adapt_monster_mechanics_2014
from app.content.monster_mixed_damage_2014 import source_completed_mixed_attack_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_necrotic_drain_2014 import source_proven_typed_drain_2014
from app.domain.event_support import DamageRollComponent
from app.domain.weapons_base import DamageType
from scripts.browser_template_serializer import template_row

logger = logging.getLogger(__name__)


def _source():
    try:
        return {card.id: card for card in load_monster_source_2014()}
    except Exception:
        logger.exception("Failed to load source-driven typed-drain family.")
        raise


def _bite(card):
    try:
        attack = next(a for a in card.attacks if a.name.lower().startswith("bite"))
        runtime = compile_combatant(adapt_monster_mechanics_2014(card))
        compiled = next(a for a in [runtime.weapon_attack, *runtime.alternate_weapon_attacks]
                        if a is not None and a.weapon.name.lower().startswith("bite"))
        return attack, runtime, compiled
    except Exception:
        logger.exception("Failed to compile printed typed-drain attack on %s.", card.id)
        raise


def test_entire_327_catalog_uses_same_source_proven_typed_drain():
    try:
        cards = _source()
        assert len(cards) == 327
        matches = {
            card.id: attack.id
            for card in cards.values()
            for attack in card.attacks
            if source_proven_typed_drain_2014(card, attack) is not None
        }
        assert matches == {"vampire": "bite-bat-or-vampire-form-only", "vampire-spawn": "bite"}
        for id_, dice, regen in (("vampire", 3, 20), ("vampire-spawn", 2, 10)):
            card = cards[id_]
            immutable = card.model_dump_json()
            attack, template, compiled = _bite(card)
            assert not attack.source_complete
            assert source_completed_mixed_attack_2014(card, attack).source_complete
            assert compiled.target_qualification.any_of == [
                "source_grappled", "incapacitated", "restrained", "willing",
            ]
            assert compiled.on_hit_typed_drain.damage_type == DamageType.NECROTIC
            row = next(x for x in template_row(template)["attacks"] if x["id"] == compiled.id)
            assert row["targetQualification"]["anyOf"] == compiled.target_qualification.any_of
            assert row["onHitTypedDrain"]["damageType"] == "necrotic"
            assert row["onHitTypedDrain"]["zeroMaximumHpKills"] is True
            rider = next(x for x in row["onHitDamage"] if x["damageType"] == "necrotic")
            assert (rider["diceCount"], rider["diceSize"]) == (dice, 6)
            assert template.regeneration.amount == regen
            assert "attack:incomplete" not in basic_blockers_2014(card)
            assert card.model_dump_json() == immutable
    except Exception:
        logger.exception("Source family matching or compilation regression failed.")
        raise


def test_maximum_hp_zero_kill_is_distinct_from_ordinary_hp_death():
    try:
        card = _source()["vampire-spawn"]
        _, template, attack = _bite(card)
        caster = build_combatant_state(template)
        recipient = build_combatant_state(build_goblin_warrior())
        recipient.hit_point_maximum_reduction = recipient.template.max_hp - 1
        necrotic = [DamageRollComponent(
            source="renamed-bite", notation="2d6", rolls=[2, 3],
            damage_type=DamageType.NECROTIC, total=5, applied_total=5,
        )]
        transferred = apply_on_hit_typed_drain(caster, recipient, attack, necrotic)
        assert transferred.killed_by_zero_maximum
        assert recipient.is_dead
        assert recipient.current_hp == 0
        already_dead = build_combatant_state(build_goblin_warrior())
        already_dead.is_dead = True
        already_dead.is_alive = False
        already_dead.current_hp = 0
        already_dead.hit_point_maximum_reduction = already_dead.template.max_hp - 1
        transferred_dead = apply_on_hit_typed_drain(caster, already_dead, attack, necrotic)
        assert transferred_dead.killed_by_zero_maximum is False
    except Exception:
        logger.exception("Failed maximum-HP-specific terminal outcome regression.")
        raise


def test_damage_components_target_legality_renaming_and_source_mutation():
    try:
        card = _source()["vampire-spawn"]
        attack, template, compiled = _bite(card)
        actor = build_combatant_state(template)
        actor.current_hp -= 15
        target = build_combatant_state(build_goblin_warrior())
        assert not attack_allowed_against(compiled, "synthetic-drainer", target)
        target.active_effect_ids.append("restrained")
        assert attack_allowed_against(compiled, "synthetic-drainer", target)
        target.active_effect_ids.clear()
        target.willing_attack_source_ids.append("synthetic-drainer")
        assert attack_allowed_against(compiled, "synthetic-drainer", target)
        target.willing_attack_source_ids.clear()
        rows = [
            DamageRollComponent(source="typed", notation="1d6", rolls=[3],
                                damage_type=DamageType.PIERCING, total=3, applied_total=3),
            DamageRollComponent(source="typed", notation="2d6", rolls=[5, 4],
                                damage_type=DamageType.NECROTIC, total=9, applied_total=4),
        ]
        result = apply_on_hit_typed_drain(actor, target, compiled, rows)
        assert result.damage_taken == 4
        assert result.max_hp_reduced == 4
        assert result.attacker_healed == 4
        assert actor.current_hp == template.max_hp - 11
        assert target.hit_point_maximum_reduction == 4
        assert target.template.max_hp == build_goblin_warrior().max_hp
        renamed = card.model_copy(update={"id": "another-source", "name": "Another Source"})
        assert source_proven_typed_drain_2014(renamed, attack) is not None
        for before, after in (
            ("necrotic damage taken", "piercing damage taken"),
            ("regains hit points", "loses hit points"),
            ("creature that is grappled by", "creature that sees"),
        ):
            mutated = card.model_copy(update={
                "source_actions": card.source_actions.replace(before, after),
            })
            assert mutated.source_actions != card.source_actions
            assert source_proven_typed_drain_2014(mutated, attack) is None
    except Exception:
        logger.exception("Typed drain source mutation or state lifecycle failed.")
        raise
