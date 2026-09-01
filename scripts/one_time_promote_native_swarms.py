from __future__ import annotations

from pathlib import Path


def _replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if new in text:
        return
    if old not in text:
        raise RuntimeError(f"Promotion marker missing from {path}: {old!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def main() -> None:
    _replace_once(
        Path("backend/tests/test_arena_roster.py"),
        '        "srd-bandit-captain", "srd-knight", "srd-noble", "srd-warrior-veteran",\n    ]',
        '        "srd-bandit-captain", "srd-knight", "srd-noble", "srd-warrior-veteran",\n        "srd-swarm-of-insects", "srd-swarm-of-venomous-snakes",\n    ]',
    )
    _replace_once(
        Path("backend/tests/test_full_content_catalog.py"),
        "    assert len(ready_monsters) == 99",
        "    assert len(ready_monsters) == 101",
    )
    _replace_once(
        Path("backend/tests/test_full_content_catalog.py"),
        '        "Spider": "srd-spider", "Swarm of Bats": "srd-swarm-of-bats",\n        "Swarm of Crawling Claws": "srd-swarm-of-crawling-claws", "Swarm of Rats": "srd-swarm-of-rats",',
        '        "Spider": "srd-spider", "Swarm of Bats": "srd-swarm-of-bats",\n        "Swarm of Crawling Claws": "srd-swarm-of-crawling-claws", "Swarm of Insects": "srd-swarm-of-insects",\n        "Swarm of Rats": "srd-swarm-of-rats", "Swarm of Venomous Snakes": "srd-swarm-of-venomous-snakes",',
    )
    _replace_once(
        Path("backend/tests/test_figure_profiles.py"),
        "    assert len(ready_names) == 99",
        "    assert len(ready_names) == 101",
    )
    _replace_once(
        Path("backend/tests/test_figure_profiles.py"),
        '        "Swarm of Crawling Claws": "swarm",\n        "Swarm of Rats": "swarm",',
        '        "Swarm of Crawling Claws": "swarm",\n        "Swarm of Insects": "swarm",\n        "Swarm of Rats": "swarm",\n        "Swarm of Venomous Snakes": "swarm",',
    )
    _replace_once(
        Path("backend/tests/test_figure_profiles.py"),
        '        "Swarm of Crawling Claws": "crawling-claws",\n        "Swarm of Rats": "rats",',
        '        "Swarm of Crawling Claws": "crawling-claws",\n        "Swarm of Insects": "insects",\n        "Swarm of Rats": "rats",\n        "Swarm of Venomous Snakes": "venomous-snakes",',
    )
    _replace_once(
        Path("backend/tests/test_monster_source_audit.py"),
        "    assert len(ready) == 99",
        "    assert len(ready) == 101",
    )

    browser = Path("frontend/browser-generated-monsters.test.cjs")
    _replace_once(browser, "Object.keys(generated).length, 99", "Object.keys(generated).length, 101")
    _replace_once(
        browser,
        '  "srd-swarm-of-bats", "srd-swarm-of-rats", "srd-swarm-of-crawling-claws",',
        '  "srd-swarm-of-bats", "srd-swarm-of-rats", "srd-swarm-of-crawling-claws",\n  "srd-swarm-of-insects", "srd-swarm-of-venomous-snakes",',
    )
    marker = 'assert.equal(generated["srd-swarm-of-crawling-claws"].attacks[0].proneMaxSize, "medium");'
    assertions = marker + '''
const insectSwarm = generated["srd-swarm-of-insects"];
assert.deepEqual(insectSwarm.source_trait_names, ["Spider Climb", "Swarm"]);
assert.equal(insectSwarm.traits.includes("swarm"), true);
assert.deepEqual(insectSwarm.movement_modes, {
  walk_ft: 20, fly_ft: 20, climb_ft: 0, swim_ft: 0, burrow_ft: 0, hover: false,
});
assert.deepEqual(insectSwarm.attacks[0].conditionalDamage, {
  trigger: "attacker_bloodied", mode: "replace_weapon", diceCount: 1, diceSize: 4,
  damageBonus: 1, damageType: "poison",
});
const snakeSwarm = generated["srd-swarm-of-venomous-snakes"];
assert.deepEqual(snakeSwarm.source_trait_names, ["Swarm"]);
assert.equal(snakeSwarm.traits.includes("swarm"), true);
assert.equal(snakeSwarm.movement_modes.swim_ft, 30);
assert.deepEqual(snakeSwarm.attacks[0].onHitDamage, [
  { source: "Poison", diceCount: 3, diceSize: 6, damageBonus: 0, damageType: "poison" },
]);
assert.deepEqual(snakeSwarm.attacks[0].conditionalDamage, {
  trigger: "attacker_bloodied", mode: "replace_weapon", diceCount: 1, diceSize: 4,
  damageBonus: 4, damageType: "piercing",
});'''
    _replace_once(browser, marker, assertions)
    _replace_once(
        browser,
        "Generated monster runtime contains 99 RAW-certified templates with Blood Hawk and Swarm conditional damage, Redirect Attack, and T. rex retargeting.",
        "Generated monster runtime contains 101 RAW-certified templates, including native data-only swarms, with conditional damage, Redirect Attack, and T. rex retargeting.",
    )


if __name__ == "__main__":
    main()
