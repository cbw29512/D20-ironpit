from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import logging
import re

from app.content.monster_basic_candidates_2014 import basic_blockers_2014, unsupported_traits_2014
from app.content.monster_catalog import build_monster_catalog
from app.content.monster_roster_2014 import build_basic_2014_monsters
from app.content.monster_source_2014 import SourceMonster2014, load_monster_source_2014
from app.domain.catalog import CoverageStatus, MonsterCatalogCard

logger = logging.getLogger(__name__)
_REPORT_LIMIT = 60


@dataclass(frozen=True)
class PairedMonsterStatus:
    key: str
    name_2014: str
    name_2024: str
    ready_2014: bool
    ready_2024: bool
    blockers_2014: tuple[str, ...]
    blockers_2024: tuple[str, ...]
    unsupported_traits_2014: tuple[str, ...]


def _pair_key(name: str) -> str:
    try:
        key = re.sub(r"[^a-z0-9]+", "", name.casefold())
        if not key:
            raise ValueError(f"Monster name {name!r} has no usable pairing key.")
        return key
    except Exception:
        logger.exception("Failed to normalize monster name %r for edition pairing.", name)
        raise


def _unique_map(items, name_getter, label: str):
    try:
        result = {}
        for item in items:
            name = name_getter(item)
            key = _pair_key(name)
            if key in result:
                raise ValueError(f"{label} pairing key collision for {name!r}.")
            result[key] = item
        return result
    except Exception:
        logger.exception("Failed to build unique %s monster pairing map.", label)
        raise


def _paired_statuses() -> tuple[list[PairedMonsterStatus], list[str], list[str]]:
    try:
        source_2014 = load_monster_source_2014()
        cards_2024 = build_monster_catalog()
        if len(source_2014) != 327 or len(cards_2024) != 330:
            raise ValueError("Paired report requires the canonical 327/330 source corpora.")
        by_2014 = _unique_map(source_2014, lambda item: item.name, "2014")
        by_2024 = _unique_map(cards_2024, lambda item: item.name, "2024")
        ready_2014 = {item.name for item in build_basic_2014_monsters()}
        statuses: list[PairedMonsterStatus] = []
        for key in sorted(set(by_2014) & set(by_2024)):
            monster_2014: SourceMonster2014 = by_2014[key]
            card_2024: MonsterCatalogCard = by_2024[key]
            blockers_2014 = basic_blockers_2014(monster_2014)
            runtime_ready_2014 = monster_2014.name in ready_2014
            if runtime_ready_2014 != (not blockers_2014):
                raise ValueError(f"2014 readiness drift detected for {monster_2014.name!r}.")
            statuses.append(PairedMonsterStatus(
                key=key, name_2014=monster_2014.name, name_2024=card_2024.name,
                ready_2014=runtime_ready_2014,
                ready_2024=card_2024.coverage_status is CoverageStatus.RAW_READY,
                blockers_2014=blockers_2014, blockers_2024=tuple(card_2024.blockers),
                unsupported_traits_2014=unsupported_traits_2014(monster_2014),
            ))
        only_2014 = sorted(by_2014[key].name for key in set(by_2014) - set(by_2024))
        only_2024 = sorted(by_2024[key].name for key in set(by_2024) - set(by_2014))
        return statuses, only_2014, only_2024
    except Exception:
        logger.exception("Failed to build paired-edition monster status.")
        raise


def _blocker_text(blockers: tuple[str, ...]) -> str:
    return ",".join(blockers) if blockers else "none"


def _report_trait_yields(catchup_2014: list[PairedMonsterStatus]) -> None:
    try:
        single_trait = [item for item in catchup_2014 if item.blockers_2014 == ("source:trait",)]
        counts = Counter(trait for item in single_trait for trait in item.unsupported_traits_2014)
        for trait, count in sorted(counts.items(), key=lambda item: (-item[1], item[0])):
            names = sorted(item.name_2014 for item in single_trait if trait in item.unsupported_traits_2014)
            print(f"PAIRED_CATCHUP_TRAIT\t{trait}\t{count}\t" + " | ".join(names))
    except Exception:
        logger.exception("Failed to report 2014 catch-up trait yields.")
        raise


def main() -> None:
    try:
        statuses, only_2014, only_2024 = _paired_statuses()
        total_ready_2014 = len(build_basic_2014_monsters())
        total_ready_2024 = sum(card.coverage_status is CoverageStatus.RAW_READY for card in build_monster_catalog())
        both_ready = [item for item in statuses if item.ready_2014 and item.ready_2024]
        catchup_2014 = [item for item in statuses if item.ready_2024 and not item.ready_2014]
        ahead_2014 = [item for item in statuses if item.ready_2014 and not item.ready_2024]
        both_blocked = [item for item in statuses if not item.ready_2014 and not item.ready_2024]
        print(
            "PAIRED_BASELINE"
            f"\t2014_ready={total_ready_2014}/327\t2024_ready={total_ready_2024}/330"
            f"\tshared={len(statuses)}\tonly_2014={len(only_2014)}\tonly_2024={len(only_2024)}"
        )
        print(
            "PAIRED_STATUS"
            f"\tboth_ready={len(both_ready)}\tcatchup_2014={len(catchup_2014)}"
            f"\t2014_ahead={len(ahead_2014)}\tboth_blocked={len(both_blocked)}"
        )
        _report_trait_yields(catchup_2014)
        for item in sorted(catchup_2014, key=lambda row: (len(row.blockers_2014), row.blockers_2014, row.name_2014))[:_REPORT_LIMIT]:
            traits = ",".join(item.unsupported_traits_2014) or "none"
            print(f"PAIRED_CATCHUP_2014\t{item.name_2014}\t{_blocker_text(item.blockers_2014)}\ttraits={traits}")
        for item in sorted(ahead_2014, key=lambda row: (len(row.blockers_2024), row.blockers_2024, row.name_2024))[:_REPORT_LIMIT]:
            print(f"PAIRED_CHECK_2024\t{item.name_2024}\t{_blocker_text(item.blockers_2024)}")
        if only_2014:
            print("PAIRED_ONLY_2014\t" + " | ".join(only_2014))
        if only_2024:
            print("PAIRED_ONLY_2024\t" + " | ".join(only_2024))
        logger.info("Paired-edition report completed with %d shared monster identities.", len(statuses))
    except Exception:
        logger.exception("Paired-edition monster progress report failed.")
        raise


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
