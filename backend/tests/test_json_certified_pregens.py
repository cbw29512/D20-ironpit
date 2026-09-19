from pathlib import Path

import pytest

from app.content.capability_compiler import compile_combatant
from app.content.certified_hero_progressions import CERTIFIED_HERO_PROGRESSIONS
from app.content.json_combatant_compiler import compile_hero_definition, fold_hero_level, load_hero_bundle


ROOT = Path(__file__).resolve().parents[2]


def _slug(template) -> str:
    name = template.name.lower().replace(" ", "-")
    return f"{name}-2014" if template.ruleset == "2014" else name


def _resource_map(template):
    return {item.id: item.max_uses for item in template.resources}


def _core(template):
    slots = None if template.attack_action is None else len(template.attack_action.slots)
    return {
        "id": template.id,
        "name": template.name,
        "level": template.level,
        "ruleset": template.ruleset,
        "armor_class": template.armor_class,
        "max_hp": template.max_hp,
        "speed_ft": template.speed_ft,
        "initiative_bonus": template.initiative_bonus,
        "resources": _resource_map(template),
        "skill_bonuses": template.skill_bonuses,
        "saving_throw_bonuses": template.saving_throw_bonuses,
        "primary_weapon": template.weapon_attack.weapon.id,
        "attack_bonus": template.weapon_attack.attack_bonus,
        "damage_bonus": template.weapon_attack.damage_bonus,
        "attack_slots": slots,
        "rage_damage_bonus": template.rage_damage_bonus,
        "combat_traits": [str(item) for item in template.combat_traits],
        "weapon_masteries": list(template.weapon_masteries or []),
        "fighting_style": template.fighting_style,
        "fighting_styles": list(template.fighting_styles or []),
        "progression": template.progression_features.model_dump(exclude_defaults=True),
        "ability_scores": None if template.ability_scores is None else template.ability_scores.model_dump(),
    }


def _cases():
    cases = []
    for progression in CERTIFIED_HERO_PROGRESSIONS:
        first = progression.template_builder(list(progression.levels)[0])
        cases.append((first.ruleset, progression.class_id, _slug(first), progression))
    return cases


@pytest.mark.parametrize("edition,class_id,slug,progression", _cases())
def test_certified_json_matches_python_core_combat_fields(edition, class_id, slug, progression):
    identity, class_prog, subclass, species, track, build = load_hero_bundle(ROOT, edition, slug)
    mismatches = {}
    for level in progression.levels:
        certified = progression.oracle(level)
        folded = fold_hero_level(class_prog, subclass, species, track, level)
        compiled = compile_combatant(compile_hero_definition(identity.id, identity.name, folded, build))
        left = _core(certified)
        right = _core(compiled)
        if left["ability_scores"] is None:
            for key in ("ability_scores", "skill_bonuses", "saving_throw_bonuses", "initiative_bonus"):
                left.pop(key, None)
                right.pop(key, None)
        diffs = {key: (left[key], right[key]) for key in left if left[key] != right[key]}
        if diffs:
            mismatches[level] = diffs
    assert mismatches == {}, f"{edition} {class_id} {slug}: {mismatches}"


def test_fighter_runtime_uses_json_and_keeps_python_oracle():
    fighters = [item for item in CERTIFIED_HERO_PROGRESSIONS if item.class_id == "fighter"]
    assert fighters
    for progression in fighters:
        assert progression.oracle_builder is not None
        assert progression.oracle_builder is not progression.template_builder
        runtime = progression.template_builder(list(progression.levels)[0])
        oracle = progression.oracle(list(progression.levels)[0])
        assert runtime.id == oracle.id
        assert runtime.max_hp == oracle.max_hp
        assert runtime.armor_class == oracle.armor_class
