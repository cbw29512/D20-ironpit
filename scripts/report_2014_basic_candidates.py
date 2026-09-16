from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.content.arena_neutral_bonus_actions import is_arena_neutral_bonus_action
from app.content.capability_compiler import compile_combatant
from app.content.monster_basic_candidates_2014 import _ARENA_NEUTRAL_TRAITS, basic_blockers_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014

_ATTACK_FIELDS = (
    "conditional_damage", "conditional_attack_advantage", "on_hit_damage",
    "on_hit_save_effect", "on_hit_contested_movement", "ongoing_damage_effect",
    "control_effect", "resource_id", "breakable_restraint", "charge_profile",
    "forbid_target_grappled_by_self", "grapple_target_policy",
)


def _unsupported_traits(monsters):
    return Counter(
        trait for monster in monsters for trait in monster.trait_names
        if trait not in _ARENA_NEUTRAL_TRAITS and not is_arena_neutral_bonus_action(trait)
    )


def _attack_shapes(monsters):
    counts = Counter()
    names = defaultdict(set)
    for monster in monsters:
        for attack in monster.attacks:
            for field in _ATTACK_FIELDS:
                value = getattr(attack, field)
                active = value not in (None, False, [], {}, "normal")
                if active:
                    counts[field] += 1
                    names[field].add(monster.name)
    return counts, names


def _single_blocker_families(monsters):
    names = defaultdict(list)
    for monster in monsters:
        blockers = basic_blockers_2014(monster)
        if len(blockers) == 1:
            names[blockers[0]].append(monster.name)
    return names


def _trait_only_details(monsters):
    rows = []
    for monster in monsters:
        if basic_blockers_2014(monster) != ("source:trait",):
            continue
        unsupported = [
            trait for trait in monster.trait_names
            if trait not in _ARENA_NEUTRAL_TRAITS and not is_arena_neutral_bonus_action(trait)
        ]
        rows.append((monster.name, unsupported))
    return rows


def main() -> None:
    monsters = load_monster_source_2014()
    ready = [monster for monster in monsters if not basic_blockers_2014(monster)]
    compiled = [compile_combatant(adapt_basic_monster_2014(monster)) for monster in ready]
    counts = Counter(blocker for monster in monsters for blocker in basic_blockers_2014(monster))
    print(f"2014 basic candidates: {len(ready)}/{len(monsters)}")
    print(f"2014 basic candidates compiled: {len(compiled)}/{len(ready)}")
    print("Candidate names:")
    print(", ".join(monster.name for monster in ready))
    print("Blockers:")
    for blocker, count in counts.most_common():
        print(f"  {blocker}: {count}")
    print("Single-blocker unlocks:")
    for blocker, names in sorted(_single_blocker_families(monsters).items(), key=lambda item: (-len(item[1]), item[0])):
        print(f"  {len(names):3}  {blocker}: {' | '.join(names)}")
    print("Trait-only details:")
    for name, traits in _trait_only_details(monsters):
        print(f"  {name}: {' | '.join(traits)}")
    attack_counts, attack_names = _attack_shapes(monsters)
    print("Complex attack shapes:")
    for field, count in attack_counts.most_common():
        print(f"  {count:3}  {field}: {' | '.join(sorted(attack_names[field]))}")
    print("Unsupported traits:")
    for trait, count in _unsupported_traits(monsters).most_common():
        print(f"  {count:3}  {trait}")
    if len(monsters) != 327:
        raise RuntimeError(f"Expected 327 source monsters, found {len(monsters)}")
    if len(ready) <= 4:
        raise RuntimeError("Bulk classifier did not improve on the four-monster MVP lane.")
    if len(compiled) != len(ready):
        raise RuntimeError("Not every admitted 2014 basic candidate compiled through the universal engine.")


if __name__ == "__main__":
    main()
