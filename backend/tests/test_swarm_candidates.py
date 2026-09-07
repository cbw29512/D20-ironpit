from app.content.monster_bonus_action_source_audit import complete_monster_bonus_action_fingerprints
from app.content.monster_catalog import build_monster_catalog, load_monster_rows
from app.content.monster_legendary_source_audit import complete_monster_legendary_fingerprints
from app.content.monster_limited_use_source_audit import complete_monster_limited_use_fingerprints
from app.content.monster_reaction_source_audit import complete_monster_reaction_fingerprints
from app.content.monster_saving_throws import complete_monster_saving_throws
from app.content.monster_source_audit import audit_monster_source
from app.content.monster_spellcasting_source_audit import complete_monster_spellcasting_fingerprints
from app.content.monster_trait_source_audit import complete_monster_trait_fingerprints
from app.content.monsters_swarms import build_swarm_candidates
from app.content.unarmed_opportunity_profiles import complete_unarmed_opportunity_profiles
from app.domain.catalog import CoverageStatus
from app.domain.traits import CombatTrait


def _candidates():
    monsters = build_swarm_candidates()
    monsters = complete_monster_trait_fingerprints(monsters)
    monsters = complete_monster_reaction_fingerprints(monsters)
    monsters = complete_monster_bonus_action_fingerprints(monsters)
    monsters = complete_monster_limited_use_fingerprints(monsters)
    monsters = complete_monster_legendary_fingerprints(monsters)
    monsters = complete_monster_spellcasting_fingerprints(monsters)
    monsters = complete_monster_saving_throws(monsters)
    return complete_unarmed_opportunity_profiles(monsters)


def test_clean_swarm_candidates_pass_full_srd_source_audit() -> None:
    rows = {row["name"]: row for row in load_monster_rows()}
    candidates = _candidates()
    assert [item.name for item in candidates] == [
        "Swarm of Bats", "Swarm of Rats", "Swarm of Crawling Claws", "Swarm of Piranhas",
    ]
    for swarm in candidates:
        assert audit_monster_source(swarm, rows[swarm.name]) == []
        assert CombatTrait.SWARM in swarm.combat_traits
        assert "Swarm" in swarm.source_trait_names
        conditional = swarm.weapon_attack.conditional_damage[0]
        assert conditional.trigger == "attacker_bloodied"
        assert conditional.mode == "replace_weapon"


def test_crawling_claws_preserves_medium_prone_rider() -> None:
    claws = next(item for item in _candidates() if item.name == "Swarm of Crawling Claws")
    assert claws.weapon_attack.knocks_prone_max_size.value == "medium"


def test_swarm_of_piranhas_composes_existing_swarm_bloodied_and_injured_target_math() -> None:
    piranhas = next(item for item in _candidates() if item.name == "Swarm of Piranhas")
    attack = piranhas.weapon_attack
    conditional = attack.conditional_damage[0]

    assert piranhas.source_trait_names == ["Swarm", "Water Breathing"]
    assert attack.advantage_if_target_missing_hp is True
    assert (attack.attack_bonus, attack.weapon.dice_count, attack.weapon.dice_size, attack.damage_bonus) == (5, 2, 4, 3)
    assert (conditional.dice_count, conditional.dice_size, conditional.damage_bonus, conditional.damage_type.value) == (1, 4, 3, "piercing")


def test_swarm_of_piranhas_is_raw_ready_after_existing_capability_composition() -> None:
    card = next(card for card in build_monster_catalog() if card.name == "Swarm of Piranhas")
    assert card.coverage_status is CoverageStatus.RAW_READY
    assert card.runnable_template_id == "srd-swarm-of-piranhas"
    assert card.blockers == []
