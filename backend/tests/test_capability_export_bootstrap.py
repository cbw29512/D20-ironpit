from app.content.capability_from_template import definition_from_template
from app.content.capability_registry import get_capability_definition
from app.content.legacy_monster_roster import build_legacy_monster_templates


_MIGRATED_IDS = {
    "srd-wolf",
    "srd-dire-wolf",
    "srd-giant-constrictor-snake",
}


def test_export_only_sources_match_migrated_capability_definitions() -> None:
    sources = {
        template.id: template
        for template in build_legacy_monster_templates(include_capability_migrated=False)
        if template.id in _MIGRATED_IDS
    }
    assert set(sources) == _MIGRATED_IDS
    for template_id, template in sources.items():
        assert template.ruleset == "2024"
        assert definition_from_template(template) == get_capability_definition(template_id)
