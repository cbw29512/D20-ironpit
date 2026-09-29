from __future__ import annotations

import json

from app.content.audited_cleric import build_seraphine_dawnshield_level
from app.content.certified_heroes import build_certified_hero_templates_for_ruleset


def _serialized_text(value: object) -> str:
    try:
        if hasattr(value, "model_dump"):
            value = value.model_dump(mode="json")
        return json.dumps(value, sort_keys=True).casefold()
    except Exception as exc:
        raise RuntimeError("Certified 2024 spell provenance could not be serialized.") from exc


def test_certified_2024_runtime_never_embeds_2014_or_legacy_spell_provenance() -> None:
    """A same-name spell may reuse universal mechanics, but never a legacy spell contract."""
    templates = build_certified_hero_templates_for_ruleset("2024")

    for template in templates:
        payload = _serialized_text(template)
        assert "basic rules 2014" not in payload, template.id
        assert "legacy spell" not in payload, template.id
        assert "legacy:" not in payload, template.id


def test_2024_cleric_changed_spell_fingerprints_do_not_regress_to_2014() -> None:
    """Lock known 2024 spell rewrites to their 2024 mechanics rather than spell names."""
    level_one = build_seraphine_dawnshield_level(1)
    cure = next(item for item in level_one.healing_actions if item.id == "cure-wounds")
    assert (cure.dice_count, cure.dice_size) == (2, 8)
    assert cure.excluded_creature_types == []

    level_two = build_seraphine_dawnshield_level(2)
    word = next(item for item in level_two.healing_actions if item.id == "healing-word")
    assert (word.dice_count, word.dice_size) == (2, 4)
    assert word.excluded_creature_types == []

    level_four = build_seraphine_dawnshield_level(4)
    inflict = next(item for item in level_four.spell_save_actions if item.id == "inflict-wounds")
    assert inflict.save_ability == "constitution"
    assert (inflict.damage_dice_count, inflict.damage_dice_size) == (2, 10)
    assert inflict.success_damage == "half"
    assert all(item.id != "inflict-wounds" for item in level_four.spell_attack_actions)

    level_five = build_seraphine_dawnshield_level(5)
    mass_word = next(item for item in level_five.healing_actions if item.id == "mass-healing-word")
    assert (mass_word.dice_count, mass_word.dice_size) == (2, 4)
    assert mass_word.max_targets == 6
    assert mass_word.excluded_creature_types == []

    level_nine = build_seraphine_dawnshield_level(9)
    mass_cure = next(item for item in level_nine.healing_actions if item.id == "mass-cure-wounds")
    assert (mass_cure.dice_count, mass_cure.dice_size) == (5, 8)
    assert mass_cure.max_targets == 6
    assert mass_cure.excluded_creature_types == []
