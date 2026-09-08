from __future__ import annotations

import re
from collections import defaultdict

from app.content.blocker_yield import build_blocker_signatures, single_family_yields
from app.content.monster_catalog import build_monster_catalog, load_monster_rows
from app.content.monster_source_classifier import _ALLOWED_TRAITS, source_blockers
from app.content.monster_trait_source_audit import parse_trait_names
from app.domain.catalog import CoverageStatus

_SIGNATURE_LIMIT = 25
_NOISE_BLOCKERS = frozenset({"monster-combat-mechanics-not-compiled"})
_CONTROL_EFFECT = re.compile(
    r"\b(blinded|charmed|deafened|frightened|grappled|incapacitated|paralyzed|petrified|poisoned|prone|restrained|stunned|unconscious|push(?:es|ed)?|pull(?:s|ed)?|swallow(?:s|ed)?)\b",
    re.I,
)


def _unsupported_traits(row: dict[str, object]) -> tuple[str, ...]:
    traits = parse_trait_names(row.get("traits", ""))
    return tuple(sorted(trait for trait in traits if trait not in _ALLOWED_TRAITS))


def _trait_heading_yields(rows_by_name: dict[str, dict[str, object]], names: list[str]) -> dict[str, list[str]]:
    yields: dict[str, list[str]] = defaultdict(list)
    for name in names:
        unsupported = _unsupported_traits(rows_by_name[name])
        if not unsupported:
            continue
        for trait in unsupported:
            yields[trait].append(name)
    return {
        trait: sorted(monsters)
        for trait, monsters in sorted(yields.items(), key=lambda item: (-len(item[1]), item[0]))
    }


def _single_trait_heading_yields(
    rows_by_name: dict[str, dict[str, object]], names: list[str]
) -> dict[str, list[str]]:
    yields: dict[str, list[str]] = defaultdict(list)
    for name in names:
        unsupported = _unsupported_traits(rows_by_name[name])
        if len(unsupported) == 1:
            yields[unsupported[0]].append(name)
    return {
        trait: sorted(monsters)
        for trait, monsters in sorted(yields.items(), key=lambda item: (-len(item[1]), item[0]))
    }


def _normalize_control_effect(value: str) -> str:
    normalized = value.lower()
    if normalized.startswith("push"):
        return "forced-push"
    if normalized.startswith("pull"):
        return "forced-pull"
    if normalized.startswith("swallow"):
        return "swallow"
    return normalized


def _control_effects(row: dict[str, object]) -> tuple[str, ...]:
    actions = str(row.get("actions", ""))
    effects = {_normalize_control_effect(match.group(1)) for match in _CONTROL_EFFECT.finditer(actions)}
    return tuple(sorted(effects))


def _control_effect_yields(
    rows_by_name: dict[str, dict[str, object]], names: list[str]
) -> dict[str, list[str]]:
    yields: dict[str, list[str]] = defaultdict(list)
    for name in names:
        for effect in _control_effects(rows_by_name[name]):
            yields[effect].append(name)
    return {
        effect: sorted(monsters)
        for effect, monsters in sorted(yields.items(), key=lambda item: (-len(item[1]), item[0]))
    }


def _control_signatures(
    rows_by_name: dict[str, dict[str, object]], names: list[str]
) -> dict[tuple[str, ...], list[str]]:
    grouped: dict[tuple[str, ...], list[str]] = defaultdict(list)
    for name in names:
        effects = _control_effects(rows_by_name[name])
        if effects:
            grouped[effects].append(name)
    return {
        signature: sorted(monsters)
        for signature, monsters in sorted(grouped.items(), key=lambda item: (-len(item[1]), item[0]))
    }


def _family_incidence(blockers_by_name: dict[str, list[str]]) -> dict[str, list[str]]:
    incidence: dict[str, list[str]] = defaultdict(list)
    for name, blockers in blockers_by_name.items():
        for blocker in sorted(set(blockers) - _NOISE_BLOCKERS):
            incidence[blocker].append(name)
    return {
        blocker: sorted(names)
        for blocker, names in sorted(incidence.items(), key=lambda item: (-len(item[1]), item[0]))
    }


def main() -> None:
    rows = load_monster_rows()
    rows_by_name = {str(row["name"]): row for row in rows}
    monster_names = set(rows_by_name)
    ready_names = {
        card.name
        for card in build_monster_catalog()
        if card.coverage_status is CoverageStatus.RAW_READY
    }
    blockers_by_name: dict[str, list[str]] = {}
    for row in rows:
        name = str(row["name"])
        if name in ready_names:
            continue
        blockers = source_blockers(row, monster_names)
        blockers_by_name[name] = blockers or ["unclassified-source-audit-gap"]

    signatures = build_blocker_signatures(blockers_by_name)
    singles = single_family_yields(signatures)
    trait_only = singles.get("trait", [])
    control_only = singles.get("condition-or-control", [])
    all_trait = [name for name, blockers in blockers_by_name.items() if "trait" in blockers]
    all_control = [name for name, blockers in blockers_by_name.items() if "condition-or-control" in blockers]
    print(
        "CAPABILITY_YIELD_BASELINE"
        f"\tready={len(ready_names)}\tblocked={len(blockers_by_name)}\tsignatures={len(signatures)}"
    )
    for blocker, names in _family_incidence(blockers_by_name).items():
        print(f"CAPABILITY_FAMILY_INCIDENCE\t{blocker}\t{len(names)}\t" + " | ".join(names))
    for blocker, names in sorted(singles.items(), key=lambda item: (-len(item[1]), item[0])):
        print(f"CAPABILITY_SINGLE_FAMILY\t{blocker}\t{len(names)}\t" + " | ".join(names))
    for effect, names in _control_effect_yields(rows_by_name, all_control).items():
        print(f"CAPABILITY_CONTROL_INCIDENCE\t{effect}\t{len(names)}\t" + " | ".join(names))
    for trait, names in _trait_heading_yields(rows_by_name, all_trait).items():
        print(f"CAPABILITY_TRAIT_INCIDENCE\t{trait}\t{len(names)}\t" + " | ".join(names))
    for signature, names in _control_signatures(rows_by_name, control_only).items():
        print(f"CAPABILITY_CONTROL_SIGNATURE\t{'+'.join(signature)}\t{len(names)}\t" + " | ".join(names))
    for effect, names in _control_effect_yields(rows_by_name, control_only).items():
        print(f"CAPABILITY_CONTROL_EFFECT\t{effect}\t{len(names)}\t" + " | ".join(names))
    for trait, names in _single_trait_heading_yields(rows_by_name, trait_only).items():
        print(f"CAPABILITY_TRAIT_SINGLE_HEADING\t{trait}\t{len(names)}\t" + " | ".join(names))
    for trait, names in _trait_heading_yields(rows_by_name, trait_only).items():
        print(f"CAPABILITY_TRAIT_HEADING\t{trait}\t{len(names)}\t" + " | ".join(names))
    for index, (signature, names) in enumerate(signatures.items()):
        if index >= _SIGNATURE_LIMIT:
            break
        label = "+".join(signature) if signature else "none"
        print(f"CAPABILITY_SIGNATURE\t{len(names)}\t{label}\t" + " | ".join(names))


if __name__ == "__main__":
    main()
