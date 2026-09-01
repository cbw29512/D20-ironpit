from app.content.canonical_hero_policy import (
    CASTER_CLASS_IDS,
    canonical_spell_package,
    canonical_template_id,
)
from app.content.certified_heroes import build_certified_hero_entries
from app.content.hero_progressions import HERO_BY_CLASS


def test_every_certified_level_belongs_to_the_same_canonical_hero() -> None:
    for (class_id, level, build_id), template in build_certified_hero_entries():
        hero = HERO_BY_CLASS[class_id]
        assert build_id == "canonical"
        assert template.name == hero.hero_name
        assert template.id == canonical_template_id(class_id, level)


def test_certified_casters_must_use_complete_shared_class_package() -> None:
    for (class_id, level, _), _template in build_certified_hero_entries():
        if class_id not in CASTER_CLASS_IDS:
            continue
        package = canonical_spell_package(class_id, level)
        assert package is not None
        assert package.class_id == class_id
