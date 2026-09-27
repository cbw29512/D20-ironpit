from __future__ import annotations

from app.content.sorcerer_2014_spell_package import build_sorcerer_2014_spell_package
from app.content.sorcerer_draconic_2014_runtime import build_nyra_emberveil_2014


def _runtime_spell_ids(hero) -> set[str]:
    return {
        *(item.id for item in hero.spell_attack_actions),
        *(item.id for item in hero.spell_save_actions),
        *(item.id for item in hero.auto_hit_spell_actions),
        *(item.id for item in hero.defensive_spell_actions),
        *(item.id for item in hero.effect_removal_actions),
    }


def test_every_combat_facing_known_spell_has_a_runtime_binding() -> None:
    for level in range(1, 21):
        hero = build_nyra_emberveil_2014(level)
        package = build_sorcerer_2014_spell_package(level)
        runtime_ids = _runtime_spell_ids(hero)

        choices = [*package.cantrips, *package.spells]
        missing = [
            item.id
            for item in choices
            if "arena-out-of-scope" not in item.required_capabilities
            and item.id not in runtime_ids
        ]
        assert missing == [], f"level {level} known combat spells missing runtime bindings: {missing}"


def test_runtime_spell_actions_do_not_leak_future_known_spells() -> None:
    for level in range(1, 21):
        hero = build_nyra_emberveil_2014(level)
        package = build_sorcerer_2014_spell_package(level)
        known_ids = {
            item.id
            for item in [*package.cantrips, *package.spells]
            if "arena-out-of-scope" not in item.required_capabilities
        }
        runtime_ids = _runtime_spell_ids(hero)
        assert runtime_ids <= known_ids, (
            f"level {level} runtime exposes spells not yet known: {sorted(runtime_ids - known_ids)}"
        )
