from app.combat.concentration import end_concentration
from app.combat.condition_rules import has_condition
from app.combat.modifier_stack import attacks_against_advantage_sources, invisibility_suppressed
from app.combat.spell_modifiers import apply_failed_save_spell_modifiers, start_save_spell_concentration
from app.combat.state import build_combatant_state
from app.content.demo import build_goblin_warrior
from app.content.monster_catalog_2014 import load_catalog_2014, monster_by_id_2014
from app.content.shared_spell_actions_2014 import build_faerie_fire


def test_faerie_fire_is_one_shared_spell_with_caster_dc() -> None:
    first = build_faerie_fire(13)
    second = build_faerie_fire(17)

    assert first.dc == 13 and second.dc == 17
    assert first.area is not None
    assert (first.range_ft, first.area.shape, first.area.origin, first.area.length_ft) == (60, "cube", "point", 20)
    assert first.concentration is True and first.duration_minutes == 1
    assert [effect.kind for effect in first.failure_modifier_effects] == [
        "attacks-against-advantage", "invisibility-suppressed",
    ]


def test_drider_uses_shared_faerie_fire_and_its_own_dc_resource() -> None:
    source = next(monster for monster in load_catalog_2014() if monster.id == "drider")
    template = monster_by_id_2014("drider")
    spell = next(action for action in template.spell_save_actions if action.id == "faerie-fire")

    assert source.innate_spellcasting is not None
    assert spell.dc == source.innate_spellcasting.save_dc
    assert any(resource.id == "innate-faerie-fire" and resource.max_uses == 1 for resource in template.resources)


def test_faerie_fire_failed_save_modifiers_end_with_concentration() -> None:
    owner = build_combatant_state(build_goblin_warrior())
    target = build_combatant_state(build_goblin_warrior())
    target.active_effect_ids.append("invisible")
    spell = build_faerie_fire(13)
    states = [owner, target]

    start_save_spell_concentration(owner, "caster", spell, 1, states)
    apply_failed_save_spell_modifiers("target", target, "caster", spell, 1)

    assert attacks_against_advantage_sources(target) == 1
    assert invisibility_suppressed(target) is True
    assert has_condition(target, "invisible") is False

    assert end_concentration(owner, states) is True
    assert attacks_against_advantage_sources(target) == 0
    assert invisibility_suppressed(target) is False
    assert has_condition(target, "invisible") is True
