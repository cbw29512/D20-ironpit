from app.content.canonical_spell_policy import canonical_spell_package
from app.content.cleric_life_2014_runtime import build_seraphine_dawnshield_2014
from app.content.grapple_escape_skill_bonuses import complete_template_grapple_escape_skills
from app.content.pregen_2014_roster_audit import (
    EXPECTED_2014_SNAPSHOTS,
    audit_2014_pregen_roster,
)


def test_canonical_policy_routes_2014_wizard_and_druid_packages() -> None:
    wizard = canonical_spell_package("wizard", 1, "2014", 3)
    druid = canonical_spell_package("druid", 1, "2014", 3)

    assert wizard is not None
    assert wizard.class_id == "wizard"
    assert {spell.id for spell in wizard.cantrips} >= {"fire-bolt", "poison-spray"}
    assert druid is not None
    assert druid.class_id == "druid"
    assert {spell.id for spell in druid.cantrips} >= {"produce-flame", "poison-spray"}


def test_2014_pregen_roster_audit_checks_every_registered_snapshot() -> None:
    rows = audit_2014_pregen_roster()
    by_class = {row.class_id for row in rows}
    levels_by_class = {
        class_id: sorted(row.level for row in rows if row.class_id == class_id)
        for class_id in by_class
    }

    assert len(rows) == EXPECTED_2014_SNAPSHOTS
    assert all(row.checked for row in rows)
    assert by_class == {
        "barbarian", "bard", "cleric", "druid", "fighter", "monk",
        "paladin", "ranger", "rogue", "sorcerer", "warlock", "wizard",
    }
    assert all(levels == list(range(1, 21)) for levels in levels_by_class.values())
    assert all(row.passed for row in rows)
    assert all(not row.unsupported_mechanics for row in rows)
    assert not any(
        "combat-skill-bonuses-mismatch" in row.unsupported_mechanics
        for row in rows
    )


def test_untrained_grapple_skills_do_not_rewrite_printed_proficiencies() -> None:
    raw = build_seraphine_dawnshield_2014(1)
    completed = complete_template_grapple_escape_skills(raw)
    assert raw.skill_bonuses == {
        "insight": 5, "religion": 1, "medicine": 5, "persuasion": 3,
    }
    assert completed.skill_bonuses == {
        "insight": 5, "religion": 1, "medicine": 5, "persuasion": 3,
        "athletics": 1, "acrobatics": 0,
    }
