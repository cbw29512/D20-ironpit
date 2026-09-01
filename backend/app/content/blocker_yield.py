from __future__ import annotations

from collections import defaultdict

BlockerSignature = tuple[str, ...]


def build_blocker_signatures(blockers_by_name: dict[str, list[str]]) -> dict[BlockerSignature, list[str]]:
    """Group combatants by their unique, normalized blocker-family set."""
    grouped: dict[BlockerSignature, list[str]] = defaultdict(list)
    for name, blockers in blockers_by_name.items():
        signature = tuple(sorted(set(blockers)))
        grouped[signature].append(name)
    return {
        signature: sorted(names)
        for signature, names in sorted(
            grouped.items(),
            key=lambda item: (-len(item[1]), item[0]),
        )
    }


def single_family_yields(signatures: dict[BlockerSignature, list[str]]) -> dict[str, list[str]]:
    """Return monsters whose analyzer has exactly one blocker family remaining."""
    return {
        signature[0]: names
        for signature, names in signatures.items()
        if len(signature) == 1
    }


def removal_yields(signatures: dict[BlockerSignature, list[str]]) -> dict[str, list[str]]:
    """Estimate immediate candidates if one blocker family disappeared and no others remained."""
    yields: dict[str, list[str]] = defaultdict(list)
    for signature, names in signatures.items():
        if len(signature) == 1:
            yields[signature[0]].extend(names)
    return {
        blocker: sorted(names)
        for blocker, names in sorted(yields.items(), key=lambda item: (-len(item[1]), item[0]))
    }
