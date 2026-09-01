import pytest

from app.content.audited_barbarian_profile import build_rokhan_stonefury_profile
from app.content.audited_fighter_profile import build_karnok_stoneward_profile
from app.content.canonical_hero_policy import (
    assert_canonical_identity,
    assert_canonical_profile_policy,
    canonical_melee_loadout,
    canonical_spell_package,
    canonical_subclass_id,
    canonical_template_id,
    combat_feature_audits,
)
from app.content.fighter_progression_profile import (
    build_karnok_stoneward_level2_profile,
    build_karnok_stoneward_level3_profile,
    build_karnok_stoneward_level4_profile,
    build_karnok_stoneward_level5_profile,
)
from app.content.hero_progressions import CANONICAL_HEROES, COMBAT_MODE_BY_CLASS, COMBAT_PLAN_BY_CLASS
from app.domain.character_builds import FeatureAudit


def test_every_class_has_one_persistent_canonical_identity() -> None:
    assert len(CANONICAL_HEROES) == 12
    assert len({hero.class_id for hero in CANONICAL_HEROES}) == 12
    assert len({hero.hero_name for hero in CANONICAL_HEROES}) == 12
    assert set(COMBAT_MODE_BY_CLASS) == {hero.class_id for hero in CANONICAL_HEROES}
    assert set(COMBAT_PLAN_BY_CLASS) == {hero.class_id for hero in CANONICAL_HEROES}

    for hero in CANONICAL_HEROES:
        plan = COMBAT_PLAN_BY_CLASS[hero.class_id]
        assert plan.class_id == hero.class_id
        assert plan.mode == COMBAT_MODE_BY_CLASS[hero.class_id]
        level_ids = [canonical_template_id(hero.class_id, level) for level in range(1, 21)]
        slug = hero.hero_name.lower().replace(" ", "-")
        assert level_ids == [f"{slug}-l{level}" for level in range(1, 21)]
        assert_canonical_identity(hero.class_id, hero.hero_name, 1)
        assert_canonical_identity(hero.class_id, hero.hero_name, 20)


def test_class_combat_modes_are_simple_and_repeatable() -> None:
    assert COMBAT_MODE_BY_CLASS["fighter"] == "melee"
    assert COMBAT_MODE_BY_CLASS["rogue"] == "melee"
    assert COMBAT_MODE_BY_CLASS["wizard"] == "caster"
    assert COMBAT_MODE_BY_CLASS["cleric"] == "caster"
    assert COMBAT_MODE_BY_CLASS["paladin"] == "hybrid"
    assert COMBAT_MODE_BY_CLASS["ranger"] == "hybrid"
    assert COMBAT_PLAN_BY_CLASS["monk"].forced_melee_kind == "unarmed"


def test_existing_certified_melee_progressions_use_shared_loadout_policy() -> None:
    profiles = [
        build_karnok_stoneward_profile(),
        build_karnok_stoneward_level2_profile(),
        build_karnok_stoneward_level3_profile(),
        build_karnok_stoneward_level4_profile(),
        build_karnok_stoneward_level5_profile(),
        build_rokhan_stonefury_profile(),
    ]
    for profile in profiles:
        loadout = canonical_melee_loadout(profile)
        assert loadout is not None
        assert loadout.kind == "two-handed"
        assert profile.combat_loadout_kind == "two-handed"
        assert_canonical_profile_policy(profile)


def test_canonical_policy_rejects_loadout_drift() -> None:
    profile = build_karnok_stoneward_profile()
    profile.combat_loadout_kind = "one-hander-shield"
    with pytest.raises(ValueError, match="canonical loadout drifted"):
        assert_canonical_profile_policy(profile)


def test_canonical_identity_rejects_alternate_same_class_character() -> None:
    with pytest.raises(ValueError, match="must progress as Karnok Stoneward"):
        assert_canonical_identity("fighter", "Different Fighter", 6)


def test_subclass_identity_is_fixed_once_it_unlocks() -> None:
    assert canonical_subclass_id("fighter", 1) is None
    assert canonical_subclass_id("fighter", 2) is None
    assert canonical_subclass_id("fighter", 3) == "champion"
    assert canonical_subclass_id("fighter", 20) == "champion"


def test_noncombat_features_are_excluded_from_runtime_automation_scope() -> None:
    audits = [
        FeatureAudit(
            feature_id="combat-feature", feature_name="Combat Feature",
            source_reference="SRD combat source", category="class",
            combat_relevant=True, automated=True,
        ),
        FeatureAudit(
            feature_id="ribbon-feature", feature_name="Ribbon Feature",
            source_reference="SRD exploration source", category="class",
            combat_relevant=False, automated=False,
        ),
    ]
    assert [audit.feature_id for audit in combat_feature_audits(audits)] == ["combat-feature"]


def test_same_class_and_level_reuses_same_spell_package() -> None:
    first = canonical_spell_package("wizard", 1)
    second = canonical_spell_package("wizard", 1)
    assert first == second
    assert first is not None
    assert [spell.name for spell in first.spells] == [
        "Mage Armor", "Magic Missile", "Sleep", "Thunderwave",
    ]


def test_noncasters_do_not_receive_a_spell_package() -> None:
    assert canonical_spell_package("fighter", 5) is None


def test_incomplete_higher_level_spell_package_fails_closed() -> None:
    with pytest.raises(ValueError, match="canonical package is incomplete"):
        canonical_spell_package("wizard", 2)
