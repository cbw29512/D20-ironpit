"""2014 source complete Erinyes using universal weapon, save and poison rules."""
from __future__ import annotations

from app.combat.on_hit_condition_save import resolve_on_hit_condition_save
from app.combat.condition_removal import remove_condition
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.demo import build_demo_fighter
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_included_weapon_traits_2014 import (
    included_weapon_trait_names_2014, weapon_damage_source_qualifiers_2014,
)
from app.content.monster_mixed_damage_2014 import source_completed_mixed_attack_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.encounters import EncounterCombatant
from app.domain.weapons import DamageSourceQualifier
from scripts.browser_template_serializer import template_row


def _source():
    return next(x for x in load_monster_source_2014() if x.id == "erinyes")


def _bow(source):
    return next(a for a in source.attacks if a.id == "longbow")


def test_source_poisons_with_one_save_and_never_adds_duplicate_poison_damage() -> None:
    monster = _source()
    before = monster.model_dump_json()
    source_bow = _bow(monster)
    assert not source_bow.source_complete
    assert source_bow.on_hit_save_effect is None
    fixed = source_completed_mixed_attack_2014(monster, source_bow)
    assert fixed.source_complete
    assert fixed.damage == source_bow.damage
    assert fixed.on_hit_damage == source_bow.on_hit_damage
    assert fixed.on_hit_save_effect == {
        "save_ability": "constitution", "dc": 14, "condition_id": "poisoned",
    }
    assert fixed.on_hit_damage == [{
        "average": 13, "dice_count": 3, "dice_size": 8, "bonus": 0, "type": "poison",
    }]
    assert monster.model_dump_json() == before


def test_hellish_weapon_magical_tags_and_exact_source_admission() -> None:
    monster = _source()
    assert "Hellish Weapons" in included_weapon_trait_names_2014(monster)
    assert DamageSourceQualifier.MAGICAL in weapon_damage_source_qualifiers_2014(monster)
    assert basic_blockers_2014(monster) == ()
    template = compile_combatant(adapt_basic_monster_2014(monster))
    assert "Hellish Weapons" in template.source_trait_names
    attacks = [template.weapon_attack, *template.alternate_weapon_attacks]
    bow = next(a for a in attacks if a.weapon.name == "Longbow")
    assert bow.on_hit_condition_save is not None
    assert (bow.on_hit_condition_save.dc, bow.on_hit_condition_save.condition_id) == (14, "poisoned")
    assert bow.on_hit_condition_save.duration_rounds is None
    assert bow.on_hit_condition_save.repeat_save_timing is None
    assert DamageSourceQualifier.MAGICAL in bow.damage_source_qualifiers
    browser = template_row(template)
    emitted = next(a for a in browser["attacks"] if a["name"] == "Longbow")
    assert emitted["onHitConditionSave"]["conditionId"] == "poisoned"
    assert emitted["onHitConditionSave"]["dc"] == 14
    assert "durationRounds" not in emitted["onHitConditionSave"]
    assert "repeatSaveTiming" not in emitted["onHitConditionSave"]
    assert emitted["damageSourceQualifiers"] == ["magical"]


def test_failed_save_persists_until_shared_condition_removal_no_timer() -> None:
    template = compile_combatant(adapt_basic_monster_2014(_source()))
    bow = next(a for a in [template.weapon_attack, *template.alternate_weapon_attacks]
               if a.weapon.name == "Longbow")
    target = build_combatant_state(build_demo_fighter())
    failed = resolve_on_hit_condition_save(
        target, bow, FixedDiceProvider([1]),
        template, source_id="source", round_number=1,
    )
    assert failed.save_succeeded is False and failed.applied_condition == "poisoned"
    assert "poisoned" in target.active_effect_ids
    assert not target.timed_effects
    remove_condition(EncounterCombatant(
        combatant_id="target", side="heroes", position_ft=5, state=target,
    ), "poisoned")
    assert "poisoned" not in target.active_effect_ids
    fresh = build_combatant_state(target.template)
    assert "poisoned" not in fresh.active_effect_ids


def test_changed_source_save_and_other_unverified_riders_stay_blocked() -> None:
    source = _source()
    for before, after in (
        ("DC 14 Constitution", "DC 15 Constitution"),
        ("lesser restoration spell or similar magic", "the end of its next turn"),
        ("piercing damage plus 13 (3d8) poison damage", "piercing damage plus 13 (3d8) fire damage"),
    ):
        changed = source.model_copy(update={
            "source_actions": source.source_actions.replace(before, after),
        })
        assert changed.source_actions != source.source_actions
        assert not source_completed_mixed_attack_2014(changed, _bow(changed)).source_complete
        assert "attack:incomplete" in basic_blockers_2014(changed)


def test_printed_hellish_clause_drift_cannot_add_magical_attacks() -> None:
    source = _source()
    mutated = source.model_copy(update={
        "source_traits": source.source_traits.replace(
            "weapon attacks are magical", "weapon attacks are nonmagical"
        ),
    })
    assert "Hellish Weapons" not in included_weapon_trait_names_2014(mutated)
    assert "source:trait" in basic_blockers_2014(mutated)
