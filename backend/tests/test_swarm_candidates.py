from app.content.monster_bonus_action_source_audit import complete_monster_bonus_action_fingerprints
from app.content.monster_catalog import load_monster_rows
from app.content.monster_legendary_source_audit import complete_monster_legendary_fingerprints
from app.content.monster_limited_use_source_audit import complete_monster_limited_use_fingerprints
from app.content.monster_reaction_source_audit import complete_monster_reaction_fingerprints
from app.content.monster_saving_throws import complete_monster_saving_throws
from app.content.monster_source_audit import audit_monster_source
from app.content.monster_spellcasting_source_audit import complete_monster_spellcasting_fingerprints
from app.content.monster_trait_source_audit import complete_monster_trait_fingerprints
from app.content.monsters_swarms import build_swarm_candidates
from app.content.unarmed_opportunity_profiles import complete_unarmed_opportunity_profiles
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
        "Swarm of Bats", "Swarm of Rats", "Swarm of Crawling Claws",
    ]
    for swarm in candidates:
        assert audit_monster_source(swarm, rows[swarm.name]) == []
        assert CombatTrait.SWARM in swarm.combat_traits
        assert swarm.source_trait_names == ["Swarm"]
        conditional = swarm.weapon_attack.conditional_damage[0]
        assert conditional.trigger == "attacker_bloodied"
        assert conditional.mode == "replace_weapon"


def test_crawling_claws_preserves_medium_prone_rider() -> None:
    claws = next(item for item in _candidates() if item.name == "Swarm of Crawling Claws")
    assert claws.weapon_attack.knocks_prone_max_size.value == "medium"
