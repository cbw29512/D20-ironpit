import pytest

from app.content.canonical_hero_policy import (
    assert_canonical_identity,
    canonical_spell_package,
    canonical_subclass_id,
    canonical_template_id,
    combat_feature_audits,
)
from app.content.hero_progressions import CANONICAL_HEROES
from app.domain.character_builds import FeatureAudit


def test_every_class_has_one_persistent_canonical_identity() -> None:
    assert len(CANONICAL_HEROES) == 12
    assert len({hero.class_id for hero in CANONICAL_HEROES}) == 12
    assert len({hero.hero_name for hero in CANONICAL_HEROES}) == 12

    for hero in CANONICAL_HEROES:
        level_ids = [canonical_template_id(hero.class_id, level) for level in range(1, 21)]
        slug = hero.hero_name.lower().replace(" ", "-")
        assert level_ids == [f"{slug}-l{level}" for level in range(1, 21)]
        assert_canonical_identity(hero.class_id, hero.hero_name, 1)
        assert_canonical_identity(hero.class_id, hero.hero_name, 20)


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
            feature_id="combat-feature",
            feature_name="Combat Feature",
            source_reference="SRD combat source",
            category="class",
            combat_relevant=True,
            automated=True,
        ),
        FeatureAudit(
            feature_id="ribbon-feature",
            feature_name="Ribbon Feature",
            source_reference="SRD exploration source",
            category="class",
            combat_relevant=False,
            automated=False,
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
