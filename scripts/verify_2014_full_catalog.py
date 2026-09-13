from __future__ import annotations

from app.content.monster_catalog_2014 import compile_monster_2014, load_catalog_2014, unsupported_mechanics_2014

EXPECTED_COUNT = 327
REQUIRED_ABILITIES = {"str", "dex", "con", "int", "wis", "cha"}


def main() -> int:
    monsters = load_catalog_2014()
    if len(monsters) != EXPECTED_COUNT:
        raise RuntimeError(f"Expected {EXPECTED_COUNT} 2014 monsters, found {len(monsters)}.")
    ids = [monster.id for monster in monsters]
    if len(ids) != len(set(ids)):
        raise RuntimeError("2014 catalog contains duplicate monster ids.")

    runnable = 0
    blocked = 0
    for monster in monsters:
        if monster.armor_class < 1 or monster.max_hp < 1:
            raise RuntimeError(f"Invalid core combat stats for {monster.name}.")
        if set(monster.abilities) != REQUIRED_ABILITIES:
            raise RuntimeError(f"Incomplete ability scores for {monster.name}.")
        blockers = unsupported_mechanics_2014(monster)
        if blockers:
            blocked += 1
            continue
        compile_monster_2014(monster)
        runnable += 1

    print(f"2014 catalog verified: {len(monsters)}/{EXPECTED_COUNT}")
    print(f"Immediately runnable through current universal engine: {runnable}")
    print(f"Blocked pending reusable mechanics: {blocked}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
