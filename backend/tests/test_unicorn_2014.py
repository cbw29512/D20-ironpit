from app.content.capability_compiler import compile_combatant
from app.content.monster_basic_candidates_2014 import basic_blockers_2014, is_basic_candidate_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_legendary_bindings_2014 import legendary_action_options_2014
from app.content.monster_roster_2014 import build_basic_2014_monsters
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.weapons import DamageSourceQualifier


def _unicorn():
    return next(item for item in load_monster_source_2014() if item.id == "unicorn")


def test_unicorn_is_the_smallest_certified_2014_legendary_candidate() -> None:
    source = load_monster_source_2014()
    legendary = [
        monster for monster in source
        if monster.legendary_action_names or monster.legendary_action_uses
    ]
    ready = [monster for monster in legendary if is_basic_candidate_2014(monster)]
    assert ready, f"no legendary candidates; unicorn blockers={basic_blockers_2014(_unicorn())}"
    unicorn = next(item for item in ready if item.id == "unicorn")
    assert all(float(item.challenge_rating) >= float(unicorn.challenge_rating) for item in ready)


def test_unicorn_binds_printed_block_and_omits_pit_banned_teleport() -> None:
    monster = _unicorn()
    assert not basic_blockers_2014(monster)
    template = compile_combatant(adapt_basic_monster_2014(monster))
    assert template.id == "2014-unicorn"
    assert template.max_hp == 67
    assert template.armor_class == 12
    assert template.legendary_actions
    names = {item.name for item in template.legendary_actions}
    assert names == {"Hooves", "Shimmering Shield", "Heal Self"}
    assert {item.kind for item in template.legendary_actions} == {"attack", "ac_buff", "heal"}
    attack_ids = {template.weapon_attack.id, *(item.id for item in template.alternate_weapon_attacks)}
    assert "2014-unicorn-hooves" in attack_ids
    assert "2014-unicorn-horn" in attack_ids
    hooves = next(item for item in [template.weapon_attack, *template.alternate_weapon_attacks] if item.id == "2014-unicorn-hooves")
    assert DamageSourceQualifier.MAGICAL in hooves.damage_source_qualifiers
    assert any(item.id == "healing-touch" for item in template.healing_actions)
    assert {item.id for item in template.spell_save_actions} == {"entangle", "calm-emotions"}
    assert any(item.id == "dispel-evil-and-good" for item in template.timed_self_buff_actions)
    assert any(item.id == "break-enchantment" for item in template.condition_removal_actions)
    assert "legendary-actions" in {item.id for item in template.resources}
    assert "legendary-actions" in template.progression_features.start_turn_resource_refill_ids
    assert "Teleport" not in {item.name for item in template.healing_actions}
    assert not getattr(template, "teleport_actions", [])
    options = legendary_action_options_2014(monster)
    assert all("teleport" not in item.name.casefold() for item in options)


def test_2014_roster_includes_unicorn_at_current_roster() -> None:
    roster = build_basic_2014_monsters()
    assert len(roster) == 198
    unicorn = next(item for item in roster if item.id == "2014-unicorn")
    assert unicorn.source_legendary_action_names == [
        "Hooves",
        "Shimmering Shield (Costs 2 Actions)",
        "Heal Self (Costs 3 Actions)",
    ]